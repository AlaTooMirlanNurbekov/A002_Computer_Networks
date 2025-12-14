"""
Task CN38 : Link aggregation (LACP) simulator (concept-level)

Description: **Link Aggregation** (EtherChannel / Port-Channel),
and introduces the main ideas behind **LACP (IEEE 802.3ad)**:

- Multiple physical links can be bundled into one logical link
- The bundle increases bandwidth and provides redundancy
- Traffic is load-balanced using a hashing algorithm (very simplified here)
- If one physical link fails, traffic continues using remaining links

This simulator lets you:
- Create an LACP bundle (Port-Channel) between two switches
- Add/remove member links
- Mark links up/down
- "Send flows" and see which physical link each flow uses
- See how traffic shifts when a link fails

Concept: real switches do not split a *single* flow across multiple links randomly.
They use a hash based on source/destination MAC/IP/ports so that each flow
stays on one physical link (to avoid reordering), but many flows are spread
across members.

This simulator uses a simple stable hash:
  hash(src + dst + sport + dport) % active_links
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import hashlib

@dataclass
class PhysicalLink:
    name: str
    up: bool = True

@dataclass
class Flow:
    src: str
    dst: str
    src_port: int
    dst_port: int

    def flow_id(self) -> str:
        return f"{self.src}-{self.dst}-{self.src_port}-{self.dst_port}"

class LacpBundle:
    """
    Represents one Port-Channel (logical link) with member physical links.
    """
    def __init__(self, bundle_name: str):
        self.bundle_name = bundle_name
        self.links: Dict[str, PhysicalLink] = {}

    def add_link(self, link_name: str):
        if link_name in self.links:
            print(f"[Bundle] Link {link_name} already exists.")
            return
        self.links[link_name] = PhysicalLink(link_name, up=True)
        print(f"[Bundle] Added link {link_name} to {self.bundle_name}")

    def remove_link(self, link_name: str):
        if link_name not in self.links:
            print(f"[Bundle] Link {link_name} not found.")
            return
        del self.links[link_name]
        print(f"[Bundle] Removed link {link_name} from {self.bundle_name}")
    def set_link_state(self, link_name: str, up: bool):
        if link_name not in self.links:
            print(f"[Bundle] Link {link_name} not found.")
            return
        self.links[link_name].up = up
        state = "UP" if up else "DOWN"
        print(f"[Bundle] Link {link_name} is now {state}")

    def active_links(self) -> List[str]:
        return [name for name, l in self.links.items() if l.up]

    def choose_link_for_flow(self, flow: Flow) -> Tuple[bool, str]:
        """
        Returns (success, chosen_link_name).
        If no active links, success=False.
        """
        active = self.active_links()
        if not active:
            return False, "(no active links)"

        # stable hash of flow_id
        h = hashlib.sha256(flow.flow_id().encode("utf-8")).hexdigest()
        value = int(h, 16)
        idx = value % len(active)
        return True, active[idx]

    def show_status(self):
        print(f"\nBundle: {self.bundle_name}")
        print("-" * (8 + len(self.bundle_name)))
        if not self.links:
            print("(no member links)\n")
            return

        print(f"{'Link':<10} State")
        print("-" * 20)
        for name in sorted(self.links.keys()):
            st = "UP" if self.links[name].up else "DOWN"
            print(f"{name:<10} {st}")
        print()

        active = self.active_links()
        print(f"Active member links: {len(active)} → {active if active else 'none'}\n")

def print_menu():
    print("=== Task CN38 : Link Aggregation (LACP) Simulator ===")
    print("1) Show bundle status")
    print("2) Add member link")
    print("3) Remove member link")
    print("4) Set link UP/DOWN")
    print("5) Send a flow (see which link is chosen)")
    print("6) Send multiple demo flows")
    print("7) Exit")

def handle_send_flow(bundle: LacpBundle):
    print("\nSend flow")
    print("---------")
    src = input("Source (MAC/IP text): ").strip()
    dst = input("Destination (MAC/IP text): ").strip()
    sp = input("Source port (number): ").strip()
    dp = input("Destination port (number): ").strip()
    if not (sp.isdigit() and dp.isdigit()):
        print("Ports must be numeric.\n")
        return

    flow = Flow(src, dst, int(sp), int(dp))
    ok, link = bundle.choose_link_for_flow(flow)
    if ok:
        print(f"Flow {flow.flow_id()} → forwarded on member link: {link}\n")
    else:
        print("No active member links → flow dropped ❌\n")

def handle_demo_flows(bundle: LacpBundle):
    print("\nDemo flows")
    print("----------")
    demo = [
        Flow("PC1", "ServerA", 50001, 80),
        Flow("PC2", "ServerA", 50002, 80),
        Flow("PC3", "ServerB", 50100, 443),
        Flow("PC4", "ServerB", 50101, 443),
        Flow("PC5", "ServerC", 51000, 53),
        Flow("PC6", "ServerC", 51001, 53),
    ]
    if not bundle.active_links():
        print("No active links. Bring at least one member UP.\n")
        return

    for f in demo:
        ok, link = bundle.choose_link_for_flow(f)
        print(f"  {f.flow_id():<28} → {link}")
    print("\nTip: bring one link DOWN and run again to see redistribution.\n")

def main():
    #create a bundle with a few default member links
    bundle = LacpBundle("Port-Channel1")
    bundle.add_link("Gi0/1")
    bundle.add_link("Gi0/2")

    while True:
        print_menu()
        choice = input("Choose option (1–7): ").strip()
        if choice == "1":
            bundle.show_status()
        elif choice == "2":
            name = input("Member link name (e.g., Gi0/3): ").strip()
            if name:
                bundle.add_link(name)
            print()
        elif choice == "3":
            name = input("Member link name to remove: ").strip()
            if name:
                bundle.remove_link(name)
            print()
        elif choice == "4":
            name = input("Member link name: ").strip()
            state = input("State (up/down): ").strip().lower()
            if state not in ("up", "down"):
                print("State must be 'up' or 'down'.\n")
                continue
            bundle.set_link_state(name, up=(state == "up"))
            print()
        elif choice == "5":
            handle_send_flow(bundle)
        elif choice == "6":
            handle_demo_flows(bundle)
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")

# program entry point
if __name__ == "__main__":
    main()
