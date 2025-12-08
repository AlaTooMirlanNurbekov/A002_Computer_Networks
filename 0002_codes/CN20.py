"""
Task CN20 : IPv4 host configuration checker

Description:
This task checks if a given host configuration looks correct for a small LAN.

You enter:
- Host IPv4 address
- Subnet mask
- Default gateway address
- (Optional) DNS server address

The program will:
- Validate all IPv4 addresses and the subnet mask
- Check that host IP is not the network or broadcast address
- Check that the default gateway is in the same subnet as the host
- Check that DNS (if provided) is a valid IPv4 address
- Tell you whether the configuration is OK or has problems

Concept explained:
For two devices (host and router/gateway) to communicate directly on a LAN,
they must be in the same subnet. Also, host IP addresses must not use the
network address or broadcast address of the subnet. This tool helps you
understand if a typical manual IPv4 configuration makes sense
"""

from CN10 import is_valid_ipv4
from CN13 import is_valid_subnet_mask


def ip_to_int(ip: str) -> int:
    """Converts dotted-decimal IPv4 string to 32-bit integer."""
    parts = [int(p) for p in ip.split(".")]
    value = 0
    for part in parts:
        value = (value << 8) | part
    return value


def int_to_ip(value: int) -> str:
    """Converts 32-bit integer to dotted-decimal IPv4 string."""
    return ".".join(str((value >> (8 * i)) & 0xFF) for i in range(3, -1, -1))


def calculate_network_and_broadcast(ip: str, mask: str) -> tuple[str, str]:
    """
    Returns (network_address, broadcast_address) for a given IP and subnet mask.
    """
    ip_int = ip_to_int(ip)
    mask_int = ip_to_int(mask)

    network_int = ip_int & mask_int
    wildcard_int = (~mask_int) & 0xFFFFFFFF
    broadcast_int = network_int | wildcard_int

    return int_to_ip(network_int), int_to_ip(broadcast_int)


def same_subnet(ip1: str, ip2: str, mask: str) -> bool:
    """Returns True if ip1 and ip2 are in the same subnet for the given mask."""
    net1, _ = calculate_network_and_broadcast(ip1, mask)
    net2, _ = calculate_network_and_broadcast(ip2, mask)
    return net1 == net2


def analyze_host_config(host_ip: str, mask: str, gateway: str, dns: str | None = None) -> dict:
    """
    Analyzes the given host configuration and returns a dict with:

    - network
    - broadcast
    - is_host_network_address
    - is_host_broadcast_address
    - gateway_same_subnet
    - dns_valid (None if no DNS given)
    - overall_ok
    - issues: list of text descriptions
    """
    issues: list[str] = []

    network, broadcast = calculate_network_and_broadcast(host_ip, mask)

    is_network_addr = (host_ip == network)
    is_broadcast_addr = (host_ip == broadcast)

    if is_network_addr:
        issues.append("Host IP is the network address (cannot be used by a host).")

    if is_broadcast_addr:
        issues.append("Host IP is the broadcast address (cannot be used by a host).")

    # Checck gateway in same subnert
    gateway_same = same_subnet(host_ip, gateway, mask)
    if not gateway_same:
        issues.append(
            "Default gateway is not in the same subnet as the host. "
            "The host will not reach the gateway without routing tricks."
        )

    #basic DNS check (if provided)
    dns_valid = None
    if dns:
        if not is_valid_ipv4(dns):
            dns_valid = False
            issues.append("DNS server address is not a valid IPv4 address.")
        else:
            dns_valid = True

    overall_ok = (len(issues) == 0)

    return {
        "network": network,
        "broadcast": broadcast,
        "is_host_network_address": is_network_addr,
        "is_host_broadcast_address": is_broadcast_addr,
        "gateway_same_subnet": gateway_same,
        "dns_valid": dns_valid,
        "overall_ok": overall_ok,
        "issues": issues,
    }


def print_report(host_ip: str, mask: str, gateway: str, dns: str | None, info: dict) -> None:
    """
    Prints a human-readable report of the host configuration analysis.
    """
    print("\nConfiguration summary")
    print("---------------------")
    print(f"Host IP        : {host_ip}")
    print(f"Subnet mask    : {mask}")
    print(f"Network address: {info['network']}")
    print(f"Broadcast addr : {info['broadcast']}")
    print(f"Default gateway: {gateway}")

    if dns:
        print(f"DNS server     : {dns}")
    else:
        print("DNS server     : (not provided)")

    print("\nChecks:")
    print("-------")

    if info["is_host_network_address"]:
        print(" - Host IP is the NETWORK address ❌")
    else:
        print(" - Host IP is not the network address ✔")

    if info["is_host_broadcast_address"]:
        print(" - Host IP is the BROADCAST address ❌")
    else:
        print(" - Host IP is not the broadcast address ✔")

    if info["gateway_same_subnet"]:
        print(" - Gateway is in the same subnet as the host ✔")
    else:
        print(" - Gateway is NOT in the same subnet as the host ❌")

    if info["dns_valid"] is None:
        print(" - DNS server not checked (no DNS provided).")
    elif info["dns_valid"]:
        print(" - DNS server address format is valid ✔")
    else:
        print(" - DNS server address format is NOT valid ❌")

    print("\nOverall result")
    print("--------------")
    if info["overall_ok"]:
        print(" ✅ This configuration looks OK for a typical IPv4 LAN.\n")
    else:
        print(" ⚠ This configuration has issues:\n")
        for problem in info["issues"]:
            print(f"   - {problem}")
        print()


def main():
    print("=== Task CN20 : IPv4 Host Configuration Checker ===\n")

    while True:
        host_ip = input("Enter host IPv4 address (or 'q' to quit): ").strip()
        if host_ip.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break

        mask = input("Enter subnet mask: ").strip()
        gateway = input("Enter default gateway IPv4 address: ").strip()
        dns = input("Enter DNS server IPv4 address (optional, press Enter to skip): ").strip()
        if dns == "":
            dns = None

        #Validate basic formats first
        if not is_valid_ipv4(host_ip):
            print("Host IP is NOT a valid IPv4 address. Please try again.\n")
            continue

        if not is_valid_subnet_mask(mask):
            print("Subnet mask is NOT a valid mask. Please try again.\n")
            continue

        if not is_valid_ipv4(gateway):
            print("Default gateway IP is NOT a valid IPv4 address. Please try again.\n")
            continue

        # Analyze config
        info = analyze_host_config(host_ip, mask, gateway, dns)
        print_report(host_ip, mask, gateway, dns, info)

#program entry point
if __name__ == "__main__":
    main()
