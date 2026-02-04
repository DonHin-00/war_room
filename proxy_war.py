
import emulator
import proxy_units
import time
import sys

def run_proxy_war(duration=60):
    print("\033[95m[PROXY WAR] Initializing Virtual Sandbox...\033[0m")
    sandbox = emulator.Sandbox()

    red_proxy = proxy_units.ProxyRed(sandbox)
    blue_proxy = proxy_units.ProxyBlue(sandbox)

    start_time = time.time()
    battles = 0
    wins = 0

    print("\033[95m[PROXY WAR] Engaging in Shadow Conflict...\033[0m")
    try:
        while time.time() - start_time < duration:
            # 1. Red Acts (Detonates Malware in Sandbox)
            pid, name, behavior = red_proxy.act()

            # 2. Blue Reacts (Intervention)
            action, reward = blue_proxy.react(pid, name, behavior)

            battles += 1
            if reward > 0: wins += 1

            # Log
            outcome = "BLOCKED" if reward > 0 else "MISSED"
            print(f"  [Battle #{battles}] Threat: {name} ({behavior}) -> Blue Action: {action} -> Result: {outcome}")

            time.sleep(0.1) # Fast emulation

    except KeyboardInterrupt:
        pass

    print(f"\n\033[95m[PROXY WAR] Conflict Ends. {battles} battles, {wins} Blue victories.\033[0m")
    print("\033[90mExperience Replay DB updated for Main Agents.\033[0m")

if __name__ == "__main__":
    duration = 30
    if len(sys.argv) > 1:
        try: duration = int(sys.argv[1])
        except: pass
    run_proxy_war(duration)
