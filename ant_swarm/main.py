import time
import json
import os
import logging
from ant_swarm.agents.blue_defender import BlueDefender
from ant_swarm.red.red_teamer import RedTeamer
from ant_swarm.core.hive import HiveState

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')

def main():
    print("Initializing Ant Swarm Hive Mind...")

    # Init Hive
    hive = HiveState()

    # Init Agents
    blue = BlueDefender()
    red = RedTeamer()

    print("Deploying Agents...")
    blue.start()
    red.start()

    state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hive_state.json")

    try:
        while True:
            time.sleep(1)
            state = hive.get_state()
            with open(state_file, 'w') as f:
                json.dump(state, f)
    except KeyboardInterrupt:
        print("Shutting down Hive...")
        blue.stop()
        red.stop()

if __name__ == "__main__":
    main()
