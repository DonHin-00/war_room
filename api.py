import os
import subprocess
import json
import logging
import time
import uuid
import signal
import re
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CyberMuzzleAPI")

# Global process store for async tasks (captures)
ACTIVE_PROCESSES = {}

# --- UTILITIES ---

def run_command(command_args, timeout=30):
    """Executes a system command and returns output/error."""
    try:
        logger.info(f"Executing: {' '.join(command_args)}")
        result = subprocess.run(
            command_args,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False  # Don't raise immediately, handle returncode
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip()
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Command not found: {command_args[0]}"
        }
    except Exception as e:
        logger.error(f"Execution error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def parse_nmcli(output):
    """Parses nmcli terse output into structured JSON."""
    networks = []
    # nmcli -t -f SSID,BSSID,SIGNAL,SECURITY dev wifi
    # Format: SSID:BSSID:SIGNAL:SECURITY
    # Handle escaped colons if possible, but basic split is often sufficient for simple SSIDs
    try:
        lines = output.strip().split('\n')
        for line in lines:
            if not line: continue
            # Basic parsing strategy: BSSID is 17 chars (XX:XX:XX:XX:XX:XX)
            # Signal is integer
            # Security is string
            # We can use regex to find the BSSID pattern

            # Regex for BSSID: ([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}
            match = re.search(r'((?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}):(\d+):(.*)$', line)
            if match:
                bssid = match.group(1)
                signal_str = match.group(2)
                security = match.group(3)
                # SSID is everything before the BSSID (minus the separator colon)
                # The BSSID is preceeded by a colon in the full string: SSID:BSSID...
                # So we find the index of BSSID
                bssid_idx = line.find(bssid)
                if bssid_idx > 0:
                    ssid = line[:bssid_idx-1]
                else:
                    ssid = ""

                networks.append({
                    "ssid": ssid,
                    "bssid": bssid,
                    "signal": int(signal_str),
                    "security": security
                })
            else:
                # Fallback simplistic split
                parts = line.split(':')
                if len(parts) >= 4:
                     networks.append({
                        "ssid": parts[0],
                        "bssid": ":".join(parts[1:7]) if len(parts[1])==2 else parts[1], # Handle if BSSID was split
                        "raw": line
                    })
    except Exception as e:
        logger.error(f"Parsing error: {e}")
    return networks

# --- ENDPOINTS ---

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "active", "version": "1.1.0", "mode": "LIVE_CAPABLE"})

@app.route('/api/sentinel/status', methods=['GET'])
def sentinel_status():
    """Reads the shared state from Blue Brain (Sentinel)."""
    state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "war_state.json")
    try:
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                data = json.load(f)
            return jsonify({"success": True, "data": data})
        else:
            return jsonify({"success": False, "error": "Sentinel state not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 1. WiFi Operations
@app.route('/api/wifi/scan', methods=['POST'])
def wifi_scan():
    """
    Real implementation using nmcli.
    """
    # nmcli -t (terse) -f (fields) ...
    # Note: escaped colons in SSID are annoying, but we try best effort parsing
    res = run_command(["nmcli", "-t", "-f", "SSID,BSSID,SIGNAL,SECURITY", "dev", "wifi"])

    data = []
    if res['success']:
        data = parse_nmcli(res['output'])
    else:
        # Fallback check
        res_iw = run_command(["iwlist", "scan"])
        if res_iw['success']:
            res['output'] += "\n" + res_iw['output'] # Append for debug
            # Parsing iwlist is complex, leaving raw for now but at least we tried

    return jsonify({
        "success": res['success'],
        "output": res['output'],
        "error": res['error'],
        "data": data
    })

@app.route('/api/wifi/capture', methods=['POST'])
def wifi_capture():
    """
    Starts a background capture process (airodump-ng).
    """
    data = request.json
    bssid = data.get('bssid')
    channel = data.get('channel')
    interface = data.get('interface', 'wlan0mon')

    if not bssid or not channel:
        return jsonify({"success": False, "error": "BSSID and Channel required"}), 400

    # Ensure tool exists
    check = run_command(["which", "airodump-ng"])
    if not check['success']:
         return jsonify({"success": False, "error": "airodump-ng not found on system."}), 500

    # Output prefix
    capture_id = str(uuid.uuid4())[:8]
    output_base = f"/tmp/capture_{capture_id}"

    cmd = [
        "airodump-ng",
        "-c", str(channel),
        "--bssid", bssid,
        "-w", output_base,
        "--output-format", "pcap",
        interface
    ]

    try:
        logger.info(f"Starting capture: {' '.join(cmd)}")
        # Start detached process
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid # Create new session group to allow clean kill
        )

        ACTIVE_PROCESSES[capture_id] = {
            "pid": proc.pid,
            "cmd": cmd,
            "start_time": time.time(),
            "bssid": bssid,
            "file_base": output_base
        }

        return jsonify({
            "success": True,
            "message": f"Capture started on {bssid}",
            "capture_id": capture_id,
            "pid": proc.pid
        })
    except Exception as e:
        logger.error(f"Capture start failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/wifi/stop_capture', methods=['POST'])
def stop_capture():
    data = request.json
    capture_id = data.get('capture_id')

    if capture_id not in ACTIVE_PROCESSES:
        return jsonify({"success": False, "error": "Capture ID not found"}), 404

    info = ACTIVE_PROCESSES[capture_id]
    pid = info['pid']

    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
        # Verify file existence
        pcap_file = info['file_base'] + "-01.cap"
        file_exists = os.path.exists(pcap_file)

        del ACTIVE_PROCESSES[capture_id]

        return jsonify({
            "success": True,
            "message": "Capture stopped",
            "file_saved": file_exists,
            "path": pcap_file if file_exists else None
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to stop process: {str(e)}"}), 500

@app.route('/api/wifi/deauth', methods=['POST'])
def wifi_deauth():
    data = request.json
    bssid = data.get('bssid')
    interface = data.get('interface', 'wlan0mon')

    # aireplay-ng --deauth 5 -a [bssid] [interface]
    # Real attack execution
    cmd = ["aireplay-ng", "--deauth", "5", "-a", bssid, interface]

    res = run_command(cmd)
    return jsonify(res)

# 2. Network Operations
@app.route('/api/network/scan', methods=['POST'])
def network_scan():
    target = request.json.get('target', 'localhost')

    # Use nmap with XML output but also try to get normal output for reading
    # We'll return the raw output for now as it contains the real data
    cmd = ["nmap", "-F", target]

    res = run_command(cmd)
    return jsonify(res)

# 3. Web Operations
@app.route('/api/web/scan', methods=['POST'])
def web_scan():
    url = request.json.get('url')
    if not url:
        return jsonify({"success": False, "error": "URL required"}), 400

    try:
        import requests
        # Real request
        resp = requests.get(url, timeout=5)

        # Security Header Analysis
        headers = resp.headers
        security_report = {
            "x-frame-options": headers.get("X-Frame-Options", "MISSING"),
            "x-xss-protection": headers.get("X-XSS-Protection", "MISSING"),
            "content-security-policy": headers.get("Content-Security-Policy", "MISSING"),
            "strict-transport-security": headers.get("Strict-Transport-Security", "MISSING")
        }

        return jsonify({
            "success": True,
            "headers": dict(headers),
            "status_code": resp.status_code,
            "security_report": security_report
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/processes', methods=['GET'])
def list_processes():
    """Debug endpoint to see active background tasks."""
    return jsonify(ACTIVE_PROCESSES)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
