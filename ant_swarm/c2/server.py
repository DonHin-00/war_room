from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import time
from queue import Queue
from rich.console import Console
from rich.table import Table

console = Console()

class TaskDispatcher:
    def __init__(self):
        self.job_queue = Queue()
        self.results = {}
        self.total_tasks = 0
        self._init_map_reduce()

    def _init_map_reduce(self):
        """
        Splits a massive scan into chunks.
        """
        target = "127.0.0.1" # The Hardened Target
        console.print(f"[OVERMIND] 🧠 Initializing MapReduce for Target: {target}")

        # Split 100 ports into 10 chunks of 10
        for i in range(0, 100, 10):
            task = {
                "id": f"TASK_{i//10}",
                "type": "SCAN",
                "target": target,
                "port_range": f"{i}-{i+10}"
            }
            self.job_queue.put(task)
            self.total_tasks += 1

    def get_next_task(self):
        if not self.job_queue.empty():
            return self.job_queue.get()
        return {"type": "SLEEP"}

    def submit_result(self, drone_id, result):
        self.results[drone_id] = result
        # Check completion
        if len(self.results) >= self.total_tasks:
            self._finalize_job()

    def _finalize_job(self):
        console.print("\n[OVERMIND] 🏁 JOB COMPLETE. Aggregating Swarm Data...")
        table = Table(title="Global Target Map")
        table.add_column("Drone")
        table.add_column("Findings")

        for drone, res in self.results.items():
            table.add_row(drone, str(res))

        console.print(table)

class C2Handler(BaseHTTPRequestHandler):
    dispatcher = TaskDispatcher() # Shared state

    def do_POST(self):
        if self.path == '/beacon':
            self._handle_beacon()
        elif self.path == '/loot':
            self._handle_loot()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/orders':
            self._handle_orders()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_beacon(self):
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        # console.print(f"[OVERMIND] 📡 Beacon from {data['id']}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ACK')

    def _handle_loot(self):
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        console.print(f"[OVERMIND] 💰 Loot/Result from {data['id']}")
        self.dispatcher.submit_result(data['id'], data['content'])
        self.send_response(200)
        self.end_headers()

    def _handle_orders(self):
        task = self.dispatcher.get_next_task()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(task).encode())

    def log_message(self, format, *args):
        return # Silence standard HTTP logs

class OvermindServer:
    def __init__(self, port=8080):
        self.port = port
        self.server = HTTPServer(('0.0.0.0', port), C2Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        console.print(f"[OVERMIND] 👁️ C2 Server Online on port {self.port}")
        self.thread.start()

    def stop(self):
        self.server.shutdown()
