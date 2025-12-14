"""
Task CN40 : DHCP snooping simulator

Description: **DHCP Snooping**, a Layer-2 security feature used on switches.

DHCP Snooping:
- Protects networks from **rogue DHCP servers**
- Differentiates between:
    * TRUSTED ports   → allowed to send DHCP server messages
    * UNTRUSTED ports → only allowed to send client messages
- Builds a **DHCP Snooping Binding Table** (IP ↔ MAC ↔ VLAN ↔ Port)

It can:
- Configure switch ports as trusted or untrusted
- Simulate DHCP messages (DISCOVER, OFFER, REQUEST, ACK)
- See which packets are allowed or dropped
- Inspect the DHCP snooping binding table

Concept: Without DHCP Snooping, a rogue DHCP server can:
- Give wrong gateway/DNS
- Perform man-in-the-middle attacks

DHCP Snooping ensures that **only legitimate servers** can reply to clients.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Literal


DhcpMessageType = Literal["DISCOVER", "OFFER", "REQUEST", "ACK"]

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
class Port:
    trusted: bool = False

@dataclass
class DhcpBinding:
    mac: str
    ip: str
    vlan: int
    port: int

class DhcpSnoopingSwitch:
    def __init__(self, ports: int = 4):
        self.ports: Dict[int, Port] = {p: Port(False) for p in range(1, ports + 1)}
        self.bindings: Dict[str, DhcpBinding] = {}  # MAC → binding

    def set_trusted(self, port: int, trusted: bool):
        self._check_port(port)
        self.ports[port].trusted = trusted
        state = "TRUSTED" if trusted else "UNTRUSTED"
        print(f"[Config] Port {port} set to {state}")

    def process_dhcp(
        self,
        ingress_port: int,
        msg_type: DhcpMessageType,
        src_mac: str,
        offered_ip: str | None = None,
        vlan: int = 1,
    ):
        self._check_port(ingress_port)

        if not is_valid_mac(src_mac):
            print("Invalid MAC address.\n")
            return

        mac = normalize_mac(src_mac)
        port_cfg = self.ports[ingress_port]

        print("\nDHCP packet received")
        print("--------------------")
        print(f"Ingress port : {ingress_port}")
        print(f"Message type : {msg_type}")
        print(f"Source MAC   : {mac}")
        print(f"VLAN         : {vlan}")

        # client messages are always allowed
        if msg_type in ("DISCOVER", "REQUEST"):
            print("Client DHCP message → allowed ✔\n")
            return

        # Server messages must come from TRUSTED ports
        if msg_type in ("OFFER", "ACK"):
            if not port_cfg.trusted:
                print("SECURITY VIOLATION ❌")
                print("Rogue DHCP server detected!")
                print("Action: DHCP packet DROPPED\n")
                return

            print("DHCP server message from TRUSTED port ✔")

            # Learn binding on ACK
            if msg_type == "ACK" and offered_ip:
                self.bindings[mac] = DhcpBinding(
                    mac=mac,
                    ip=offered_ip,
                    vlan=vlan,
                    port=ingress_port,
                )
                print(f"Binding learned: {mac} → {offered_ip}")

            print()

    def show_bindings(self):
        if not self.bindings:
            print("\nDHCP Snooping Binding Table is empty.\n")
            return

        print("\nDHCP Snooping Binding Table")
        print("---------------------------")
        print(f"{'MAC address':<20} {'IP address':<16} {'VLAN':<6} Port")
        print("-" * 55)
        for b in self.bindings.values():
            print(f"{b.mac:<20} {b.ip:<16} {b.vlan:<6} {b.port}")
        print()

    def show_ports(self):
        print("\nPort Trust Status")
        print("-----------------")
        for p, cfg in self.ports.items():
            state = "TRUSTED" if cfg.trusted else "UNTRUSTED"
            print(f"Port {p}: {state}")
        print()

    def _check_port(self, port: int):
        if port not in self.ports:
            raise ValueError("Invalid port number.")


def print_menu():
    print("=== Task CN40 : DHCP Snooping Simulator ===")
    print("1) Show port trust status")
    print("2) Set port TRUSTED")
    print("3) Set port UNTRUSTED")
    print("4) Send DHCP packet")
    print("5) Show DHCP snooping bindings")
    print("6) Exit")


def main():
    sw = DhcpSnoopingSwitch(ports=4)
    # Typical real-world config: port 1 → uplink to real DHCP server (trusted)
    sw.set_trusted(1, True)

    while True:
        print_menu()
        choice = input("Choose option (1–6): ").strip()

        if choice == "1":
            sw.show_ports()
        elif choice == "2":
            p = int(input("Port number: ").strip())
            sw.set_trusted(p, True)
            print()
        elif choice == "3":
            p = int(input("Port number: ").strip())
            sw.set_trusted(p, False)
            print()
        elif choice == "4":
            p = int(input("Ingress port: ").strip())
            msg = input("Message (DISCOVER/OFFER/REQUEST/ACK): ").strip().upper()
            mac = input("Source MAC: ").strip().lower()
            ip = None
            if msg == "ACK":
                ip = input("Assigned IP (for ACK): ").strip()
            sw.process_dhcp(p, msg, mac, ip)
        elif choice == "5":
            sw.show_bindings()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")

# program entry point
if __name__ == "__main__":
    main()
