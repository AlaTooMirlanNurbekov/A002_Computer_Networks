"""
Task CN19 : same-subnet checker

Description:
This task checks whether two IPv4 addresses belong to the same subnet,
based on a given subnet mask. It will:

- Validate both IPv4 addresses and the subnet mask
- Calculate the network address for each IP
- Tell you if they are in the same subnet or not
- Show the network address of each IP

Concept explained:
Two hosts are in the same IPv4 subnet if, after applying the subnet mask
(bitwise AND), they produce the same network address. This is important
for understanding when devices can communicate directly without a router.
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
    """Converts a 32-bit integer to dotted-decimal IPv4 string."""
    return ".".join(str((value >> (8 * i)) & 0xFF) for i in range(3, -1, -1))


def calculate_network_address(ip: str, mask: str) -> str:
    """
    Returns the network address as dotted-decimal string
    for the given IP and subnet mask.
    """
    ip_int = ip_to_int(ip)
    mask_int = ip_to_int(mask)
    network_int = ip_int & mask_int
    return int_to_ip(network_int)


def same_subnet(ip1: str, ip2: str, mask: str) -> bool:
    """
    Returns True if ip1 and ip2 are in the same subnet for the given mask.
    """
    net1 = calculate_network_address(ip1, mask)
    net2 = calculate_network_address(ip2, mask)
    return net1 == net2


def main():
    print("=== Task CN19 : Same-Subnet Checker ===\n")

    while True:
        ip1 = input("Enter first IPv4 address (or 'q' to quit): ").strip()
        if ip1.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break

        ip2 = input("Enter second IPv4 address: ").strip()
        mask = input("Enter subnet mask: ").strip()

        #validate inputs
        if not is_valid_ipv4(ip1):
            print("The first IPv4 address is NOT valid.\n")
            continue

        if not is_valid_ipv4(ip2):
            print("The second IPv4 address is NOT valid.\n")
            continue

        if not is_valid_subnet_mask(mask):
            print("The subnet mask is NOT valid.\n")
            continue

        # calculate network addresses
        net1 = calculate_network_address(ip1, mask)
        net2 = calculate_network_address(ip2, mask)

        print("\nResults:")
        print(f"  IP 1           : {ip1}")
        print(f"  IP 2           : {ip2}")
        print(f"  Subnet mask    : {mask}")
        print(f"  Network of IP1 : {net1}")
        print(f"  Network of IP2 : {net2}")

        if same_subnet(ip1, ip2, mask):
            print("\nConclusion: These two IP addresses ARE in the same subnet.\n")
        else:
            print("\nConclusion: These two IP addresses are NOT in the same subnet.\n")

# program entry point
if __name__ == "__main__":
    main()
