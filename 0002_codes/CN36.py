"""
Task CN36 : Spanning tree protocol (STP) simulator (concept-level)

Description: this task simulates the key ideas of **Spanning Tree Protocol (STP)**:

- Switches exchange BPDUs to prevent Layer 2 loops
- The switch with the lowest Bridge ID becomes the Root Bridge
- Each non-root switch chooses:
    * One Root Port (best path to root)
    * One Designated Port per segment (best switch on that segment)
    * Other ports become Blocked to break loops

This is a teaching simulator:
- It does NOT implement full IEEE timers/state machines
- It focuses on the decision logic:
    Root Bridge election + port roles + loop removal

You can:
- Create a small topology of switches and links
- Run STP calculation
- See which ports forward and which are blocked

Concept explained:
STP creates a loop-free tree from a potentially looped topology by
blocking redundant links while keeping full connectivity.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

@dataclass
class Switch:
    name: str
    bridge_id: int  # lower is better (priority + MAC concept simplified)

@dataclass
class Link:
    """
    Represents a bidirectional link between two switches.
    Each side has a port label.
    """
    sw1: str
    port1: str
    sw2: str
    port2: str
    cost: int  # path cost (lower is better)

@dataclass
class PortRole:
    role: str  # "ROOT", "DESIGNATED", "BLOCKED"
    forwarding: bool

class STPSimulator:
    def __init__(self):
        self.switches: Dict[str, Switch] = {}
        self.links: List[Link] = []

        # Results: switch_name, port_label -> PortRole
        self.port_roles: Dict[Tuple[str, str], PortRole] = {}

        self.root_bridge: Optional[str] = None

    def add_switch(self, name: str, bridge_id: int):
        if name in self.switches:
            raise ValueError("Switch already exists.")
        self.switches[name] = Switch(name, bridge_id)

    def add_link(self, sw1: str, port1: str, sw2: str, port2: str, cost: int):
        if sw1 not in self.switches or sw2 not in self.switches:
            raise ValueError("Both switches must exist before linking.")
        self.links.append(Link(sw1, port1, sw2, port2, cost))

    def elect_root_bridge(self) -> str:
        root = min(self.switches.values(), key=lambda s: s.bridge_id)
        self.root_bridge = root.name
        return root.name

    def build_adjacency(self) -> Dict[str, List[Tuple[str, str, str, int]]]:
        """
        adjacency[switch] = list of (neighbor_switch, local_port, neighbor_port, cost)
        """
        adj: Dict[str, List[Tuple[str, str, str, int]]] = {sw: [] for sw in self.switches}
        for link in self.links:
            adj[link.sw1].append((link.sw2, link.port1, link.port2, link.cost))
            adj[link.sw2].append((link.sw1, link.port2, link.port1, link.cost))
        return adj

    def shortest_path_cost_to_root(self, adj, start: str, root: str) -> Tuple[int, Optional[Tuple[str, str]]]:
        """
        Dijkstra-like shortest path to root.
        Returns:
          (best_cost, first_hop_info)
        first_hop_info is (local_port, next_switch) from 'start' toward root.
        """
        visited = set()
        dist: Dict[str, int] = {sw: 10**9 for sw in self.switches}
        prev: Dict[str, Optional[str]] = {sw: None for sw in self.switches}

        dist[start] = 0

        while True:
            # pick unvisited with smallest dist
            current = None
            current_dist = 10**9
            for sw, d in dist.items():
                if sw not in visited and d < current_dist:
                    current = sw
                    current_dist = d

            if current is None:
                break
            if current == root:
                break

            visited.add(current)

            for neigh, _, _, cost in adj[current]:
                if neigh in visited:
                    continue
                nd = dist[current] + cost
                if nd < dist[neigh]:
                    dist[neigh] = nd
                    prev[neigh] = current

        if dist[root] >= 10**9:
            return 10**9, None

        # To determine root port, walk from root back to start
        # We want the next hop from start on the best path.
        path = []
        cur = root
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        # path is root -> ... -> start (reverse direction)
        if start not in path:
            return 10**9, None

        # Find neighbor after start towards root: path is [root, ..., start]
        idx = path.index(start)
        if idx == 0:
            # start is root
            return 0, None
        next_switch = path[idx - 1]  # one step toward root

        # Find the local port on 'start' that connects to next_switch
        for neigh, local_port, _, _ in adj[start]:
            if neigh == next_switch:
                return dist[root], (local_port, next_switch)

        return dist[root], None

    def calculate(self):
        if not self.switches:
            raise ValueError("No switches in topology.")

        root = self.elect_root_bridge()
        adj = self.build_adjacency()

        # Initialize all ports as DESIGNATED forwarding
        self.port_roles.clear()
        for link in self.links:
            self.port_roles[(link.sw1, link.port1)] = PortRole("DESIGNATED", True)
            self.port_roles[(link.sw2, link.port2)] = PortRole("DESIGNATED", True)

        # 1) Root bridge: all its ports are DESIGNATED forwarding

        # 2) Non-root switches: pick root port (best path cost)
        root_ports: Dict[str, Tuple[str, int]] = {}  # sw -> (port, cost_to_root)

        for sw in self.switches:
            if sw == root:
                continue
            cost, hop = self.shortest_path_cost_to_root(adj, sw, root)
            if hop is None:
                continue
            local_port, _ = hop
            root_ports[sw] = (local_port, cost)
            self.port_roles[(sw, local_port)] = PortRole("ROOT", True)

        # 3) For each link segment: choose designated port based on best path to root
        # If tie then lower bridge_id wins 
        for link in self.links:
            a = link.sw1
            b = link.sw2

            #Root path cost from each switch
            cost_a = 0 if a == root else root_ports.get(a, (None, 10**9))[1]
            cost_b = 0 if b == root else root_ports.get(b, (None, 10**9))[1]

            # Switch with better (lower) cost becomes designated on this segment
            if cost_a < cost_b:
                designated_sw = a
            elif cost_b < cost_a:
                designated_sw = b
            else:
                # tie → lower bridge_id wins
                designated_sw = a if self.switches[a].bridge_id < self.switches[b].bridge_id else b

            #other side may become blocked if it is neither root port nor designated
            if designated_sw == a:
                self.port_roles[(a, link.port1)] = PortRole("DESIGNATED", True)
                # if b port isn't root port, block it
                if not (b in root_ports and root_ports[b][0] == link.port2):
                    self.port_roles[(b, link.port2)] = PortRole("BLOCKED", False)
            else:
                self.port_roles[(b, link.port2)] = PortRole("DESIGNATED", True)
                if not (a in root_ports and root_ports[a][0] == link.port1):
                    self.port_roles[(a, link.port1)] = PortRole("BLOCKED", False)

        return root

#displaying helpers
    def show_topology(self):
        print("\nTopology")
        print("--------")
        print("Switches:")
        for sw in sorted(self.switches.values(), key=lambda s: s.bridge_id):
            print(f"  {sw.name} (bridge_id={sw.bridge_id})")
        print("\nLinks:")
        for l in self.links:
            print(f"  {l.sw1}:{l.port1} --cost {l.cost}-- {l.sw2}:{l.port2}")
        print()

    def show_results(self):
        if self.root_bridge is None:
            print("\nSTP not calculated yet.\n")
            return

        print("\nSTP Results")
        print("-----------")
        print(f"Root Bridge: {self.root_bridge}")
        print("\nPort roles:")
        print(f"{'Switch':<8} {'Port':<8} {'Role':<12} Forwarding")
        print("-" * 42)

        items = sorted(self.port_roles.items(), key=lambda x: (x[0][0], x[0][1]))
        for (sw, port), role in items:
            print(f"{sw:<8} {port:<8} {role.role:<12} {str(role.forwarding)}")
        print()

def print_menu():
    print("=== Task CN36 : STP Simulator (concept) ===")
    print("1) Show topology")
    print("2) Run STP calculation")
    print("3) Show STP results")
    print("4) Exit")


def main():
    stp = STPSimulator()
    # Demo topology (triangle loop):
    # S1 -- S2
    #  \    /
    #    S3
    #
    # Bridge IDs decide root (lower wins).
    stp.add_switch("S1", 32768)
    stp.add_switch("S2", 32769)
    stp.add_switch("S3", 32770)

    stp.add_link("S1", "P1", "S2", "P1", cost=4)
    stp.add_link("S2", "P2", "S3", "P1", cost=4)
    stp.add_link("S1", "P2", "S3", "P2", cost=4)

    while True:
        print_menu()
        choice = input("Choose option (1–4): ").strip()
        if choice == "1":
            stp.show_topology()
        elif choice == "2":
            root = stp.calculate()
            print(f"\nSTP calculated. Root Bridge is {root}.\n")
        elif choice == "3":
            stp.show_results()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")

# program entry point
if __name__ == "__main__":
    main()
