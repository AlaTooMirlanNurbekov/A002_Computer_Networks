"""
Task CN37 : Switch port security simulator

Description: simulates **port security** on a layer 2 switch.

Port security is used to protect access ports by:
- Limiting the number of MAC addresses per port
- Optionally allowing only specific (sticky/static) MAC addresses
- Taking action when a violation occurs

Supported security modes:
- restrict  → drop frames, log violation
- shutdown → disable the port entirely
- protect  → silently drop frames

You can:
- Configure port security on ports
- Set maximum allowed MAC addresses per port
- Enable sticky MAC learning
- Send frames and observe violations
- View port security status and violation counters

Concept:
Port security is commonly used on access ports to prevent:
- Unauthorized devices
- MAC flooding attacks
- Accidental loops caused by hubs/switches
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Set, Literal


ViolationMode = Literal["protect", "restrict", "shutdown"]

def is_valid_mac(mac: str) -> bool:
    parts = mac.split(":")
    if len(parts) != 6:
        return False
    try:
        return all(0 <= int(p, 16) <= 255 for p in parts)
    except ValueError:
        return False


def normalize_mac(mac: str) -> str:
    return ":".join(p.lower().zfill(2) for p in mac.split(":"))

@dataclass
class PortSecurityConfig:
    enabled: bool = False
    max_macs: int = 1
    violation_mode: ViolationMode = "shutdown"
    sticky_enabled: bool = False
    allowed_macs: Set[str] = field(default_factory=set)

    # runtime state
    learned_macs: Set[str] = field(default_factory=set)
    violations: int = 0
    shutdown: bool = False

class PortSecuritySwitch:
    def __init__(self, ports: int = 4):
        self.ports = ports
        self.port_security: Dict[int, PortSecurityConfig] = {
            p: PortSecurityConfig() for p in range(1, ports + 1)
        }

    def enable_port_security(
        self,
        port: int,
        max_macs: int = 1,
        violation_mode: ViolationMode = "shutdown",
        sticky: bool = False,
    ):
        self._check_port(port)
        cfg = self.port_security[port]
        cfg.enabled = True
        cfg.max_macs = max_macs
        cfg.violation_mode = violation_mode
        cfg.sticky_enabled = sticky
        print(
            f"[Config] Port {port}: port-security enabled "
            f"(max={max_macs}, mode={violation_mode}, sticky={sticky})"
        )

    def disable_port_security(self, port: int):
        self._check_port(port)
        self.port_security[port] = PortSecurityConfig()
        print(f"[Config] Port {port}: port-security disabled")

    def add_static_mac(self, port: int, mac: str):
        self._check_port(port)
        if not is_valid_mac(mac):
            raise ValueError("Invalid MAC address.")
        mac_n = normalize_mac(mac)
        cfg = self.port_security[port]
        cfg.allowed_macs.add(mac_n)
        print(f"[Config] Port {port}: added static MAC {mac_n}")

    def receive_frame(self, port: int, src_mac: str):
        self._check_port(port)
        cfg = self.port_security[port]
        if not is_valid_mac(src_mac):
            print("Invalid source MAC.\n")
            return

        mac = normalize_mac(src_mac)
        print("\nFrame received")
        print("--------------")
        print(f"Ingress port : {port}")
        print(f"Source MAC   : {mac}")

        if not cfg.enabled:
            print("Port security disabled → frame accepted ✔\n")
            return

        if cfg.shutdown:
            print("PORT IS SHUTDOWN due to previous violation ❌\n")
            return

        # check static allowed MACs
        if cfg.allowed_macs and mac not in cfg.allowed_macs:
            self._violation(port, mac, reason="MAC not in static allowed list")
            return

        # check MAC count
        if mac not in cfg.learned_macs:
            if len(cfg.learned_macs) >= cfg.max_macs:
                self._violation(port, mac, reason="maximum MAC limit exceeded")
                return

            # for MAC
            cfg.learned_macs.add(mac)
            if cfg.sticky_enabled:
                cfg.allowed_macs.add(mac)
                print(f"[Sticky] MAC {mac} learned and added to allowed list")
            else:
                print(f"[Learn] MAC {mac} learned on port {port}")

        print("Frame accepted ✔\n")

    def _violation(self, port: int, mac: str, reason: str):
        cfg = self.port_security[port]
        cfg.violations += 1

        print(f"PORT SECURITY VIOLATION on port {port}")
        print(f"Reason      : {reason}")
        print(f"Offending MAC: {mac}")

        if cfg.violation_mode == "protect":
            print("Action      : PROTECT → frame dropped silently\n")
        elif cfg.violation_mode == "restrict":
            print("Action      : RESTRICT → frame dropped, violation logged\n")
        elif cfg.violation_mode == "shutdown":
            cfg.shutdown = True
            print("Action      : SHUTDOWN → port disabled ❌\n")

    def show_status(self):
        print("\nPort Security Status")
        print("--------------------")
        print(
            f"{'Port':<6} {'Enabled':<8} {'Max':<4} "
            f"{'Mode':<10} {'Learned MACs':<15} Violations State"
        )
        print("-" * 80)
        for p in range(1, self.ports + 1):
            cfg = self.port_security[p]
            state = "SHUTDOWN" if cfg.shutdown else "UP"
            print(
                f"{p:<6} {str(cfg.enabled):<8} {cfg.max_macs:<4} "
                f"{cfg.violation_mode:<10} {len(cfg.learned_macs):<15} "
                f"{cfg.violations:<10} {state}"
            )
        print()

# validation
    def _check_port(self, port: int):
        if not (1 <= port <= self.ports):
            raise ValueError(f"Port must be between 1 and {self.ports}")

def print_menu():
    print("=== Task CN37 : Switch Port Security Simulator ===")
    print("1) Show port security status")
    print("2) Enable port security on port")
    print("3) Disable port security on port")
    print("4) Add static MAC to port")
    print("5) Send frame into port")
    print("6) Exit")

def main():
    sw = PortSecuritySwitch(ports=4)
    # config
    sw.enable_port_security(port=1, max_macs=1, violation_mode="shutdown", sticky=True)
    while True:
        print_menu()
        choice = input("Choose option (1–6): ").strip()

        if choice == "1":
            sw.show_status()
        elif choice == "2":
            p = int(input("Port number: ").strip())
            max_macs = int(input("Max MACs: ").strip())
            mode = input("Violation mode (protect/restrict/shutdown): ").strip()
            sticky = input("Sticky MAC? (y/n): ").strip().lower() in ("y", "yes")
            sw.enable_port_security(p, max_macs, mode, sticky)
            print()
        elif choice == "3":
            p = int(input("Port number: ").strip())
            sw.disable_port_security(p)
            print()
        elif choice == "4":
            p = int(input("Port number: ").strip())
            mac = input("MAC address: ").strip().lower()
            sw.add_static_mac(p, mac)
            print()
        elif choice == "5":
            p = int(input("Ingress port: ").strip())
            mac = input("Source MAC: ").strip().lower()
            sw.receive_frame(p, mac)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")
# program entry point
if __name__ == "__main__":
    main()
