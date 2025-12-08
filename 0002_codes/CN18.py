"""
Task CN18 :subnet splitter (network → multiple smaller subnets)
Description: this task helps you split an existing network into smaller subnets.
You provide:
- A base network in CIDR notation (for example: 192.168.1.0/24)
- The number of subnets you need (for example: 4)
The program will:
- Find how many bits must be borrowed to create at least that many subnets
- Show the new prefix length and subnet mask
- Show how many subnets you actually get
- Show how many usable hosts per subnet
- List the first subnets with their:
    - Network address
    - Broadcast address
    - First usable host
    - Last usable host
Concept explained:subnetting is done by "borrowing" host bits to create more network bits.
More subnets → fewer host bits → fewer hosts per subnet.
This program makes this process visible with real IP examples.
"""

from CN10 import is_valid_ipv4
from CN14 import cidr_to_mask


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


def parse_cidr(cidr: str) -> tuple[str, int]:
    """
    Parses a CIDR string like '192.168.1.0/24' and returns (ip_str, prefix_length).

    Raises ValueError on invalid input.
    """
    if "/" not in cidr:
        raise ValueError("CIDR must be in the form 'IP/prefix', e.g. 192.168.1.0/24.")

    ip_part, prefix_part = cidr.split("/", 1)
    ip_part = ip_part.strip()
    prefix_part = prefix_part.strip()

    if not is_valid_ipv4(ip_part):
        raise ValueError("Invalid IPv4 address in CIDR.")

    if not prefix_part.isdigit():
        raise ValueError("Prefix length must be a number between 0 and 32.")

    prefix = int(prefix_part)
    if not (0 <= prefix <= 32):
        raise ValueError("Prefix length must be between 0 and 32.")

    return ip_part, prefix


def network_align(ip: str, prefix: int) -> str:
    """
    Aligns the given IP to the correct network address for the prefix.
    """
    ip_int = ip_to_int(ip)
    if prefix == 0:
        mask_int = 0
    else:
        mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF

    network_int = ip_int & mask_int
    return int_to_ip(network_int)


def calculate_subnets(base_network: str, base_prefix: int, desired_subnets: int):
    """
    Given a base network and prefix, and desired number of subnets,
    return a dictionary describing the new subnetting:

    - base_network
    - base_prefix
    - new_prefix
    - new_mask
    - actual_subnets
    - hosts_per_subnet
    - subnets: list of dicts with:
        - network
        - broadcast
        - first_host
        - last_host
    """
    if desired_subnets <= 0:
        raise ValueError("Number of subnets must be a positive integer.")

    # How many bits do we need to borrow to have at least 'desired_subnets' subnets?
    bits_to_borrow = 0
    while (1 << bits_to_borrow) < desired_subnets:
        bits_to_borrow += 1

    new_prefix = base_prefix + bits_to_borrow

    # We limit to /30 for "normal" host subnets (at least 2 usable hosts)
    if new_prefix > 30:
        raise ValueError(
            "Cannot create that many subnets while keeping at least 2 usable host "
            "addresses per subnet (new prefix would be /{}).".format(new_prefix)
        )

    actual_subnets = 1 << bits_to_borrow
    host_bits = 32 - new_prefix
    total_addresses_per_subnet = 1 << host_bits
    hosts_per_subnet = total_addresses_per_subnet - 2  # exclude network + broadcast

    new_mask = cidr_to_mask(new_prefix)

    # Align base network to its original prefix boundary
    aligned_base = network_align(base_network, base_prefix)
    base_int = ip_to_int(aligned_base)

    # Size (in addresses) of each new subnet
    block_size = total_addresses_per_subnet

    subnets_info = []
    for i in range(actual_subnets):
        network_int = base_int + i * block_size
        broadcast_int = network_int + block_size - 1

        network_ip = int_to_ip(network_int)
        broadcast_ip = int_to_ip(broadcast_int)

        if hosts_per_subnet > 0:
            first_host_ip = int_to_ip(network_int + 1)
            last_host_ip = int_to_ip(broadcast_int - 1)
        else:
            first_host_ip = "N/A"
            last_host_ip = "N/A"

        subnets_info.append(
            {
                "network": network_ip,
                "broadcast": broadcast_ip,
                "first_host": first_host_ip,
                "last_host": last_host_ip,
            }
        )

    return {
        "base_network": aligned_base,
        "base_prefix": base_prefix,
        "new_prefix": new_prefix,
        "new_mask": new_mask,
        "actual_subnets": actual_subnets,
        "hosts_per_subnet": hosts_per_subnet,
        "subnets": subnets_info,
    }


def print_subnet_plan(info: dict) -> None:
    """
    Nicely prints the subnet plan to the console.
    """
    print("\nSubnetting plan:")
    print("----------------")
    print(f"Base network       : {info['base_network']}/{info['base_prefix']}")
    print(f"New prefix         : /{info['new_prefix']}")
    print(f"New subnet mask    : {info['new_mask']}")
    print(f"Number of subnets  : {info['actual_subnets']}")
    print(f"Usable hosts / subnet: {info['hosts_per_subnet']}")
    print("----------------")

    # Avoid printing an excessively long list
    max_to_show = 16
    total = info["actual_subnets"]
    to_show = min(total, max_to_show)

    print(f"Showing first {to_show} subnet(s):\n")

    for idx in range(to_show):
        s = info["subnets"][idx]
        print(f"Subnet {idx}:")
        print(f"  Network   : {s['network']}/{info['new_prefix']}")
        print(f"  Broadcast : {s['broadcast']}")
        print(f"  First host: {s['first_host']}")
        print(f"  Last host : {s['last_host']}")
        print()

    if total > max_to_show:
        print(f"... ({total - max_to_show} more subnets not shown for brevity) ...\n")


def main():
    print("=== Task CN18 : Subnet Splitter (Network → Multiple Subnets) ===\n")

    while True:
        cidr_input = input(
            "Enter base network in CIDR (e.g., 192.168.1.0/24) or 'q' to quit: "
        ).strip()

        if cidr_input.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break

        try:
            base_ip, base_prefix = parse_cidr(cidr_input)
        except ValueError as e:
            print(f"Error: {e}\n")
            continue

        raw_subnets = input("Enter desired number of subnets: ").strip()
        if not raw_subnets.isdigit():
            print("Number of subnets must be a positive integer.\n")
            continue

        desired_subnets = int(raw_subnets)
        if desired_subnets <= 0:
            print("Number of subnets must be greater than 0.\n")
            continue

        try:
            info = calculate_subnets(base_ip, base_prefix, desired_subnets)
            print_subnet_plan(info)
        except ValueError as e:
            print(f"Error: {e}\n")


# program entry point
if __name__ == "__main__":
    main()
