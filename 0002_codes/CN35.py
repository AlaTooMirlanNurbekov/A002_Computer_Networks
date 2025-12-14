"""
Task CN35 : Inter VLAN routing simulator

Description: this task simulates **Inter-VLAN routing** using the classic
**router-on-a-stick** approach.

Scenario:
- A switch has multiple VLANs
- A router is connected to the switch via a TRUNK link
- The router has subinterfaces (e.g. G0/0.10, G0/0.20)
- Each subinterface acts as the default gateway for its VLAN
- Hosts in different VLANs can communicate ONLY via the router
You can:
- Define VLANs and their IP subnets
- Configure router subinterfaces (VLAN ↔ IP gateway mapping)
- Add hosts to VLANs
- Send a "packet" from one host to another
- Observe routing decisions step by step

Concepts:
- Why VLANs isolate broadcast domains
- Why routing is required for inter-VLAN communication
- How router subinterfaces work with 802.1Q tags
- Default gateway logic
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, List

def is_valid_ipv4(ip: str) -> bool:
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return False
    return all(0 <= n <= 255 for n in nums)

def ip_to_int(ip: str) -> int:
    value = 0
    for p in ip.split("."):
        value = (value << 8) | int(p)
    return value

def same_subnet(ip1: str, ip2: str, mask: str) -> bool:
    return (ip_to_int(ip1) & ip_to_int(mask)) == (ip_to_int(ip2) & ip_to_int(mask))

@dataclass
class VLAN:
    vlan_id: int
    network: str
    subnet_mask: str


@dataclass
class Host:
    name: str
    ip: str
    vlan_id: int
    gateway: str


@dataclass
class RouterSubInterface:
    vlan_id: int
    ip: str  # gateway IP


class RouterOnAStick:
    def __init__(self):
        self.subinterfaces: Dict[int, RouterSubInterface] = {}

    def add_subinterface(self, vlan_id: int, ip: str):
        if not is_valid_ipv4(ip):
            raise ValueError("Invalid IP address.")
        self.subinterfaces[vlan_id] = RouterSubInterface(vlan_id, ip)
        print(f"[Router] Subinterface for VLAN {vlan_id} configured with IP {ip}")

    def route(self, src: Host, dst: Host) -> bool:
        print("\n[Router] Routing decision")
        print("-------------------------")

        # Check ingress VLAN
        if src.vlan_id not in self.subinterfaces:
            print(f"No router interface for source VLAN {src.vlan_id}")
            return False

        if dst.vlan_id not in self.subinterfaces:
            print(f"No router interface for destination VLAN {dst.vlan_id}")
            return False

        print(f"Packet arrives on subinterface VLAN {src.vlan_id}")
        print(f"Routing to subinterface VLAN {dst.vlan_id}")
        print("Packet forwarded successfully ✔")
        return True

class InterVlanNetwork:
    def __init__(self):
        self.vlans: Dict[int, VLAN] = {}
        self.hosts: Dict[str, Host] = {}
        self.router = RouterOnAStick()

    def add_vlan(self, vlan_id: int, network: str, mask: str):
        self.vlans[vlan_id] = VLAN(vlan_id, network, mask)
        print(f"[Switch] VLAN {vlan_id} created ({network}/{mask})")

    def add_host(self, name: str, ip: str, vlan_id: int, gateway: str):
        if vlan_id not in self.vlans:
            raise ValueError("VLAN does not exist.")
        self.hosts[name] = Host(name, ip, vlan_id, gateway)
        print(f"[Host] {name} added: {ip} in VLAN {vlan_id}")

    def send_packet(self, src_name: str, dst_name: str):
        print("\n=== Inter-VLAN Packet Simulation ===")

        if src_name not in self.hosts or dst_name not in self.hosts:
            print("Source or destination host not found.")
            return
        src = self.hosts[src_name]
        dst = self.hosts[dst_name]

        print(f"Source      : {src.name} ({src.ip}) VLAN {src.vlan_id}")
        print(f"Destination : {dst.name} ({dst.ip}) VLAN {dst.vlan_id}")
        # Same VLAN?
        if src.vlan_id == dst.vlan_id:
            print("Same VLAN → direct Layer 2 communication ✔")
            return
        #Different VLAN → routing required
        print("Different VLANs → routing required")
        print(f"{src.name} sends packet to default gateway {src.gateway}")
        success = self.router.route(src, dst)
        if success:
            print("Inter-VLAN communication SUCCESSFUL ✔\n")
        else:
            print("Inter-VLAN communication FAILED ❌\n")

    def show_state(self):
        print("\nCurrent network state")
        print("---------------------")
        print("VLANs:")
        for v in self.vlans.values():
            print(f"  VLAN {v.vlan_id} → {v.network}/{v.subnet_mask}")
        print("\nRouter subinterfaces:")
        for si in self.router.subinterfaces.values():
            print(f"  VLAN {si.vlan_id} → {si.ip}")
        print("\nHosts:")
        for h in self.hosts.values():
            print(f"  {h.name}: {h.ip}, VLAN {h.vlan_id}, GW {h.gateway}")
        print()

def main():
    net = InterVlanNetwork()
    # Create VLANs
    net.add_vlan(10, "192.168.10.0", "255.255.255.0")
    net.add_vlan(20, "192.168.20.0", "255.255.255.0")
    # Configure router subinterfaces
    net.router.add_subinterface(10, "192.168.10.1")
    net.router.add_subinterface(20, "192.168.20.1")

    # Add hosts
    net.add_host("PC_A", "192.168.10.10", 10, "192.168.10.1")
    net.add_host("PC_B", "192.168.20.20", 20, "192.168.20.1")
    net.show_state()
    #test communication
    net.send_packet("PC_A", "PC_B")
    net.send_packet("PC_A", "PC_A")

# program entry point
if __name__ == "__main__":
    main()
