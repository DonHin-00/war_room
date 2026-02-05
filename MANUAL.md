# Ant Swarm Framework v1.0

The **Ant Swarm** is a sophisticated Multi-Agent Framework designed for **Red Team Intelligence**, **Secure Code Generation**, and **Cyber War Simulation**.

## Architecture

### 1. The Hive Mind (`ant_swarm.core`)
The central nervous system.
- **HiveState**: Tracks global "Mood" (Neutral, Critical, War) and "DEFCON" levels (5-1).
- **SignalBus**: Event-driven communication between agents.
- **OODA Loop**: The decision engine (Observe-Orient-Decide-Act) that selects `TacticalDoctrines`.

### 2. The Red Team (`ant_swarm.red`)
Offensive capabilities.
- **Strategist**: Orchestrates campaigns.
- **AutoRecon**: Mass-scale scanning (Filesystem & Network).
- **PivotTunnel**: Lateral movement via SSH/Socket relays.
- **LootBag**: Stealthy data exfiltration (Steganography) and infiltration (Smuggling).
- **GhostProtocol**: Evasion (Process Cloaking, Timestomping).

### 3. The C2 Infrastructure (`ant_swarm.c2`)
Distributed operations.
- **Overmind**: HTTP Command & Control server. Uses MapReduce to split tasks.
- **Drone**: Deployable agents that cloak and execute orders.

### 4. Code Intelligence (`ant_swarm.core.micro_lm`)
- **MicroLM**: A "Secure SmallLM" engine.
- **GeneticOptimizer**: Breeds code variants to find optimal solutions.
- **Toolbox**: Real static analysis (AST, Regex, Fuzzing) to harden code.

## Usage

Use the unified CLI:

```bash
python3 ant_swarm_cli.py [COMMAND]
```

### Commands

- `server`: Start the C2 Overmind.
  - `python3 ant_swarm_cli.py server --port 8080`
- `drone`: Deploy a Drone agent.
  - `python3 ant_swarm_cli.py drone --c2 http://localhost:8080`
- `attack`: Launch an interactive attack against a target IP.
  - `python3 ant_swarm_cli.py attack --target 192.168.1.50`
- `campaign`: Run the automated Strategist logic (Simulated Campaign).
- `demo`: Run a full "Hive Net" simulation with 5 drones.

## The Void (Deception Layer)

The system includes a **Mirage Layer** (`ant_swarm.support.mirage`) for defense.
- **Honeypots**: Rigs `.env` and `config.json` with fake keys.
- **Tarpits**: `PhantomShell` simulates a fake OS to waste attacker time.
- **Obfuscation**: `FractalObfuscator` generates multi-layer payloads.

## Disclaimer

This tool is for **Educational and Simulation Purposes Only**. Features like "Ghost Protocol" and "Exploit Generation" are implemented for Red Team training scenarios.
