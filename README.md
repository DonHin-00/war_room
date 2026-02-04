# AI Cyber War Emulation

This repository contains a self-learning adversarial emulation environment. It is NOT a simulation; it performs live file system operations, generates persistent audit logs, and adapts strategies in real-time.

**Components:**
- **Blue Brain (Defender):** Implements NIST SP 800-61 incident response, active defense (honeypots), and ransomware recovery.
- **Red Brain (Attacker):** Implements MITRE ATT&CK tactics, evolving malware payloads, and anti-forensics.
- **Battlefield:** A live directory where actual file operations (encryption, obfuscation, deletion) occur.

**Philosophy:**
- **Realistic Emulation:** Agents perform real I/O operations with locking, checksums, and resource limits.
- **Live Fire:** Attacks result in actual data transformation (e.g., byte-reversal encryption).
- **Chaos Engineering:** The system is resilient to external corruption and state tampering.
