"""
Task CN26 : firewall rule simulator

Description:
This task simulates a very simple firewall with ordered rules.

You can:
- Add rules with:
    * action   : ALLOW or DENY
    * direction: in / out / any
    * protocol : tcp / udp / any
    * src IP   : single IP (e.g. 192.168.1.10), subnet (192.168.1.0/24), or 'any'
    * dst IP   : same as src
    * src port : number (80), range (1000-2000), or 'any'
    * dst port : same as src port
- List all rules (top → bottom)
- Test “packets” against the rules to see ALLOW/DENY and which rule matched

Concept explained:
Real firewalls usually:
- Check rules from top to bottom
- Use “first match wins”
- Apply a default policy (often “deny all” at the end)

This simulator copies that logic in a simplified way.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Literal

try:
    # Reuse existing validator from previous tasks if available
    from CN10 import is_valid_ipv4  # type: ignore
except ImportError:
    # Fallback simple validator (no advanced checks)
    def is_valid_ipv4(ip: str) -> bool:
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        try:
            nums = [int(p) for p in parts]
        except ValueError:
            return False
        return all(0 <= n <= 255 for n in nums)


# ---------- helpers for IP and port matching ----------


def ip_to_int(ip: str) -> int:
    parts = [int(p) for p in ip.split(".")]
    value = 0
    for p in parts:
        value = (value << 8) | p
    return value


@dataclass
class IpPattern:
    """Represents a source/destination IP pattern: 'any', single IP, or subnet."""

    kind: Literal["any", "single", "subnet"]
    ip_int: Optional[int] = None
    network_int: Optional[int] = None
    prefix: Optional[int] = None

    def matches(self, ip: str) -> bool:
        if self.kind == "any":
            return True

        if not is_valid_ipv4(ip):
            return False

        ip_int = ip_to_int(ip)

        if self.kind == "single":
            return ip_int == self.ip_int

        if self.kind == "subnet":
            assert self.network_int is not None and self.prefix is not None
            mask = (0xFFFFFFFF << (32 - self.prefix)) & 0xFFFFFFFF
            return (ip_int & mask) == self.network_int

        return False


def parse_ip_pattern(text: str) -> IpPattern:
    text = text.strip().lower()
    if text in ("any", "*"):
        return IpPattern(kind="any")

    # subnet form: a.b.c.d/prefix
    if "/" in text:
        ip_part, prefix_part = text.split("/", 1)
        ip_part = ip_part.strip()
        prefix_part = prefix_part.strip()
        if not (is_valid_ipv4(ip_part) and prefix_part.isdigit()):
            raise ValueError("Invalid subnet pattern.")
        prefix = int(prefix_part)
        if not (0 <= prefix <= 32):
            raise ValueError("Prefix length must be 0–32.")
        ip_int = ip_to_int(ip_part)
        mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF if prefix > 0 else 0
        network_int = ip_int & mask
        return IpPattern(kind="subnet", network_int=network_int, prefix=prefix)

    # single IP
    if not is_valid_ipv4(text):
        raise ValueError("Invalid IP address pattern.")
    return IpPattern(kind="single", ip_int=ip_to_int(text))


@dataclass
class PortPattern:
    """Represents a source/destination port pattern: 'any', single, or range."""

    kind: Literal["any", "single", "range"]
    port: Optional[int] = None
    start: Optional[int] = None
    end: Optional[int] = None

    def matches(self, port: int) -> bool:
        if self.kind == "any":
            return True

        if not (0 <= port <= 65535):
            return False

        if self.kind == "single":
            return port == self.port

        if self.kind == "range":
            assert self.start is not None and self.end is not None
            return self.start <= port <= self.end

        return False


def parse_port_pattern(text: str) -> PortPattern:
    text = text.strip().lower()
    if text in ("any", "*"):
        return PortPattern(kind="any")

    if "-" in text:
        start_s, end_s = text.split("-", 1)
        if not (start_s.isdigit() and end_s.isdigit()):
            raise ValueError("Port range must use digits, e.g. 1000-2000.")
        start = int(start_s)
        end = int(end_s)
        if not (0 <= start <= 65535 and 0 <= end <= 65535 and start <= end):
            raise ValueError("Invalid port range.")
        return PortPattern(kind="range", start=start, end=end)

    if not text.isdigit():
        raise ValueError("Port must be a number, range, or 'any'.")
    p = int(text)
    if not (0 <= p <= 65535):
        raise ValueError("Port must be between 0 and 65535.")
    return PortPattern(kind="single", port=p)


# ---------- firewall rule model ----------


@dataclass
class FirewallRule:
    index: int  # rule order
    action: Literal["allow", "deny"]
    direction: Literal["in", "out", "any"]
    protocol: Literal["tcp", "udp", "any"]
    src_ip: IpPattern
    dst_ip: IpPattern
    src_port: PortPattern
    dst_port: PortPattern
    comment: str = ""

    def matches_packet(self, direction: str, protocol: str,
                       src_ip: str, dst_ip: str,
                       src_port: int, dst_port: int) -> bool:
        # Direction
        if self.direction != "any" and self.direction != direction:
            return False

        # Protocol
        proto_l = protocol.lower()
        if self.protocol != "any" and self.protocol != proto_l:
            return False

        # IPs
        if not self.src_ip.matches(src_ip):
            return False
        if not self.dst_ip.matches(dst_ip):
            return False

        #ports
        if not self.src_port.matches(src_port):
            return False
        if not self.dst_port.matches(dst_port):
            return False

        return True


class SimpleFirewall:
    def __init__(self):
        self.rules: List[FirewallRule] = []

    def add_rule(self, action: str, direction: str, protocol: str,
                 src_ip_pattern: str, dst_ip_pattern: str,
                 src_port_pattern: str, dst_port_pattern: str,
                 comment: str = "") -> None:
        action_l = action.strip().lower()
        direction_l = direction.strip().lower()
        protocol_l = protocol.strip().lower()

        if action_l not in ("allow", "deny"):
            raise ValueError("Action must be 'allow' or 'deny'.")
        if direction_l not in ("in", "out", "any"):
            raise ValueError("Direction must be 'in', 'out', or 'any'.")
        if protocol_l not in ("tcp", "udp", "any"):
            raise ValueError("Protocol must be 'tcp', 'udp', or 'any'.")

        src_ip = parse_ip_pattern(src_ip_pattern)
        dst_ip = parse_ip_pattern(dst_ip_pattern)
        src_port = parse_port_pattern(src_port_pattern)
        dst_port = parse_port_pattern(dst_port_pattern)

        rule = FirewallRule(
            index=len(self.rules),
            action=action_l, direction=direction_l, protocol=protocol_l,
            src_ip=src_ip, dst_ip=dst_ip,
            src_port=src_port, dst_port=dst_port,
            comment=comment,
        )
        self.rules.append(rule)

    def clear_rules(self) -> None:
        self.rules.clear()

    def list_rules(self) -> None:
        if not self.rules:
            print("\n(No rules configured.)\n")
            return

        print("\nCurrent firewall rules (top → bottom):")
        print("--------------------------------------")
        for r in self.rules:
            print(f"[{r.index}] {r.action.upper()} dir={r.direction}, proto={r.protocol}, "
                  f"src_ip={_ip_pattern_to_str(r.src_ip)}, dst_ip={_ip_pattern_to_str(r.dst_ip)}, "
                  f"src_port={_port_pattern_to_str(r.src_port)}, dst_port={_port_pattern_to_str(r.dst_port)}")
            if r.comment:
                print(f"      comment: {r.comment}")
        print()

    def check_packet(self, direction: str, protocol: str,
                     src_ip: str, dst_ip: str,
                     src_port: int, dst_port: int):
        direction_l = direction.strip().lower()
        protocol_l = protocol.strip().lower()

        for r in self.rules:
            if r.matches_packet(direction_l, protocol_l, src_ip, dst_ip, src_port, dst_port):
                return r.action, r
        #default policy: deny if no rule matched
        return "deny", None


def _ip_pattern_to_str(p: IpPattern) -> str:
    if p.kind == "any":
        return "any"
    if p.kind == "single":
        return f"{(p.ip_int >> 24) & 0xFF}.{(p.ip_int >> 16) & 0xFF}.{(p.ip_int >> 8) & 0xFF}.{p.ip_int & 0xFF}"
    if p.kind == "subnet":
        ip_int = p.network_int or 0
        return f"{(ip_int >> 24) & 0xFF}.{(ip_int >> 16) & 0xFF}.{(ip_int >> 8) & 0xFF}.{ip_int & 0xFF}/{p.prefix}"
    return "?"


def _port_pattern_to_str(p: PortPattern) -> str:
    if p.kind == "any":
        return "any"
    if p.kind == "single":
        return str(p.port)
    if p.kind == "range":
        return f"{p.start}-{p.end}"
    return "?"


# ---------- interactive CLI ----------

def print_menu():
    print("=== Task CN26 : Simple Firewall Rule Simulator ===")
    print("1) List rules")
    print("2) Add rule")
    print("3) Clear all rules")
    print("4) Test a packet")
    print("5) Exit")


def handle_add_rule(fw: SimpleFirewall):
    print("\nAdd new rule")
    print("------------")
    action = input("Action (allow/deny): ").strip()
    direction = input("Direction (in/out/any): ").strip()
    protocol = input("Protocol (tcp/udp/any): ").strip()

    src_ip = input("Source IP (single, subnet, or 'any'): ").strip()
    dst_ip = input("Destination IP (single, subnet, or 'any'): ").strip()

    src_port = input("Source port (number, range like 1000-2000, or 'any'): ").strip()
    dst_port = input("Destination port (number, range, or 'any'): ").strip()

    comment = input("Optional comment/description: ").strip()

    try:
        fw.add_rule(action, direction, protocol, src_ip, dst_ip, src_port, dst_port, comment)
        print("Rule added.\n")
    except ValueError as e:
        print(f"Error adding rule: {e}\n")


def handle_test_packet(fw: SimpleFirewall):
    print("\nTest a packet")
    print("-------------")
    direction = input("Direction (in/out): ").strip()
    protocol = input("Protocol (tcp/udp): ").strip().lower()

    src_ip = input("Source IP: ").strip()
    dst_ip = input("Destination IP: ").strip()

    src_p_raw = input("Source port: ").strip()
    dst_p_raw = input("Destination port: ").strip()

    if not (src_p_raw.isdigit() and dst_p_raw.isdigit()):
        print("Ports must be numeric.\n")
        return

    src_port = int(src_p_raw)
    dst_port = int(dst_p_raw)

    if not is_valid_ipv4(src_ip) or not is_valid_ipv4(dst_ip):
        print("Invalid IP address format.\n")
        return

    action, rule = fw.check_packet(direction, protocol, src_ip, dst_ip, src_port, dst_port)

    print("\nResult")
    print("------")
    print(f"Packet: dir={direction}, proto={protocol}, "
          f"{src_ip}:{src_port} → {dst_ip}:{dst_port}")
    if rule is not None:
        print(f"Decision : {action.upper()} (matched rule #{rule.index})")
        print(f"Rule     : action={rule.action}, dir={rule.direction}, proto={rule.protocol},")
        print(f"           src_ip={_ip_pattern_to_str(rule.src_ip)}, "
              f"dst_ip={_ip_pattern_to_str(rule.dst_ip)},")
        print(f"           src_port={_port_pattern_to_str(rule.src_port)}, "
              f"dst_port={_port_pattern_to_str(rule.dst_port)}")
        if rule.comment:
            print(f"Comment  : {rule.comment}")
    else:
        print("Decision : DENY (no rule matched, default policy = deny all)")
    print()


def main():
    fw = SimpleFirewall()
    #optional: add a sample rule to make it less empty for the first run
    try:
        fw.add_rule(
            action="allow",
            direction="in",
            protocol="tcp",
            src_ip_pattern="any",
            dst_ip_pattern="192.168.1.0/24",
            src_port_pattern="any",
            dst_port_pattern="80",
            comment="Allow HTTP to local web server subnet",
        )
    except Exception:
        #if something fails we just ignore (only a demo)
        pass
    while True:
        print_menu()
        choice = input("Choose an option (1-5): ").strip()
        if choice == "1":
            fw.list_rules()
        elif choice == "2":
            handle_add_rule(fw)
        elif choice == "3":
            confirm = input("Are you sure you want to clear ALL rules? (y/n): ").strip().lower()
            if confirm in ("y", "yes"):
                fw.clear_rules()
                print("All rules cleared.\n")
            else:
                print("Clear canceled.\n")
        elif choice == "4":
            handle_test_packet(fw)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1–5.\n")

# program entry point
if __name__ == "__main__":
    main()
