import red_brain
import time
import sys
import os
import json
import signal
import config
import utils

# Ensure dummy files exist to simulate real I/O
if not os.path.exists(config.PATHS["Q_TABLE_RED"]):
    utils.safe_json_write(config.PATHS["Q_TABLE_RED"], {})
if not os.path.exists(config.PATHS["WAR_STATE"]):
    utils.safe_json_write(config.PATHS["WAR_STATE"], {'blue_alert_level': 1})

# Mock time.sleep to avoid waiting
red_brain.time.sleep = lambda x: None

class StopBenchmark(BaseException):
    pass

count = 0
MAX_ITERS = 1000

# Monkey patch StateManager.get_war_state on the instance or class in utils
original_get_war_state = utils.StateManager.get_war_state

def mock_get_war_state(self):
    global count
    count += 1
    if count > MAX_ITERS:
        raise StopBenchmark
    return original_get_war_state(self)

utils.StateManager.get_war_state = mock_get_war_state

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
