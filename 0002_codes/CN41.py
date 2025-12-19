"""
Task CN41 : Dynamic ARP Inspection (DAI) simulator

Description: this task simulates **Dynamic ARP Inspection (DAI)**, a Layer-2 security feature.

DAI protects against **ARP spoofing / ARP poisoning** by validating ARP packets
against a trusted binding table (typically built by DHCP Snooping).

Core idea:
- Only ARP packets that match a known (IP ↔ MAC) binding are allowed
- Invalid ARP packets are dropped and logged
- Trusted ports may bypass inspection (uplink / router ports)

You can:
- Configure ports as TRUSTED or UNTRUSTED for ARP inspection
- Add DHCP Snooping-like bindings manually (IP ↔ MAC ↔ VLAN)
- Send ARP packets and see if they pass or fail inspection
- View violation counters

Concept:
ARP has no authentication by default.
Attackers can poison ARP tables by claiming:
  "Gateway IP is at my MAC"
DAI blocks such ARP packets.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Literal


ArpOp = Literal["request", "reply"]


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


def is_valid_ipv4(ip: str) -> bool:
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return False
    return all(0 <= n <= 255 for n in nums)

@dataclass
class Binding:
    ip: str
    mac: str
    vlan: int


@dataclass
class PortConfig:
    trusted: bool = False
    violations: int = 0


@dataclass
class ArpPacket:
    op: ArpOp
    sender_ip: str
    sender_mac: str
    target_ip: str
    target_mac: str  # for request can be 00:00:00:00:00:00


class DynamicArpInspectionSwitch:
    def __init__(self, ports: int = 4):
        self.ports: Dict[int, PortConfig] = {p: PortConfig(False) for p in range(1, ports + 1)}
        self.bindings: Dict[tuple[int, str], Binding] = {}  # (vlan, ip) -> binding

    def set_trusted(self, port: int, trusted: bool):
        self._check_port(port)
        self.ports[port].trusted = trusted
        state = "TRUSTED" if trusted else "UNTRUSTED"
        print(f"[Config] Port {port} set to {state} for ARP inspection")

    def add_binding(self, vlan: int, ip: str, mac: str):
        if not is_valid_ipv4(ip):
            raise ValueError("Invalid IP address.")
        if not is_valid_mac(mac):
            raise ValueError("Invalid MAC address.")
        if not (1 <= vlan <= 4094):
            raise ValueError("VLAN must be 1–4094.")

        mac_n = normalize_mac(mac)
        self.bindings[(vlan, ip)] = Binding(ip=ip, mac=mac_n, vlan=vlan)
        print(f"[Binding] VLAN {vlan}: {ip} ↔ {mac_n}")

    def process_arp(self, ingress_port: int, vlan: int, packet: ArpPacket):
        self._check_port(ingress_port)
        if not (1 <= vlan <= 4094):
            print("Invalid VLAN.\n")
            return

        if not (is_valid_ipv4(packet.sender_ip) and is_valid_ipv4(packet.target_ip)):
            print("Invalid IP in ARP packet.\n")
            return
        if not (is_valid_mac(packet.sender_mac) and is_valid_mac(packet.target_mac)):
            print("Invalid MAC in ARP packet.\n")
            return

        sender_mac = normalize_mac(packet.sender_mac)
        target_mac = normalize_mac(packet.target_mac)

        print("\nARP packet received")
        print("-------------------")
        print(f"Ingress port : {ingress_port}")
        print(f"VLAN         : {vlan}")
        print(f"Operation    : {packet.op}")
        print(f"Sender       : {packet.sender_ip} is-at {sender_mac}")
        print(f"Target       : {packet.target_ip} is-at {target_mac}")

        if self.ports[ingress_port].trusted:
            print("Port is TRUSTED → ARP inspection bypassed ✔\n")
            return

        binding = self.bindings.get((vlan, packet.sender_ip))
        if not binding:
            self._violation(ingress_port, reason="no binding exists for sender IP")
            print("Action: ARP DROPPED ❌\n")
            return

        if binding.mac != sender_mac:
            self._violation(ingress_port, reason="sender MAC does not match binding")
            print(f"Expected MAC : {binding.mac}")
            print("Action: ARP DROPPED ❌\n")
            return

        print("ARP validated against binding table ✔")
        print("Action: ARP FORWARDED ✔\n")

    def show_bindings(self):
        if not self.bindings:
            print("\nBinding table is empty.\n")
            return

        print("\nDAI Binding Table (from DHCP Snooping)")
        print("-------------------------------------")
        print(f"{'VLAN':<6} {'IP address':<16} MAC address")
        print("-" * 45)
        for (vlan, ip), b in sorted(self.bindings.items(), key=lambda x: (x[0][0], x[0][1])):
            print(f"{vlan:<6} {ip:<16} {b.mac}")
        print()

    def show_ports(self):
        print("\nPort status (DAI)")
        print("-----------------")
        for p, cfg in self.ports.items():
            state = "TRUSTED" if cfg.trusted else "UNTRUSTED"
            print(f"Port {p}: {state}, violations={cfg.violations}")
        print()

    def _violation(self, port: int, reason: str):
        self.ports[port].violations += 1
        print("DAI VIOLATION ❌")
        print(f"Reason: {reason}")

    def _check_port(self, port: int):
        if port not in self.ports:
            raise ValueError("Invalid port number.")


def print_menu():
    print("=== Task CN41 : Dynamic ARP Inspection (DAI) Simulator ===")
    print("1) Show ports")
    print("2) Set port TRUSTED")
    print("3) Set port UNTRUSTED")
    print("4) Add binding (IP ↔ MAC ↔ VLAN)")
    print("5) Send ARP packet")
    print("6) Show binding table")
    print("7) Exit")

def main():
    sw = DynamicArpInspectionSwitch(ports=4)
    #port 1 is uplink/trusted
    sw.set_trusted(1, True)

    # Demo bindings
    sw.add_binding(10, "192.168.10.10", "aa:aa:aa:aa:aa:10")
    sw.add_binding(10, "192.168.10.1", "aa:aa:aa:aa:aa:01")  # gateway

    while True:
        print_menu()
        choice = input("Choose option (1–7): ").strip()

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
            vlan = int(input("VLAN: ").strip())
            ip = input("IP address: ").strip()
            mac = input("MAC address: ").strip().lower()
            try:
                sw.add_binding(vlan, ip, mac)
                print()
            except ValueError as e:
                print(f"Error: {e}\n")
        elif choice == "5":
            vlan = int(input("VLAN: ").strip())
            port = int(input("Ingress port: ").strip())
            op = input("Operation (request/reply): ").strip().lower()
            sip = input("Sender IP: ").strip()
            smac = input("Sender MAC: ").strip().lower()
            tip = input("Target IP: ").strip()
            tmac = input("Target MAC (00:00:00:00:00:00 for request): ").strip().lower()

            pkt = ArpPacket(op=op, sender_ip=sip, sender_mac=smac, target_ip=tip, target_mac=tmac)
            sw.process_arp(port, vlan, pkt)
        elif choice == "6":
            sw.show_bindings()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")

if __name__ == "__main__":
    main()
