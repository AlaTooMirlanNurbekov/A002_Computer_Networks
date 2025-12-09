"""
Task CN29 : routing table & longest-prefix-match simulator

Description: this task simulates a very simple IP routing table and how routers choose
the best route using the **longest prefix match** rule
- Show current routing table
- Add static routes (destination network in CIDR, next hop, interface, metric)
- Delete a route by index
- Test a packet (destination IP) to see which route will be used
- See what happens when only default route matches

Concept explained: routers use a routing table to decide where to forward packets.
For each incoming packet, the router:
  1) Looks at the destination IP
  2) Finds all routes whose network includes that IP
  3) Chooses the route with the **longest prefix** (most specific match)
  4) If there is a tie in prefix length, uses the **lowest metric**
  5) If nothing matches, it may use a **default route (0.0.0.0/0)** or drop the packet

This simulator shows that decision process step by step.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple, Literal


try:
    #reuse shared validator if present
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


def ip_to_int(ip: str) -> int:
    parts = [int(p) for p in ip.split(".")]
    value = 0
    for p in parts:
        value = (value << 8) | p
    return value


def int_to_ip(value: int) -> str:
    return ".".join(str((value >> (8 * i)) & 0xFF) for i in range(3, -1, -1))


@dataclass
class Route:
    """
    Represents a single routing table entry.

    Example:
    - destination: "192.168.1.0"
    - prefix: 24
    - next_hop: "192.168.0.1" or "direct"
    - interface: "eth0"
    - metric: 10
    - description: "LAN 1"
    """
    destination: str
    prefix: int
    next_hop: str  # "direct" or IPv4 string
    interface: str
    metric: int
    description: str = ""
    def network_int(self) -> int:
        return ip_to_int(self.destination)

    def mask_int(self) -> int:
        if self.prefix == 0:
            return 0
        return (0xFFFFFFFF << (32 - self.prefix)) & 0xFFFFFFFF

    def matches(self, ip: str) -> bool:
        if not is_valid_ipv4(ip):
            return False
        ip_int = ip_to_int(ip)
        mask = self.mask_int()
        return (ip_int & mask) == (self.network_int() & mask)

    def network_cidr(self) -> str:
        return f"{self.destination}/{self.prefix}"
class RoutingTable:
    def __init__(self):
        self.routes: List[Route] = []
    def add_route(
        self,
        destination_cidr: str,
        next_hop: str,
        interface: str,
        metric: int,
        description: str = "",
    ) -> None:
        dest, prefix = self._parse_cidr(destination_cidr)
        if next_hop != "direct" and not is_valid_ipv4(next_hop):
            raise ValueError("Next hop must be 'direct' or a valid IPv4 address.")
        if metric < 0:
            raise ValueError("Metric must be non-negative.")
        route = Route(
            destination=dest,
            prefix=prefix,
            next_hop=next_hop,
            interface=interface,
            metric=metric,
            description=description,
        )
        self.routes.append(route)

    def delete_route(self, index: int) -> bool:
        if 0 <= index < len(self.routes):
            del self.routes[index]
            return True
        return False

    def list_routes(self) -> None:
        if not self.routes:
            print("\nRouting table is empty.\n")
            return
        print("\nCurrent Routing Table")
        print("---------------------")
        print(
            f"{'Idx':<4} {'Destination':<18} {'Next hop':<15} "
            f"{'Iface':<8} {'Metric':<6} Description"
        )
        print("-" * 70)
        for i, r in enumerate(self.routes):
            nh = r.next_hop
            print(
                f"{i:<4} {r.network_cidr():<18} {nh:<15} "
                f"{r.interface:<8} {r.metric:<6} {r.description}"
            )
        print()

    def _parse_cidr(self, cidr: str) -> Tuple[str, int]:
        if "/" not in cidr:
            raise ValueError("CIDR must be in the form 'a.b.c.d/prefix'.")
        ip_part, prefix_part = cidr.split("/", 1)
        ip_part = ip_part.strip()
        prefix_part = prefix_part.strip()

        if not is_valid_ipv4(ip_part):
            raise ValueError("Destination is not a valid IPv4 address.")

        if not prefix_part.isdigit():
            raise ValueError("Prefix must be a number between 0 and 32.")

        prefix = int(prefix_part)
        if not (0 <= prefix <= 32):
            raise ValueError("Prefix must be between 0 and 32.")

        # Align IP to network boundary
        ip_int = ip_to_int(ip_part)
        mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF if prefix > 0 else 0
        network_int = ip_int & mask
        network_ip = int_to_ip(network_int)

        return network_ip, prefix

    def best_route_for(self, dest_ip: str) -> Tuple[Optional[Route], List[Route]]:
        """
        Returns (best_route, all_matching_routes)

        best_route: route chosen using longest prefix match, then lowest metric.
        all_matching_routes: routes that matched the destination at all.
        """
        if not is_valid_ipv4(dest_ip):
            raise ValueError("Destination IP is not a valid IPv4 address.")

        matching = [r for r in self.routes if r.matches(dest_ip)]

        if not matching:
            return None, []

        # Longest prefix first, then lowest metric
        matching.sort(key=lambda r: (-r.prefix, r.metric))
        best = matching[0]
        return best, matching


# ------------- interactive helpers -------------


def print_menu():
    print("=== Task CN29 : Routing Table & Longest Prefix Match Simulator ===")
    print("1) Show routing table")
    print("2) Add route")
    print("3) Delete route")
    print("4) Test packet (destination IP)")
    print("5) Exit")
def handle_add_route(rt: RoutingTable):
    print("\nAdd new route")
    print("-------------")
    cidr = input("Destination network (CIDR, e.g. 192.168.1.0/24 or 0.0.0.0/0): ").strip()
    next_hop = input("Next hop IP (or 'direct'): ").strip()
    iface = input("Outgoing interface name (e.g. eth0): ").strip()
    metric_raw = input("Metric (integer, lower is preferred): ").strip()
    desc = input("Optional description: ").strip()

    if not metric_raw.isdigit():
        print("Metric must be a non-negative integer.\n")
        return

    metric = int(metric_raw)
    try:
        rt.add_route(cidr, next_hop or "direct", iface or "-", metric, desc)
        print("Route added.\n")
    except ValueError as e:
        print(f"Error adding route: {e}\n")


def handle_delete_route(rt: RoutingTable):
    print("\nDelete route")
    print("------------")
    idx_raw = input("Enter route index to delete: ").strip()
    if not idx_raw.isdigit():
        print("Index must be an integer.\n")
        return
    idx = int(idx_raw)
    if rt.delete_route(idx):
        print("Route deleted.\n")
    else:
        print("No route with that index.\n")


def handle_test_packet(rt: RoutingTable):
    print("\nTest packet")
    print("-----------")
    dest_ip = input("Enter destination IP address: ").strip()

    if not is_valid_ipv4(dest_ip):
        print("Not a valid IPv4 address.\n")
        return

    try:
        best, matches = rt.best_route_for(dest_ip)
    except ValueError as e:
        print(f"Error: {e}\n")
        return

    print(f"\nRouting decision for destination {dest_ip}")
    print("-----------------------------------------")

    if not matches:
        print("No matching route found in table.")
        print("Result: packet would be DROPPED (no route / no default route).\n")
        return

    print("Matching routes (before best-route selection):")
    print(
        f"{'Destination':<18} {'Prefix':<6} {'Next hop':<15} "
        f"{'Iface':<8} {'Metric':<6} Description"
    )
    print("-" * 80)
    for r in matches:
        print(
            f"{r.destination + '/' + str(r.prefix):<18} {r.prefix:<6} "
            f"{r.next_hop:<15} {r.interface:<8} {r.metric:<6} {r.description}"
        )

    print("\nBest route (longest prefix, then lowest metric):")
    print(f"  Destination : {best.network_cidr()}")
    print(f"  Next hop    : {best.next_hop}")
    print(f"  Interface   : {best.interface}")
    print(f"  Metric      : {best.metric}")
    if best.description:
        print(f"  Description : {best.description}")
    print("\nResult: packet will be forwarded according to the best route.\n")


def preload_demo_routes(rt: RoutingTable):
    """
    Optionally pre-load a few demo routes to make the table interesting.
    """
    try:
        rt.add_route("192.168.1.0/24", "direct", "eth0", 10, "LAN 1")
        rt.add_route("192.168.0.0/16", "192.168.1.1", "eth0", 20, "Aggregate internal LAN")
        rt.add_route("10.0.0.0/8", "10.0.0.1", "eth1", 10, "Private network")
        rt.add_route("0.0.0.0/0", "203.0.113.1", "wan0", 100, "Default route to ISP")
    except Exception:
        pass

def main():
    rt = RoutingTable()
    preload_demo_routes(rt)
    while True:
        print_menu()
        choice = input("Choose an option (1–5): ").strip()
        if choice == "1":
            rt.list_routes()
        elif choice == "2":
            handle_add_route(rt)
        elif choice == "3":
            handle_delete_route(rt)
        elif choice == "4":
            handle_test_packet(rt)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1–5.\n")

# program entry point
if __name__ == "__main__":
    main()
