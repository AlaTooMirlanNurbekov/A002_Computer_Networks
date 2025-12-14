"""
Task CN32 : ICMP diagnostics simulator (ping + traceroute)

Description: this task simulates how basic ICMP diagnostics work WITHOUT sending real packets.

It includes two modes:
1) PING simulator
   - Sends ICMP Echo Requests to a target
   - Simulates random packet loss and varying latency
   - Calculates packet loss percentage and average RTT
2) TRACEROUTE simulator
   - Simulates how traceroute discovers hops using increasing TTL
   - Each hop responds with ICMP Time Exceeded until the destination is reached
Concept explained:
- Ping uses ICMP Echo Request/Reply to check reachability and RTT.
- Traceroute works by sending packets with TTL=1,2,3... and listening for
  ICMP Time Exceeded from intermediate routers.
"""

from __future__ import annotations
import random
import time
from dataclasses import dataclass
from typing import List, Optional
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

# PING SIMULATION
@dataclass
class PingResult:
    sent: int
    received: int
    rtts_ms: List[float]
    @property
    def loss_percent(self) -> float:
        if self.sent == 0:
            return 0.0
        lost = self.sent - self.received
        return (lost / self.sent) * 100.0

    @property
    def avg_rtt(self) -> Optional[float]:
        if not self.rtts_ms:
            return None
        return sum(self.rtts_ms) / len(self.rtts_ms)

def simulate_ping(target: str, count: int = 4, loss_probability: float = 0.1) -> PingResult:
    """
    Simulate sending ICMP Echo Requests.
    """
    rtts: List[float] = []
    received = 0
    print(f"\nPinging {target} with {count} simulated ICMP Echo Requests:\n")
    for seq in range(1, count + 1):
        print(f"Request {seq} → ", end="")

        #Simulate loss
        if random.random() < loss_probability:
            print("Request timed out ❌")
            continue
        #simulate latency
        rtt = random.uniform(5.0, 120.0)  # ms
        time.sleep(min(rtt / 1000.0, 0.15))  # keep it quick
        print(f"Reply received ✔  time={rtt:.1f}ms")

        rtts.append(rtt)
        received += 1

    return PingResult(sent=count, received=received, rtts_ms=rtts)

def print_ping_summary(target: str, result: PingResult) -> None:
    print("\nPing statistics")
    print("---------------")
    print(f"Target   : {target}")
    print(f"Packets  : Sent = {result.sent}, Received = {result.received}, Lost = {result.sent - result.received}")
    print(f"Loss     : {result.loss_percent:.1f}%")
    if result.avg_rtt is None:
        print("RTT      : No replies received.")
    else:
        print(f"RTT      : Average = {result.avg_rtt:.1f}ms, Min = {min(result.rtts_ms):.1f}ms, Max = {max(result.rtts_ms):.1f}ms")
    print()


# TRACEROUTE SIMULATION
@dataclass
class Hop:
    hop_number: int
    router_ip: str
    rtt_ms: Optional[float]
    reached_destination: bool

def generate_fake_path(destination: str, max_hops: int) -> List[str]:
    """
    Generate a fake route path like:
    192.168.0.1 → 10.0.0.1 → 172.16.5.1 → destination
    """
    hops = []
    #a few private-looking routers first
    private_blocks = [
        "192.168.0.1",
        "10.0.0.1",
        "172.16.5.1",
        "100.64.0.1",
    ]
    # Choose a random length path
    path_length = random.randint(2, min(6, max_hops - 1))

    for i in range(path_length - 1):
        hops.append(private_blocks[i % len(private_blocks)])
    hops.append(destination)
    return hops

def simulate_traceroute(destination: str, max_hops: int = 10, timeout_probability: float = 0.15) -> List[Hop]:
    """
    Simulate traceroute:
    - TTL starts at 1 and increases
    - Each hop returns ICMP Time Exceeded until destination returns Echo Reply/Port Unreachable
    """
    path = generate_fake_path(destination, max_hops)
    results: List[Hop] = []
    print(f"\nTracing route to {destination} over a maximum of {max_hops} hops:\n")
    for ttl in range(1, max_hops + 1):
        if ttl <= len(path):
            router_ip = path[ttl - 1]
        else:
            # after the path ends, pretend nothing responds
            router_ip = "*"
        # Simulate timeout
        if router_ip == "*" or random.random() < timeout_probability:
            results.append(Hop(ttl, "*", None, False))
            print(f"{ttl:2d}   *   Request timed out")
            continue

        rtt = random.uniform(5.0, 180.0)
        time.sleep(min(rtt / 1000.0, 0.15))

        reached = (router_ip == destination)
        results.append(Hop(ttl, router_ip, rtt, reached))

        if reached:
            print(f"{ttl:2d}   {router_ip:<15}  {rtt:6.1f} ms   (destination reached)")
            break
        else:
            print(f"{ttl:2d}   {router_ip:<15}  {rtt:6.1f} ms")

    return results

# INTERACTIVE MENU

def print_menu():
    print("=== Task CN32 : ICMP Diagnostics Simulator (Ping + Traceroute) ===")
    print("1) Simulate ping")
    print("2) Simulate traceroute")
    print("3) Exit")

def handle_ping():
    target = input("\nEnter target IPv4 address: ").strip()
    if not is_valid_ipv4(target):
        print("Invalid IPv4 address.\n")
        return

    count_raw = input("How many requests? (default 4): ").strip()
    if count_raw.isdigit() and int(count_raw) > 0:
        count = int(count_raw)
    else:
        count = 4
    loss_raw = input("Loss probability 0.0–1.0 (default 0.1): ").strip()
    try:
        loss_prob = float(loss_raw) if loss_raw else 0.1
        if not (0.0 <= loss_prob <= 1.0):
            raise ValueError
    except ValueError:
        print("Invalid loss probability; using default 0.1\n")
        loss_prob = 0.1

    result = simulate_ping(target, count=count, loss_probability=loss_prob)
    print_ping_summary(target, result)
def handle_traceroute():
    dest = input("\nEnter destination IPv4 address: ").strip()
    if not is_valid_ipv4(dest):
        print("Invalid IPv4 address.\n")
        return

    hops_raw = input("Max hops (default 10): ").strip()
    if hops_raw.isdigit() and int(hops_raw) > 0:
        max_hops = int(hops_raw)
    else:
        max_hops = 10

    timeout_raw = input("Timeout probability 0.0–1.0 (default 0.15): ").strip()
    try:
        timeout_prob = float(timeout_raw) if timeout_raw else 0.15
        if not (0.0 <= timeout_prob <= 1.0):
            raise ValueError
    except ValueError:
        print("Invalid timeout probability; using default 0.15\n")
        timeout_prob = 0.15

    simulate_traceroute(dest, max_hops=max_hops, timeout_probability=timeout_prob)
    print()
def main():
    while True:
        print_menu()
        choice = input("Choose option (1–3): ").strip()

        if choice == "1":
            handle_ping()
        elif choice == "2":
            handle_traceroute()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")

# program entry point
if __name__ == "__main__":
    main()
