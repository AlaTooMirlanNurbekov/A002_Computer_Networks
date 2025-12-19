"""
Task CN42 : IP Source Guard simulator

Description: this task simulates **IP Source Guard (IPSG)**, a Layer-2 access security feature.

IP Source Guard works together with:
- DHCP Snooping (to build a trusted binding table)
- Dynamic ARP Inspection (optional, related protection)

Core idea:
A switch port will only allow traffic if the packet's:
  Source IP + Source MAC
match a known binding for that port/VLAN.

It prevents attacks like:
- IP spoofing (sending packets with a fake source IP)
- Some man-in-the-middle setups
- Bypassing ACL rules by forging IPs

You can:
- Configure ports to enable/disable IP Source Guard
- Add bindings (IP ↔ MAC ↔ VLAN ↔ port), like DHCP Snooping would
- Send IP "packets" through ports and see allow/drop decisions
- View violation counters

Concept explained:
DHCP Snooping creates a table of which device got which IP.
IP Source Guard uses that table to block spoofed traffic.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple


def is_valid_ipv4(ip: str) -> bool:
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return False
    return all(0 <= n <= 255 for n in nums)


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
class Binding:
    vlan: int
    port: int
    ip: str
    mac: str


@dataclass
class PortConfig:
    ipsg_enabled: bool = False
    violations: int = 0


@dataclass
class IpPacket:
    src_ip: str
    src_mac: str
    dst_ip: str


class IPSGSwitch:
    def __init__(self, ports: int = 4):
        self.ports: Dict[int, PortConfig] = {p: PortConfig(False, 0) for p in range(1, ports + 1)}
   
        self.bindings: Dict[Tuple[int, int], Binding] = {}

    def enable_ipsg(self, port: int, enabled: bool = True):
        self._check_port(port)
        self.ports[port].ipsg_enabled = enabled
        state = "ENABLED" if enabled else "DISABLED"
        print(f"[Config] IP Source Guard {state} on port {port}")

    def add_binding(self, vlan: int, port: int, ip: str, mac: str):
        self._check_port(port)
        if not (1 <= vlan <= 4094):
            raise ValueError("VLAN must be 1–4094.")
        if not is_valid_ipv4(ip):
            raise ValueError("Invalid IPv4 address.")
        if not is_valid_mac(mac):
            raise ValueError("Invalid MAC address.")

        mac_n = normalize_mac(mac)
        self.bindings[(vlan, port)] = Binding(vlan=vlan, port=port, ip=ip, mac=mac_n)
        print(f"[Binding] VLAN {vlan} Port {port}: {ip} ↔ {mac_n}")

    def process_packet(self, vlan: int, ingress_port: int, packet: IpPacket):
        self._check_port(ingress_port)
        if not (1 <= vlan <= 4094):
            print("Invalid VLAN.\n")
            return

        if not (is_valid_ipv4(packet.src_ip) and is_valid_ipv4(packet.dst_ip)):
            print("Invalid IP in packet.\n")
            return
        if not is_valid_mac(packet.src_mac):
            print("Invalid MAC in packet.\n")
            return

        src_mac = normalize_mac(packet.src_mac)

        print("\nIP packet received")
        print("------------------")
        print(f"Ingress port : {ingress_port}")
        print(f"VLAN         : {vlan}")
        print(f"Source       : {packet.src_ip} ({src_mac})")
        print(f"Destination  : {packet.dst_ip}")

        cfg = self.ports[ingress_port]
        if not cfg.ipsg_enabled:
            print("IP Source Guard disabled on this port → packet allowed ✔\n")
            return

        binding = self.bindings.get((vlan, ingress_port))
        if not binding:
            self._violation(ingress_port, "no binding exists for this VLAN+port")
            print("Action: PACKET DROPPED ❌\n")
            return

        if binding.ip != packet.src_ip:
            self._violation(ingress_port, "source IP does not match binding")
            print(f"Expected IP : {binding.ip}")
            print("Action: PACKET DROPPED ❌\n")
            return

        if binding.mac != src_mac:
            self._violation(ingress_port, "source MAC does not match binding")
            print(f"Expected MAC: {binding.mac}")
            print("Action: PACKET DROPPED ❌\n")
            return

        print("Binding match ✔")
        print("Action: PACKET FORWARDED ✔\n")

    def show_ports(self):
        print("\nPort status (IP Source Guard)")
        print("----------------------------")
        for p, cfg in self.ports.items():
            state = "ON" if cfg.ipsg_enabled else "OFF"
            print(f"Port {p}: IPSG={state}, violations={cfg.violations}")
        print()

    def show_bindings(self):
        if not self.bindings:
            print("\nBinding table is empty.\n")
            return

        print("\nIP Source Guard Bindings")
        print("-----------------------")
        print(f"{'VLAN':<6} {'Port':<6} {'IP address':<16} MAC address")
        print("-" * 60)
        for key in sorted(self.bindings.keys()):
            b = self.bindings[key]
            print(f"{b.vlan:<6} {b.port:<6} {b.ip:<16} {b.mac}")
        print()

    def _violation(self, port: int, reason: str):
        self.ports[port].violations += 1
        print("IPSG VIOLATION ❌")
        print(f"Reason: {reason}")

    def _check_port(self, port: int):
        if port not in self.ports:
            raise ValueError("Invalid port number.")

def print_menu():
    print("=== Task CN42 : IP Source Guard Simulator ===")
    print("1) Show ports")
    print("2) Enable IPSG on port")
    print("3) Disable IPSG on port")
    print("4) Add binding (VLAN+port → IP+MAC)")
    print("5) Send IP packet")
    print("6) Show bindings")
    print("7) Exit")


def main():
    sw = IPSGSwitch(ports=4)

    # config
    sw.enable_ipsg(2, True)
    sw.add_binding(10, 2, "192.168.10.10", "aa:aa:aa:aa:aa:10")

    while True:
        print_menu()
        choice = input("Choose option (1–7): ").strip()

        if choice == "1":
            sw.show_ports()
        elif choice == "2":
            p = int(input("Port number: ").strip())
            sw.enable_ipsg(p, True)
            print()
        elif choice == "3":
            p = int(input("Port number: ").strip())
            sw.enable_ipsg(p, False)
            print()
        elif choice == "4":
            vlan = int(input("VLAN: ").strip())
            port = int(input("Port: ").strip())
            ip = input("IP address: ").strip()
            mac = input("MAC address: ").strip().lower()
            try:
                sw.add_binding(vlan, port, ip, mac)
                print()
            except ValueError as e:
                print(f"Error: {e}\n")
        elif choice == "5":
            vlan = int(input("VLAN: ").strip())
            port = int(input("Ingress port: ").strip())
            sip = input("Source IP: ").strip()
            smac = input("Source MAC: ").strip().lower()
            dip = input("Destination IP: ").strip()

            pkt = IpPacket(src_ip=sip, src_mac=smac, dst_ip=dip)
            sw.process_packet(vlan, port, pkt)
        elif choice == "6":
            sw.show_bindings()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")

if __name__ == "__main__":
    main()
