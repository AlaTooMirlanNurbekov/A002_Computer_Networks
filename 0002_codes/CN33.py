"""
Task CN33 : switch MAC address table simulator

Description: simulates how an Ethernet switch learns and uses a MAC address table.

You can:
- Send frames into the switch from a given port
- Observe MAC learning (source MAC → incoming port)
- See forwarding decisions:
    * Known destination MAC → forward to specific port
    * Unknown destination MAC → flood to all other ports
    * Broadcast MAC → flood to all other ports
- Age MAC table entries over time
- Clear the MAC table

Concept:
Layer 2 switches work by:
1) Learning source MAC addresses on incoming ports
2) Storing them in a MAC (CAM) table with a timer
3) Forwarding frames intelligently instead of blindly flooding
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
import time
import random


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
class MacEntry:
    mac: str
    port: int
    ttl: int  # seconds remaining

class Switch:
    def __init__(self, ports: int = 4, entry_ttl: int = 60):
        self.ports = ports
        self.entry_ttl = entry_ttl
        self.mac_table: Dict[str, MacEntry] = {}

    def learn_mac(self, mac: str, port: int):
        mac = normalize_mac(mac)
        self.mac_table[mac] = MacEntry(mac, port, self.entry_ttl)
        print(f"[Switch] Learned MAC {mac} on port {port}")

    def age_table(self, seconds: int):
        expired = []
        for mac, entry in self.mac_table.items():
            entry.ttl -= seconds
            if entry.ttl <= 0:
                expired.append(mac)

        for mac in expired:
            del self.mac_table[mac]
            print(f"[Switch] Aged out MAC entry {mac}")

    def forward_frame(self, src_mac: str, dst_mac: str, ingress_port: int):
        print("\nFrame received:")
        print(f"  Ingress port : {ingress_port}")
        print(f"  Source MAC   : {src_mac}")
        print(f"  Dest MAC     : {dst_mac}")

        self.learn_mac(src_mac, ingress_port)
        dst_mac_n = normalize_mac(dst_mac)
        broadcast = "ff:ff:ff:ff:ff:ff"

        if dst_mac_n == broadcast:
            self.flood(ingress_port, reason="broadcast")
            return
        entry = self.mac_table.get(dst_mac_n)
        if entry:
            print(f"[Switch] Destination MAC known → forwarding to port {entry.port}")
            if entry.port != ingress_port:
                print(f"[Switch] Frame forwarded out port {entry.port}")
            else:
                print("[Switch] Source and destination on same port → frame dropped")
        else:
            self.flood(ingress_port, reason="unknown destination MAC")
    def flood(self, ingress_port: int, reason: str):
        print(f"[Switch] Flooding frame ({reason})")
        for port in range(1, self.ports + 1):
            if port != ingress_port:
                print(f"  → Sent out port {port}")
    def print_mac_table(self):
        if not self.mac_table:
            print("\nMAC table is empty.\n")
            return
        print("\nCurrent MAC Address Table")
        print("-------------------------")
        print(f"{'MAC address':<20} {'Port':<6} TTL")
        print("-" * 40)
        for entry in self.mac_table.values():
            print(f"{entry.mac:<20} {entry.port:<6} {entry.ttl}")
        print()
    def clear(self):
        self.mac_table.clear()
        print("[Switch] MAC table cleared")

def print_menu():
    print("=== Task CN33 : Switch MAC Table Simulator ===")
    print("1) Show MAC table")
    print("2) Send Ethernet frame")
    print("3) Age MAC table")
    print("4) Clear MAC table")
    print("5) Exit")

def handle_send_frame(sw: Switch):
    print("\nSend Ethernet frame")
    print("-------------------")
    src_mac = input("Source MAC (aa:bb:cc:dd:ee:ff): ").strip().lower()
    dst_mac = input("Destination MAC: ").strip().lower()
    port_raw = input(f"Ingress port (1–{sw.ports}): ").strip()
    if not (is_valid_mac(src_mac) and is_valid_mac(dst_mac)):
        print("Invalid MAC address format.\n")
        return
    if not port_raw.isdigit():
        print("Port must be a number.\n")
        return
    port = int(port_raw)
    if not (1 <= port <= sw.ports):
        print("Port number out of range.\n")
        return
    sw.forward_frame(src_mac, dst_mac, port)

def handle_age(sw: Switch):
    print("\nAge MAC table")
    print("-------------")
    secs_raw = input("Seconds to age: ").strip()
    if not secs_raw.isdigit():
        print("Invalid number.\n")
        return
    seconds = int(secs_raw)
    sw.age_table(seconds)
    print("Aging complete.\n")

def main():
    sw = Switch(ports=4, entry_ttl=60)
    #preload demo MACs
    sw.learn_mac("aa:aa:aa:aa:aa:01", 1)
    sw.learn_mac("aa:aa:aa:aa:aa:02", 2)
    while True:
        print_menu()
        choice = input("Choose option (1–5): ").strip()
        if choice == "1":
            sw.print_mac_table()
        elif choice == "2":
            handle_send_frame(sw)
        elif choice == "3":
            handle_age(sw)
        elif choice == "4":
            sw.clear()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")

# program entry point
if __name__ == "__main__":
    main()
