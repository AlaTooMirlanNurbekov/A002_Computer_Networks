"""
Task CN43 : Private VLAN (PVLAN) simulator

Description: **Private VLANs (PVLANs)**, used to isolate devices inside
the same VLAN while still allowing access to an uplink (gateway / router).

PVLAN roles:
- Primary VLAN: the main VLAN ID carrying PVLAN domain traffic
- Secondary VLANs inside the primary VLAN:
    * Isolated VLAN   → hosts cannot talk to any other host, only to promiscuous ports
    * Community VLAN  → hosts can talk to each other within the same community + promiscuous ports
- Promiscuous port: can talk to all secondary VLANs (typically the gateway/router or server)

This is useful in:
- Data centers (tenant isolation)
- Dormitories / hotels / labs (clients isolated but still have internet)

You can:
- Define a PVLAN domain (primary VLAN + isolated/community groups)
- Configure ports as:
    * PROMISCUOUS
    * ISOLATED host port
    * COMMUNITY host port (with community ID)
- Send frames between ports and see whether they are allowed or blocked

Concept explained:
PVLAN provides isolation without requiring separate VLANs for every host.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Literal


PortType = Literal["promiscuous", "isolated", "community"]


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
class PvlanPortConfig:
    port_type: PortType = "isolated"
    community_id: Optional[int] = None  # only used for community ports


@dataclass
class Frame:
    src_mac: str
    dst_mac: str



class PVLAN:
    def __init__(self, ports: int = 6, primary_vlan: int = 100):
        self.ports = ports
        self.primary_vlan = primary_vlan
        self.port_cfg: Dict[int, PvlanPortConfig] = {p: PvlanPortConfig() for p in range(1, ports + 1)}
        self.mac_to_port: Dict[str, int] = {}  # simple learning (not PVLAN-scoped for simplicity)

    #config

    def set_promiscuous(self, port: int):
        self._check_port(port)
        self.port_cfg[port] = PvlanPortConfig(port_type="promiscuous")
        print(f"[Config] Port {port} set to PROMISCUOUS")

    def set_isolated(self, port: int):
        self._check_port(port)
        self.port_cfg[port] = PvlanPortConfig(port_type="isolated")
        print(f"[Config] Port {port} set to ISOLATED host port")

    def set_community(self, port: int, community_id: int):
        self._check_port(port)
        if community_id <= 0:
            raise ValueError("Community ID must be positive.")
        self.port_cfg[port] = PvlanPortConfig(port_type="community", community_id=community_id)
        print(f"[Config] Port {port} set to COMMUNITY host port (community {community_id})")

    def send_frame(self, ingress_port: int, src_mac: str, dst_mac: str):
        self._check_port(ingress_port)
        if not (is_valid_mac(src_mac) and is_valid_mac(dst_mac)):
            print("Invalid MAC format.\n")
            return

        src = normalize_mac(src_mac)
        dst = normalize_mac(dst_mac)

        cfg_in = self.port_cfg[ingress_port]

        print("\nFrame ingress")
        print("------------")
        print(f"Primary VLAN : {self.primary_vlan}")
        print(f"Ingress port : {ingress_port} ({cfg_in.port_type})")
        if cfg_in.port_type == "community":
            print(f"Community    : {cfg_in.community_id}")
        print(f"Source MAC   : {src}")
        print(f"Dest MAC     : {dst}")
        self.mac_to_port[src] = ingress_port

        egress_port = self.mac_to_port.get(dst)

        if egress_port is None:
            print("[Forward] Unknown destination MAC → flood within allowed PVLAN rules")
            self._flood_allowed(ingress_port)
            print()
            return

        if egress_port == ingress_port:
            print("[Forward] Same ingress/egress port → drop\n")
            return

        cfg_out = self.port_cfg[egress_port]
        allowed = self._pvlan_allows(cfg_in, cfg_out)

        if allowed:
            print(f"[Forward] Allowed by PVLAN rules → forward to port {egress_port} ({cfg_out.port_type}) ✔\n")
        else:
            print(f"[Forward] BLOCKED by PVLAN rules ❌ (port {egress_port} is {cfg_out.port_type})\n")

    def _pvlan_allows(self, src_cfg: PvlanPortConfig, dst_cfg: PvlanPortConfig) -> bool:
       
        if src_cfg.port_type == "promiscuous" or dst_cfg.port_type == "promiscuous":
            return True

        if src_cfg.port_type == "isolated" and dst_cfg.port_type in ("isolated", "community"):
            return False
        if dst_cfg.port_type == "isolated" and src_cfg.port_type in ("isolated", "community"):
            return False

        if src_cfg.port_type == "community" and dst_cfg.port_type == "community":
            return src_cfg.community_id == dst_cfg.community_id

        return False

    def _flood_allowed(self, ingress_port: int):
        src_cfg = self.port_cfg[ingress_port]
        for p in range(1, self.ports + 1):
            if p == ingress_port:
                continue
            dst_cfg = self.port_cfg[p]
            if self._pvlan_allows(src_cfg, dst_cfg):
                print(f"  → flood to port {p} ({dst_cfg.port_type})")

    def show_ports(self):
        print("\nPVLAN Port Configuration")
        print("------------------------")
        print(f"Primary VLAN: {self.primary_vlan}\n")
        for p in range(1, self.ports + 1):
            cfg = self.port_cfg[p]
            if cfg.port_type == "community":
                print(f"Port {p}: COMMUNITY ({cfg.community_id})")
            else:
                print(f"Port {p}: {cfg.port_type.upper()}")
        print()

    def clear_mac_table(self):
        self.mac_to_port.clear()
        print("[Switch] MAC table cleared (learning reset)")

    def _check_port(self, port: int):
        if not (1 <= port <= self.ports):
            raise ValueError(f"Port must be 1–{self.ports}")


def print_menu():
    print("=== Task CN43 : Private VLAN (PVLAN) Simulator ===")
    print("1) Show port configuration")
    print("2) Set PROMISCUOUS port")
    print("3) Set ISOLATED host port")
    print("4) Set COMMUNITY host port")
    print("5) Send frame")
    print("6) Clear MAC learning table")
    print("7) Exit")


def main():
    pv = PVLAN(ports=6, primary_vlan=100)
    pv.set_promiscuous(1)
    pv.set_isolated(2)
    pv.set_isolated(3)
    pv.set_community(4, 10)
    pv.set_community(5, 10)
    pv.set_community(6, 20)

    while True:
        print_menu()
        choice = input("Choose option (1–7): ").strip()

        if choice == "1":
            pv.show_ports()
        elif choice == "2":
            p = int(input("Port number: ").strip())
            pv.set_promiscuous(p)
            print()
        elif choice == "3":
            p = int(input("Port number: ").strip())
            pv.set_isolated(p)
            print()
        elif choice == "4":
            p = int(input("Port number: ").strip())
            cid = int(input("Community ID: ").strip())
            pv.set_community(p, cid)
            print()
        elif choice == "5":
            p = int(input("Ingress port: ").strip())
            sm = input("Source MAC: ").strip().lower()
            dm = input("Destination MAC: ").strip().lower()
            pv.send_frame(p, sm, dm)
        elif choice == "6":
            pv.clear_mac_table()
            print()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")

if __name__ == "__main__":
    main()
