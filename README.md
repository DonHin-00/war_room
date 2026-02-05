# Apex Assurance Platform v1.0

The **Apex Assurance Platform** is an enterprise-grade Multi-Agent Framework designed for **Security Validation**, **Adversary Emulation**, and **Resilience Testing**.

## Architecture

### 1. The Core System (`apex_framework.core`)
The central nervous system.
- **HiveState**: Tracks global "Operational Status" and "Alert Levels".
- **SignalBus**: Event-driven communication between agents.
- **OODA Loop**: The decision engine (Observe-Orient-Decide-Act) that selects `TacticalDoctrines`.

### 2. Offensive Operations (`apex_framework.ops`)
Capabilities for security assessment.
- **CampaignOrchestrator**: Manages assessment campaigns.
- **AssetDiscovery**: Mass-scale asset identification (Filesystem & Network).
- **PivotTunnel**: Lateral movement via SSH/Socket relays.
- **DataTransport**: Secure artifact collection and exfiltration.
- **LowObservableMode**: Stealth techniques (Process Integrity, Timestomping).
- **PrivacyManager**: Userland masking (LD_PRELOAD) for assessment agents.
- **ServiceDaemon**: Persistence mechanisms for long-term audits.

### 3. Orchestration (`apex_framework.orchestration`)
Distributed management.
- **CentralController**: HTTP C2 server for managing agents.
- **RemoteAgent**: Deployable assessment nodes.
- **DynamicLoader**: Diskless capability streaming (RAM-only execution).

### 4. Code Intelligence (`apex_framework.core.micro_lm`)
- **MicroLM**: Genetic coding engine for automated payload generation.
- **Toolbox**: Static analysis suite (AST, Regex, Fuzzing) for code hardening.

## Usage

Use the unified CLI:

```bash
python3 apex_cli.py [COMMAND]
```

### Commands

- `controller`: Start the Central Controller.
  - `python3 apex_cli.py controller --port 8080`
- `agent`: Deploy a Remote Agent.
  - `python3 apex_cli.py agent --c2 http://localhost:8080`
- `audit`: Launch an interactive security audit against a target IP.
  - `python3 apex_cli.py audit --target 192.168.1.50`
- `campaign`: Run the automated Orchestrator logic.
- `demo`: Run a full platform simulation.

## Deception Technology (`apex_framework.support.mirage`)

The platform includes a **Mirage Layer** for defensive validation.
- **Decoys**: Deploys fake credentials (`.env`) to detect breach attempts.
- **Tarpits**: `PhantomShell` simulates a vulnerable environment to analyze attacker behavior.

## Disclaimer

This platform is for **Authorized Security Assessments and Educational Use Only**. Unauthorized use against systems you do not own is illegal.
