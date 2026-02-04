import red_brain
import time
import sys
import os
import json
import signal

# Ensure dummy files exist to simulate real I/O
if not os.path.exists(red_brain.Q_TABLE_FILE):
    with open(red_brain.Q_TABLE_FILE, 'w') as f:
        json.dump({}, f)
if not os.path.exists(red_brain.STATE_FILE):
    with open(red_brain.STATE_FILE, 'w') as f:
        json.dump({'blue_alert_level': 1}, f)

# Mock time.sleep to avoid waiting
red_brain.time.sleep = lambda x: None

# Wrap access_memory to count and stop
# Since we refactored access_memory out and use StateManager, we need to mock StateManager.get_war_state
# or just the get_war_state method of the instance.

class StopBenchmark(BaseException):
    pass

count = 0
MAX_ITERS = 1000

# We need to monkey patch StateManager.get_war_state because that's what's called in the loop
original_get_war_state = red_brain.StateManager.get_war_state

def mock_get_war_state(self):
    global count
    count += 1
    if count > MAX_ITERS:
        raise StopBenchmark
    return original_get_war_state(self)

red_brain.StateManager.get_war_state = mock_get_war_state

print(f"Running benchmark for {MAX_ITERS} iterations...")
start_time = time.time()
try:
    if hasattr(red_brain, 'RedTeamer'):
        bot = red_brain.RedTeamer()
        bot.engage()
    else:
        red_brain.engage_offense()
except StopBenchmark:
    pass
except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"Error: {e}")

end_time = time.time()
duration = end_time - start_time
print(f"Time taken for {MAX_ITERS} iterations: {duration:.4f} seconds")
print(f"Average time per iteration: {duration/MAX_ITERS:.4f} seconds")
