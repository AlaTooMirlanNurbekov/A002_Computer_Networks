"""
Task CN34 : VLAN & trunking simulator (802.1Q concept)

Description: this task simulates how VLANs work on a switch, including:
- Access ports (belong to exactly one VLAN)
- Trunk ports (carry multiple VLANs using 802.1Q tags)
- Frame forwarding rules:
    * Frames stay inside their VLAN (broadcast domain)
    * Unknown destination within VLAN → flood only within that VLAN
    * Trunk ports carry VLAN-tagged frames for allowed VLANs
    * Access ports send/receive untagged frames in their access VLAN

You can:
- Configure ports as ACCESS or TRUNK
- Assign access VLANs
- Set trunk allowed VLAN list
- Send frames between ports and observe forwarding decisions
- Inspect the MAC table per VLAN
- Age MAC entries

Concepts:
- VLAN = logical segmentation on Layer 2
- Access port = untagged in one VLAN
- Trunk port = tagged frames for many VLANs (802.1Q)
- Switch maintains MAC learning per VLAN (MAC tables are VLAN-scoped)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Set, Tuple, Literal, List


PortMode = Literal["access", "trunk"]

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


def parse_vlan_list(text: str) -> Set[int]:
    """
    Parses vlan list like:
      "10,20,30"
      "1-5,10,20-22"
    Returns a set of VLAN IDs.
    """
    text = text.strip()
    if not text:
        return set()

    vlans: Set[int] = set()
    parts = [p.strip() for p in text.split(",") if p.strip()]
    for p in parts:
        if "-" in p:
            a, b = p.split("-", 1)
            if not (a.strip().isdigit() and b.strip().isdigit()):
                raise ValueError("Invalid VLAN range.")
            start = int(a.strip())
            end = int(b.strip())
            if start > end:
                raise ValueError("VLAN range start must be <= end.")
            for v in range(start, end + 1):
                if not (1 <= v <= 4094):
                    raise ValueError("VLAN IDs must be between 1 and 4094.")
                vlans.add(v)
        else:
            if not p.isdigit():
                raise ValueError("Invalid VLAN ID.")
            v = int(p)
            if not (1 <= v <= 4094):
                raise ValueError("VLAN IDs must be between 1 and 4094.")
            vlans.add(v)
    return vlans

@dataclass
class PortConfig:
    mode: PortMode = "access"
    access_vlan: int = 1
    trunk_allowed_vlans: Set[int] = None  # None means "all allowed" (simplified)

    def __post_init__(self):
        if self.trunk_allowed_vlans is None:
            self.trunk_allowed_vlans = set()


@dataclass
class VlanMacEntry:
    mac: str
    port: int
    vlan: int
    ttl: int

class VlanSwitch:
    def __init__(self, ports: int = 6, mac_ttl: int = 60):
        self.ports = ports
        self.mac_ttl = mac_ttl

        #port configs
        self.port_cfg: Dict[int, PortConfig] = {p: PortConfig() for p in range(1, ports + 1)}

        self.mac_table: Dict[Tuple[int, str], VlanMacEntry] = {}

    # ---- port configuration ----

    def set_access_port(self, port: int, vlan: int):
        self._check_port(port)
        self._check_vlan(vlan)
        cfg = self.port_cfg[port]
        cfg.mode = "access"
        cfg.access_vlan = vlan
        cfg.trunk_allowed_vlans = set()
        print(f"[Config] Port {port} set to ACCESS VLAN {vlan}")

    def set_trunk_port(self, port: int, allowed_vlans: Optional[Set[int]] = None):
        self._check_port(port)
        cfg = self.port_cfg[port]
        cfg.mode = "trunk"
        if allowed_vlans is None or len(allowed_vlans) == 0:
            cfg.trunk_allowed_vlans = set()  # empty set = allow all (simplified)
            print(f"[Config] Port {port} set to TRUNK (allowed VLANs: ALL)")
        else:
            for v in allowed_vlans:
                self._check_vlan(v)
            cfg.trunk_allowed_vlans = set(allowed_vlans)
            print(f"[Config] Port {port} set to TRUNK (allowed VLANs: {sorted(cfg.trunk_allowed_vlans)})")

    def show_ports(self):
        print("\nPort configuration")
        print("------------------")
        print(f"{'Port':<6} {'Mode':<8} {'Access VLAN':<12} Allowed VLANs (trunk)")
        print("-" * 60)
        for p in range(1, self.ports + 1):
            cfg = self.port_cfg[p]
            allowed = "ALL" if (cfg.mode == "trunk" and len(cfg.trunk_allowed_vlans) == 0) else ",".join(map(str, sorted(cfg.trunk_allowed_vlans)))
            if cfg.mode == "access":
                allowed = "-"
            print(f"{p:<6} {cfg.mode:<8} {cfg.access_vlan:<12} {allowed}")
        print()

    def learn(self, vlan: int, mac: str, port: int):
        mac_n = normalize_mac(mac)
        key = (vlan, mac_n)
        self.mac_table[key] = VlanMacEntry(mac=mac_n, port=port, vlan=vlan, ttl=self.mac_ttl)
        print(f"[Learn] VLAN {vlan}: learned {mac_n} on port {port}")

    def age(self, seconds: int):
        expired = []
        for key, entry in self.mac_table.items():
            entry.ttl -= seconds
            if entry.ttl <= 0:
                expired.append(key)
        for key in expired:
            del self.mac_table[key]
        print(f"[Aging] Aged {seconds}s. Removed {len(expired)} expired MAC entries.")

    def show_mac_table(self):
        if not self.mac_table:
            print("\nMAC table is empty.\n")
            return
        print("\nMAC table (VLAN-scoped)")
        print("----------------------")
        print(f"{'VLAN':<6} {'MAC address':<20} {'Port':<6} TTL")
        print("-" * 45)
        for entry in sorted(self.mac_table.values(), key=lambda e: (e.vlan, e.mac)):
            print(f"{entry.vlan:<6} {entry.mac:<20} {entry.port:<6} {entry.ttl}")
        print()

    def send_frame(self, ingress_port: int, src_mac: str, dst_mac: str, vlan_tag: Optional[int] = None):
        """
        Ingress rules:
        - If ingress is ACCESS: VLAN is access_vlan and frame is untagged (ignore vlan_tag)
        - If ingress is TRUNK: VLAN must be provided (vlan_tag), and must be allowed on trunk

        Forwarding:
        - Learn src MAC in that VLAN
        - If dst is broadcast or unknown in VLAN: flood within VLAN
        - If known: forward only to learned port (within VLAN rules)
        """
        self._check_port(ingress_port)

        if not (is_valid_mac(src_mac) and is_valid_mac(dst_mac)):
            print("Invalid MAC address format.\n")
            return

        cfg_in = self.port_cfg[ingress_port]
        vlan = self._determine_ingress_vlan(cfg_in, vlan_tag)
        if vlan is None:
            print("Frame dropped at ingress due to VLAN rules.\n")
            return

        src_n = normalize_mac(src_mac)
        dst_n = normalize_mac(dst_mac)

        print("\nFrame ingress")
        print("------------")
        print(f"Ingress port : {ingress_port} ({cfg_in.mode})")
        print(f"VLAN         : {vlan}")
        print(f"Source MAC   : {src_n}")
        print(f"Dest MAC     : {dst_n}")

        # Learn source
        self.learn(vlan, src_n, ingress_port)

        broadcast = "ff:ff:ff:ff:ff:ff"
        if dst_n == broadcast:
            self._flood(vlan, ingress_port, reason="broadcast")
            print()
            return
        entry = self.mac_table.get((vlan, dst_n))
        if entry:
            if entry.port == ingress_port:
                print("[Forward] Destination learned on same ingress port → drop (no need to forward)\n")
                return
            print(f"[Forward] Destination known in VLAN {vlan} → forward to port {entry.port}")
            self._egress_send(vlan, ingress_port, entry.port, dst_n, tagged=(self.port_cfg[entry.port].mode == "trunk"))
            print()
        else:
            self._flood(vlan, ingress_port, reason="unknown destination")
            print()

    def _flood(self, vlan: int, ingress_port: int, reason: str):
        print(f"[Flood] VLAN {vlan}: flooding ({reason}) out all VLAN-member ports except ingress")
        for p in range(1, self.ports + 1):
            if p == ingress_port:
                continue
            if self._port_carries_vlan(p, vlan):
                self._egress_send(vlan, ingress_port, p, "ff:ff:ff:ff:ff:ff", tagged=(self.port_cfg[p].mode == "trunk"))

    def _egress_send(self, vlan: int, ingress_port: int, egress_port: int, dst_mac: str, tagged: bool):
        cfg = self.port_cfg[egress_port]
        tag_txt = f"tagged VLAN {vlan}" if tagged else "untagged"
        print(f"  → out port {egress_port} ({cfg.mode}), {tag_txt}")

    def _determine_ingress_vlan(self, cfg: PortConfig, vlan_tag: Optional[int]) -> Optional[int]:
        if cfg.mode == "access":
            return cfg.access_vlan

        if vlan_tag is None:
            print("[Ingress] Trunk port requires VLAN tag in this simulator.")
            return None

        self._check_vlan(vlan_tag)

        if len(cfg.trunk_allowed_vlans) == 0:
            # empty allowed list => allow all (simplified)
            return vlan_tag

        if vlan_tag not in cfg.trunk_allowed_vlans:
            print(f"[Ingress] VLAN {vlan_tag} is NOT allowed on this trunk.")
            return None

        return vlan_tag

    def _port_carries_vlan(self, port: int, vlan: int) -> bool:
        cfg = self.port_cfg[port]
        if cfg.mode == "access":
            return cfg.access_vlan == vlan
        # trunk:
        if len(cfg.trunk_allowed_vlans) == 0:
            return True  # allow all
        return vlan in cfg.trunk_allowed_vlans


    def _check_port(self, port: int):
        if not (1 <= port <= self.ports):
            raise ValueError(f"Port must be between 1 and {self.ports}")

    def _check_vlan(self, vlan: int):
        if not (1 <= vlan <= 4094):
            raise ValueError("VLAN must be 1–4094")


def print_menu():
    print("=== Task CN34 : VLAN & Trunking Simulator ===")
    print("1) Show port configuration")
    print("2) Set ACCESS port")
    print("3) Set TRUNK port")
    print("4) Show MAC table")
    print("5) Send frame")
    print("6) Age MAC table")
    print("7) Clear MAC table")
    print("8) Exit")

def handle_set_access(sw: VlanSwitch):
    p_raw = input("Port number: ").strip()
    v_raw = input("Access VLAN: ").strip()
    if not (p_raw.isdigit() and v_raw.isdigit()):
        print("Port and VLAN must be numeric.\n")
        return
    p = int(p_raw)
    v = int(v_raw)
    try:
        sw.set_access_port(p, v)
        print()
    except ValueError as e:
        print(f"Error: {e}\n")

def handle_set_trunk(sw: VlanSwitch):
    p_raw = input("Port number: ").strip()
    if not p_raw.isdigit():
        print("Port must be numeric.\n")
        return
    p = int(p_raw)
    allowed_raw = input("Allowed VLANs (e.g. 10,20,30 or 1-5,10). Empty = ALL: ").strip()
    try:
        allowed = parse_vlan_list(allowed_raw) if allowed_raw else None
        sw.set_trunk_port(p, allowed)
        print()
    except ValueError as e:
        print(f"Error: {e}\n")
def handle_send_frame(sw: VlanSwitch):
    p_raw = input("Ingress port: ").strip()
    src = input("Source MAC: ").strip().lower()
    dst = input("Destination MAC (or ff:ff:ff:ff:ff:ff): ").strip().lower()

    if not p_raw.isdigit():
        print("Port must be numeric.\n")
        return
    p = int(p_raw)
    vlan_tag = None
    if sw.port_cfg.get(p) and sw.port_cfg[p].mode == "trunk":
        tag_raw = input("VLAN tag for trunk ingress: ").strip()
        if not tag_raw.isdigit():
            print("VLAN tag must be numeric for trunk ingress.\n")
            return
        vlan_tag = int(tag_raw)
    try:
        sw.send_frame(p, src, dst, vlan_tag)
    except ValueError as e:
        print(f"Error: {e}\n")

def handle_age(sw: VlanSwitch):
    s_raw = input("Seconds to age: ").strip()
    if not s_raw.isdigit():
        print("Seconds must be numeric.\n")
        return
    sw.age(int(s_raw))
    print()

def main():
    sw = VlanSwitch(ports=6, mac_ttl=60)

    # Demo config:
    # Ports 1-2: VLAN 10 access
    # Ports 3-4: VLAN 20 access
    # Port 5: trunk allowing 10,20
    sw.set_access_port(1, 10)
    sw.set_access_port(2, 10)
    sw.set_access_port(3, 20)
    sw.set_access_port(4, 20)
    sw.set_trunk_port(5, {10, 20})
    while True:
        print_menu()
        choice = input("Choose option (1–8): ").strip()
        if choice == "1":
            sw.show_ports()
        elif choice == "2":
            handle_set_access(sw)
        elif choice == "3":
            handle_set_trunk(sw)
        elif choice == "4":
            sw.show_mac_table()
        elif choice == "5":
            handle_send_frame(sw)
        elif choice == "6":
            handle_age(sw)
        elif choice == "7":
            sw.mac_table.clear()
            print("MAC table cleared.\n")
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")

# program entry point
if __name__ == "__main__":
    main()
