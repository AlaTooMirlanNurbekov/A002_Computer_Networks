"""
Task CN30 : NAT (Network Address Translation) simulator

Description: this task simulates how a basic **Source NAT (SNAT)** and **Port Address Translation (PAT)** 
work on a home router.

- View NAT translation table
- Add LAN hosts (internal IPs)
- Simulate an internal host sending traffic to the internet → NAT creates/updates a mapping
- Simulate return traffic from the internet → NAT looks up the mapping and forwards it
- Expire old NAT entries
- Clear NAT table

Concepts:
- NAT replaces the *source IP* of an outbound packet with the router’s public IP.
- PAT also replaces the *source port* to allow many internal devices to share one public IP.
- Return traffic must match an existing NAT mapping or it is dropped.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import random
import time

try:
    from CN10 import is_valid_ipv4  # type: ignore
except ImportError:
    def is_valid_ipv4(ip: str) -> bool:
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        try:
            nums = [int(p) for p in parts]
        except ValueError:
            return False
        return all(0 <= n <= 255 for n in nums)

# -------------------------
# NAT entry structure
# -------------------------
@dataclass
class NatEntry:
    internal_ip: str
    internal_port: int
    external_ip: str  # The router’s public IP
    external_port: int
    remote_ip: str
    remote_port: int
    ttl: int  # seconds remaining
class NAT:
    def __init__(self, public_ip: str, default_ttl: int = 60):
        self.public_ip = public_ip
        self.default_ttl = default_ttl
        self.table: List[NatEntry] = []

    # -----------------------------
    # Helper: find existing mapping
    # -----------------------------
    def find_mapping(self, internal_ip: str, internal_port: int, remote_ip: str, remote_port: int) -> Optional[NatEntry]:
        for e in self.table:
            if (e.internal_ip == internal_ip and e.internal_port == internal_port
                and e.remote_ip == remote_ip and e.remote_port == remote_port):
                return e
        return None

    def find_reverse(self, external_port: int, remote_ip: str, remote_port: int) -> Optional[NatEntry]:
        """Find mapping when return traffic arrives."""
        for e in self.table:
            if e.external_port == external_port and e.remote_ip == remote_ip and e.remote_port == remote_port:
                return e
        return None
    # -----------------------------
    # Simulate outbound connection
    # -----------------------------
    def outbound_packet(self, internal_ip: str, internal_port: int, remote_ip: str, remote_port: int) -> NatEntry:
        mapping = self.find_mapping(internal_ip, internal_port, remote_ip, remote_port)
        if mapping:
            print(f"Found existing NAT mapping: {mapping.external_ip}:{mapping.external_port}")
            mapping.ttl = self.default_ttl
            return mapping

        external_port = random.randint(20000, 60000)
        entry = NatEntry(
            internal_ip=internal_ip,
            internal_port=internal_port,
            external_ip=self.public_ip,
            external_port=external_port,
            remote_ip=remote_ip,
            remote_port=remote_port,
            ttl=self.default_ttl,
        )

        self.table.append(entry)
        print(f"Created new NAT entry: {internal_ip}:{internal_port} → {self.public_ip}:{external_port}")
        return entry
    # -----------------------------
    # Simulate inbound return traffic
    # -----------------------------
    def inbound_packet(self, external_port: int, remote_ip: str, remote_port: int) -> Optional[NatEntry]:
        mapping = self.find_reverse(external_port, remote_ip, remote_port)
        if mapping:
            print(f"Return traffic matched NAT entry → forward to {mapping.internal_ip}:{mapping.internal_port}")
            mapping.ttl = self.default_ttl
            return mapping
        else:
            print("No NAT mapping found → DROP packet.")
            return None

    # -----------------------------
    # Manage TTL
    # -----------------------------
    def age(self, seconds: int):
        for e in self.table:
            e.ttl -= seconds
        self.table = [e for e in self.table if e.ttl > 0]
    def clear(self):
        self.table.clear()

    def print_table(self):
        if not self.table:
            print("\nNAT table is empty.\n")
            return

        print("\nCurrent NAT Table")
        print("-----------------")
        print(f"{'Internal':<20} {'External':<20} {'Remote':<20} TTL")
        print("-" * 72)
        for e in self.table:
            internal = f"{e.internal_ip}:{e.internal_port}"
            external = f"{e.external_ip}:{e.external_port}"
            remote = f"{e.remote_ip}:{e.remote_port}"
            print(f"{internal:<20} {external:<20} {remote:<20} {e.ttl}")
        print()
# -------------------------
# Menu interface
# -------------------------
def print_menu():
    print("=== Task CN30 : NAT Simulator (SNAT + PAT) ===")
    print("1) Show NAT table")
    print("2) Add outbound packet (create/refresh NAT entry)")
    print("3) Simulate inbound return packet")
    print("4) Age NAT entries")
    print("5) Clear NAT table")
    print("6) Exit")

def handle_outbound(nat: NAT):
    print("\nSimulate outbound packet")
    print("------------------------")
    internal_ip = input("Internal IP: ").strip()
    port_raw = input("Internal source port: ").strip()
    remote_ip = input("Remote IP: ").strip()
    remote_port_raw = input("Remote port: ").strip()

    if not (is_valid_ipv4(internal_ip) and is_valid_ipv4(remote_ip)):
        print("Invalid IP format.\n")
        return
    if not (port_raw.isdigit() and remote_port_raw.isdigit()):
        print("Ports must be numeric.\n")
        return

    internal_port = int(port_raw)
    remote_port = int(remote_port_raw)
    entry = nat.outbound_packet(internal_ip, internal_port, remote_ip, remote_port)
    print(f"NAT mapping now active: {entry.internal_ip}:{entry.internal_port} → "
          f"{entry.external_ip}:{entry.external_port}\n")


def handle_inbound(nat: NAT):
    print("\nSimulate inbound packet (reply from remote server)")
    print("--------------------------------------------------")
    port_raw = input("External port (destination on public IP): ").strip()
    remote_ip = input("Remote IP (source of incoming packet): ").strip()
    remote_port_raw = input("Remote port: ").strip()
    if not (port_raw.isdigit() and remote_port_raw.isdigit()):
        print("Ports must be numeric.\n")
        return
    if not is_valid_ipv4(remote_ip):
        print("Invalid remote IP.\n")
        return
    external_port = int(port_raw)
    remote_port = int(remote_port_raw)
    nat.inbound_packet(external_port, remote_ip, remote_port)
    print()

def handle_age(nat: NAT):
    print("\nSimulate time passing (age NAT entries)")
    print("---------------------------------------")
    secs_raw = input("Seconds to age: ").strip()
    if not secs_raw.isdigit():
        print("Enter a valid number.\n")
        return
    seconds = int(secs_raw)
    nat.age(seconds)
    print(f"Aged {seconds} seconds.\n")

def main():
    router_public_ip = "203.0.113.10"
    nat = NAT(public_ip=router_public_ip)

    while True:
        print_menu()
        choice = input("Choose option (1–6): ").strip()
        if choice == "1":
            nat.print_table()
        elif choice == "2":
            handle_outbound(nat)
        elif choice == "3":
            handle_inbound(nat)
        elif choice == "4":
            handle_age(nat)
        elif choice == "5":
            nat.clear()
            print("NAT table cleared.\n")
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Enter 1–6.\n")
# program entry point
if __name__ == "__main__":
    main()
