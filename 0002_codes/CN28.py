"""
Task CN28 : ARP table simulator
Description: this task simulates a very simple ARP (Address Resolution Protocol) table.
You can:
- Show the current ARP table
- Add static entries manually (IP → MAC)
- Simulate sending an ARP request and receiving an ARP reply
- Simulate time passing so that dynamic entries expire
- Clear the whole table
Concept explained: ARP is used in IPv4 networks to map IP addresses to MAC addresses inside a LAN.
Devices store mappings in an ARP cache (table). Dynamic entries time out after
some period, and hosts send ARP requests again when needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional
import random
import string

try:
    # Reuse validator from previous tasks if available
    from CN10 import is_valid_ipv4  # type: ignore
except ImportError:
    # Fallback simple IPv4 validator
    def is_valid_ipv4(ip: str) -> bool:
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        try:
            nums = [int(p) for p in parts]
        except ValueError:
            return False
        return all(0 <= n <= 255 for n in nums)

EntryType = Literal["static", "dynamic"]

@dataclass
class ArpEntry:
    ip: str
    mac: str
    entry_type: EntryType
    remaining_ttl: Optional[int]  # seconds; None for static entries

    def is_expired(self) -> bool:
        if self.entry_type == "static":
            return False
        if self.remaining_ttl is None:
            return False
        return self.remaining_ttl <= 0

class ArpTable:
    def __init__(self, default_ttl: int = 60):
        self.entries: List[ArpEntry] = []
        self.default_ttl = default_ttl

    def find(self, ip: str) -> Optional[ArpEntry]:
        for e in self.entries:
            if e.ip == ip:
                return e
        return None

    def add_or_update(self, ip: str, mac: str, entry_type: EntryType = "dynamic") -> ArpEntry:
        existing = self.find(ip)
        if entry_type == "static":
            ttl = None
        else:
            ttl = self.default_ttl

        if existing:
            existing.mac = mac
            existing.entry_type = entry_type
            existing.remaining_ttl = ttl
            return existing

        entry = ArpEntry(ip=ip, mac=mac, entry_type=entry_type, remaining_ttl=ttl)
        self.entries.append(entry)
        return entry

    def age(self, seconds: int) -> None:
        """Simulate time passing: reduce TTL of dynamic entries."""
        for e in self.entries:
            if e.entry_type == "dynamic" and e.remaining_ttl is not None:
                e.remaining_ttl -= seconds

    def remove_expired(self) -> None:
        """Remove dynamic entries whose TTL expired."""
        self.entries = [e for e in self.entries if not e.is_expired()]

    def clear(self) -> None:
        self.entries.clear()

    def print_table(self) -> None:
        if not self.entries:
            print("\nARP Table is empty.\n")
            return

        print("\nCurrent ARP Table")
        print("-----------------")
        print(f"{'IP address':<16} {'MAC address':<18} {'Type':<8} {'Remaining TTL':<12}")
        print("-" * 60)
        for e in self.entries:
            ttl_str = "never" if e.entry_type == "static" else (str(e.remaining_ttl) if e.remaining_ttl is not None else "?")
            print(f"{e.ip:<16} {e.mac:<18} {e.entry_type:<8} {ttl_str:<12}")
        print()


# ------------ helper functions ------------

def generate_random_mac() -> str:
    """Generate a pseudo-random MAC address (for demo purposes only)."""
    return ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))


def print_menu():
    print("=== Task CN28 : ARP Table Simulator ===")
    print("1) Show ARP table")
    print("2) Add STATIC ARP entry")
    print("3) Simulate ARP request + reply (dynamic entry)")
    print("4) Simulate time passing (age & expire dynamic entries)")
    print("5) Clear ARP table")
    print("6) Exit")


def handle_add_static_entry(table: ArpTable):
    print("\nAdd STATIC ARP entry")
    print("--------------------")
    ip = input("Enter IPv4 address (e.g. 192.168.1.10): ").strip()
    if not is_valid_ipv4(ip):
        print("Invalid IPv4 address.\n")
        return

    mac = input("Enter MAC address (or press Enter to auto-generate): ").strip()
    if not mac:
        mac = generate_random_mac()

    table.add_or_update(ip, mac, entry_type="static")
    print(f"Static ARP entry added: {ip} → {mac}\n")


def handle_simulate_arp(table: ArpTable):
    print("\nSimulate ARP Request + Reply")
    print("----------------------------")
    sender_ip = input("Enter SENDER IPv4 address (host asking): ").strip()
    target_ip = input("Enter TARGET IPv4 address (host to find MAC for): ").strip()

    if not is_valid_ipv4(sender_ip) or not is_valid_ipv4(target_ip):
        print("One or both IPs are not valid IPv4 addresses.\n")
        return

    print(f"\n[Host {sender_ip}] wants to send a frame to {target_ip}.")
    print(f"[Host {sender_ip}] looks in ARP table...")

    existing = table.find(target_ip)
    if existing and not existing.is_expired():
        print(f"  ARP hit: {target_ip} → {existing.mac}")
        print("  No ARP request needed (entry already in cache).\n")
        return

    print("  No valid ARP entry found → sending ARP REQUEST (broadcast):")
    print(f"    Who has {target_ip}? Tell {sender_ip}\n")

    #simulate a reply
    mac = input("Enter MAC address for TARGET (or press Enter to auto-generate): ").strip()
    if not mac:
        mac = generate_random_mac()

    print(f"[Host {target_ip}] replies with ARP REPLY:")
    print(f"  {target_ip} is at {mac}\n")
    entry = table.add_or_update(target_ip, mac, entry_type="dynamic")
    print(f"[Host {sender_ip}] updates ARP cache: {entry.ip} → {entry.mac}")
    print(f"Entry type: {entry.entry_type}, TTL: {entry.remaining_ttl} seconds\n")

def handle_age_entries(table: ArpTable):
    print("\nSimulate time passing (age ARP entries)")
    print("---------------------------------------")
    secs_raw = input("Enter number of seconds to simulate: ").strip()
    if not secs_raw.isdigit():
        print("Please enter a positive integer.\n")
        return
    seconds = int(secs_raw)
    if seconds <= 0:
        print("Seconds must be greater than 0.\n")
        return
    print(f"\nAging ARP entries by {seconds} seconds...")
    table.age(seconds)
    before_count = len(table.entries)
    table.remove_expired()
    after_count = len(table.entries)
    removed = before_count - after_count
    print(f"Done. Removed {removed} expired dynamic entr{'y' if removed == 1 else 'ies'}.\n")

def main():
    table = ArpTable(default_ttl=60)

    #optional: pre-load some demo entries
    table.add_or_update("192.168.1.1", "aa:bb:cc:dd:ee:01", entry_type="dynamic")
    table.add_or_update("192.168.1.254", "aa:bb:cc:dd:ee:fe", entry_type="static")
    while True:
        print_menu()
        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            table.print_table()
        elif choice == "2":
            handle_add_static_entry(table)
        elif choice == "3":
            handle_simulate_arp(table)
        elif choice == "4":
            handle_age_entries(table)
        elif choice == "5":
            confirm = input("Are you sure you want to clear the ARP table? (y/n): ").strip().lower()
            if confirm in ("y", "yes"):
                table.clear()
                print("ARP table cleared.\n")
            else:
                print("Clear canceled.\n")
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number 1–6.\n")

# program entry point
if __name__ == "__main__":
    main()
