"""
Task CN39 : Broadcast storm & storm control simulator

Description: the code is for simulating a *broadcast storm** in a Layer 2 network and shows how
**storm control** can protect a switch.

You can:
- Define a small L2 network of switches with links (optionally with a loop)
- Choose a starting switch and inject a broadcast frame
- See how broadcasts propagate (flooding)
- Observe how a loop causes repeated flooding → storm growth
- Enable storm control (broadcast rate limit per port) and see how it stops the storm

Concept explained:
- Broadcast frames (destination ff:ff:ff:ff:ff:ff) are flooded by switches
- If the topology contains a loop and STP is not blocking, broadcasts can circulate
- This may consume bandwidth/CPU and cause network outage
- Storm control limits the broadcast rate to reduce damage

This simulator is concept-level and uses "steps" instead of real time.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional

BROADCAST_MAC = "ff:ff:ff:ff:ff:ff"

@dataclass
class PortStormControl:
    enabled: bool = False
    limit_per_step: int = 10  # max broadcast frames allowed per step
    dropped_this_step: int = 0
    passed_this_step: int = 0

@dataclass
class SwitchNode:
    name: str
    ports: Dict[str, PortStormControl] = field(default_factory=dict)

@dataclass
class Link:
    a: str
    a_port: str
    b: str
    b_port: str

@dataclass
class BroadcastFrame:
    frame_id: int
    origin: str

class StormNetwork:
    def __init__(self):
        self.switches: Dict[str, SwitchNode] = {}
        self.links: List[Link] = []
        self.frame_counter = 0

    def add_switch(self, name: str, port_names: List[str]):
        self.switches[name] = SwitchNode(
            name=name,
            ports={p: PortStormControl() for p in port_names}
        )

    def add_link(self, a: str, a_port: str, b: str, b_port: str):
        if a not in self.switches or b not in self.switches:
            raise ValueError("Both switches must exist.")
        if a_port not in self.switches[a].ports or b_port not in self.switches[b].ports:
            raise ValueError("Ports must exist on both switches.")
        self.links.append(Link(a, a_port, b, b_port))

    def enable_storm_control(self, sw: str, port: str, limit_per_step: int):
        self._check_sw_port(sw, port)
        cfg = self.switches[sw].ports[port]
        cfg.enabled = True
        cfg.limit_per_step = limit_per_step

    def disable_storm_control(self, sw: str, port: str):
        self._check_sw_port(sw, port)
        cfg = self.switches[sw].ports[port]
        cfg.enabled = False

    def neighbors(self, sw: str, port: str) -> Optional[Tuple[str, str]]:
        """Return (neighbor_switch, neighbor_port) for a given switch port if linked."""
        for l in self.links:
            if l.a == sw and l.a_port == port:
                return (l.b, l.b_port)
            if l.b == sw and l.b_port == port:
                return (l.a, l.a_port)
        return None
    def reset_step_counters(self):
        for s in self.switches.values():
            for p in s.ports.values():
                p.dropped_this_step = 0
                p.passed_this_step = 0

    def inject_broadcast(self, start_switch: str, steps: int = 5, max_total_frames: int = 1000):
        """
        Simulate broadcast flooding for a number of steps.
        If there is a loop, frames can keep circulating.
        We track frames by "frame_id" but for storm behavior we allow re-flooding,
        because in real loops broadcasts can be seen repeatedly on different ports.
        """
        if start_switch not in self.switches:
            raise ValueError("Start switch does not exist.")

        print("\n=== Broadcast Storm Simulation ===")
        print(f"Start switch : {start_switch}")
        print(f"Steps        : {steps}")
        print(f"Storm control: {'enabled on some ports' if self._any_storm_control() else 'OFF'}\n")

        #queue holds tuples (switch, ingress_port, frame)
        queue: List[Tuple[str, Optional[str], BroadcastFrame]] = []

        self.frame_counter += 1
        first = BroadcastFrame(frame_id=self.frame_counter, origin=start_switch)
        queue.append((start_switch, None, first))

        total_processed = 0

        for step in range(1, steps + 1):
            if not queue:
                print(f"Step {step}: no frames in queue → storm ended.\n")
                return

            if total_processed >= max_total_frames:
                print("Reached max frame limit → stopping to avoid infinite storm.\n")
                return

            self.reset_step_counters()

            print(f"--- Step {step} ---")
            next_queue: List[Tuple[str, Optional[str], BroadcastFrame]] = []

            while queue:
                sw, ingress_port, frame = queue.pop(0)
                total_processed += 1
                if total_processed >= max_total_frames:
                    break

                #flood out all ports except ingress
                for port_name, scfg in self.switches[sw].ports.items():
                    if ingress_port is not None and port_name == ingress_port:
                        continue

                    # Storm control check
                    if scfg.enabled:
                        if scfg.passed_this_step >= scfg.limit_per_step:
                            scfg.dropped_this_step += 1
                            continue

                    # Send to neighbor if exists
                    neigh = self.neighbors(sw, port_name)
                    if neigh is None:
                        # no link drops off the network
                        if scfg.enabled:
                            scfg.passed_this_step += 1
                        continue

                    neigh_sw, neigh_port = neigh
                    if scfg.enabled:
                        scfg.passed_this_step += 1

                    # each forwarding creates a "new broadcast instance"
                    self.frame_counter += 1
                    new_frame = BroadcastFrame(frame_id=self.frame_counter, origin=frame.origin)
                    next_queue.append((neigh_sw, neigh_port, new_frame))

            self._print_port_stats()
            print(f"Frames queued for next step: {len(next_queue)}\n")
            queue = next_queue

        print("Simulation finished.\n")
    def _any_storm_control(self) -> bool:
        for s in self.switches.values():
            for p in s.ports.values():
                if p.enabled:
                    return True
        return False

    def _print_port_stats(self):
        print("Port stats (storm control)")
        print("-------------------------")
        for sw in sorted(self.switches.keys()):
            for port, cfg in self.switches[sw].ports.items():
                if cfg.enabled:
                    print(
                        f"{sw}:{port}  limit={cfg.limit_per_step:<4} "
                        f"passed={cfg.passed_this_step:<4} dropped={cfg.dropped_this_step}"
                    )

    def show_topology(self):
        print("\nTopology")
        print("--------")
        for l in self.links:
            print(f"{l.a}:{l.a_port} <--> {l.b}:{l.b_port}")
        print()

    def _check_sw_port(self, sw: str, port: str):
        if sw not in self.switches:
            raise ValueError("Switch does not exist.")
        if port not in self.switches[sw].ports:
            raise ValueError("Port does not exist.")

def print_menu():
    print("=== Task CN39 : Broadcast Storm & Storm Control Simulator ===")
    print("1) Show topology")
    print("2) Enable storm control on port")
    print("3) Disable storm control on port")
    print("4) Run broadcast simulation")
    print("5) Exit")

def main():
    net = StormNetwork()

    # Demo network with a loop (triangle):
    # S1--S2
    #  \  /
    #   S3
    net.add_switch("S1", ["P1", "P2"])
    net.add_switch("S2", ["P1", "P2"])
    net.add_switch("S3", ["P1", "P2"])

    net.add_link("S1", "P1", "S2", "P1")
    net.add_link("S2", "P2", "S3", "P1")
    net.add_link("S3", "P2", "S1", "P2")

    while True:
        print_menu()
        choice = input("Choose option (1–5): ").strip()

        if choice == "1":
            net.show_topology()
        elif choice == "2":
            sw = input("Switch name: ").strip()
            port = input("Port name: ").strip()
            lim_raw = input("Limit per step (e.g., 5): ").strip()
            if not lim_raw.isdigit():
                print("Limit must be numeric.\n")
                continue
            try:
                net.enable_storm_control(sw, port, int(lim_raw))
                print("Storm control enabled.\n")
            except ValueError as e:
                print(f"Error: {e}\n")
        elif choice == "3":
            sw = input("Switch name: ").strip()
            port = input("Port name: ").strip()
            try:
                net.disable_storm_control(sw, port)
                print("Storm control disabled.\n")
            except ValueError as e:
                print(f"Error: {e}\n")
        elif choice == "4":
            start = input("Start switch (e.g., S1): ").strip()
            steps_raw = input("Steps to simulate (default 5): ").strip()
            steps = int(steps_raw) if steps_raw.isdigit() else 5
            net.inject_broadcast(start_switch=start, steps=steps, max_total_frames=1000)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")

# program entry point
if __name__ == "__main__":
    main()
