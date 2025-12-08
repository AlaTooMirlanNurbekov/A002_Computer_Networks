"""
Task CN16 : host range calculator
Description:
This task takes an IPv4 address and subnet mask, then calculates:
- Network address
- Broadcast address
- First usable host address
- Last usable host address
- Number of usable hosts in the subnet

Concept explained: after you know the network address and broadcast address of a subnet, you can
determine which IPs are usable by hosts. The first usable IP is one above the
network address, and the last usable IP is one below the broadcast address. This is essential for IP planning and subnetting in real networks
"""

from CN10 import is_valid_ipv4
from CN13 import is_valid_subnet_mask


def ip_to_int(ip: str) -> int:
    """converts dotted-decimal IPv4 string to 32-bit integer."""
    parts = [int(p) for p in ip.split(".")]
    value = 0
    for part in parts:
        value = (value << 8) | part
    return value

def int_to_ip(value: int) -> str:
    """Converts 32-bit integer to dotted-decimal IPv4 string."""
    return ".".join(str((value >> (8 * i)) & 0xFF) for i in range(3, -1, -1))

def subnet_mask_to_prefix(mask: str) -> int:
    """
    Converts a valid subnet mask (like 255.255.255.0) to prefix length (like 24)
    Assumes mask is already validated by is_valid_subnet_mask
    """
    parts = [int(p) for p in mask.split(".")]
    binary_mask = "".join(f"{octet:08b}" for octet in parts)
    # Count number of '1' bits
    return binary_mask.count("1")


def calculate_network_and_broadcast(ip: str, mask: str) -> tuple[str, str]:
    """
    Returns (network_address_str, broadcast_address_str) for given IP and mask
    """
    ip_int = ip_to_int(ip)
    mask_int = ip_to_int(mask)

    network_int = ip_int & mask_int
    # Invert mask to get host bits, then OR with network for broadcast
    wildcard_int = (~mask_int) & 0xFFFFFFFF
    broadcast_int = network_int | wildcard_int

    return int_to_ip(network_int), int_to_ip(broadcast_int)


def calculate_host_range(ip: str, mask: str):
    """
    Calculates network, broadcast, first host, last host, and usable host count

    Returns a dictionary with keys:
    - network
    - broadcast
    - first_host
    - last_host
    - usable_hosts
    - prefix
    """
    network, broadcast = calculate_network_and_broadcast(ip, mask)
    prefix = subnet_mask_to_prefix(mask)

    network_int = ip_to_int(network)
    broadcast_int = ip_to_int(broadcast)

    host_bits = 32 - prefix

    # Special /31 and /32 cases: traditionally considered "no usable hosts"
    if prefix >= 31:
        first_host = "N/A"
        last_host = "N/A"
        usable_hosts = 0
    else:
        first_host_int = network_int + 1
        last_host_int = broadcast_int - 1
        first_host = int_to_ip(first_host_int)
        last_host = int_to_ip(last_host_int)
        usable_hosts = (1 << host_bits) - 2

    return {
        "network": network,
        "broadcast": broadcast,
        "first_host": first_host,
        "last_host": last_host,
        "usable_hosts": usable_hosts,
        "prefix": prefix,
    }

def main():
    print("=== Task CN16 : Host Range Calculator ===\n")
    while True:
        ip = input("Enter IPv4 address (or 'q' to quit): ").strip()
        if ip.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break
        mask = input("Enter subnet mask: ").strip()

        # Step 1: validate inputs
        if not is_valid_ipv4(ip):
            print("Invalid IPv4 address. Please try again.\n")
            continue

        if not is_valid_subnet_mask(mask):
            print("Invalid subnet mask. Please try again.\n")
            continue

        # Step 2: calculate host range information
        info = calculate_host_range(ip, mask)

        print("\nResults:")
        print(f"  IP address      : {ip}")
        print(f"  Subnet mask     : {mask} (/{info['prefix']})")
        print(f"  Network address : {info['network']}")
        print(f"  Broadcast addr  : {info['broadcast']}")

        if info["usable_hosts"] == 0:
            print("  First host      : N/A (this subnet has no traditional host addresses)")
            print("  Last host       : N/A")
        else:
            print(f"  First host      : {info['first_host']}")
            print(f"  Last host       : {info['last_host']}")

        print(f"  Usable hosts    : {info['usable_hosts']}\n")


# program entry point
if __name__ == "__main__":
    main()
