"""
Task CN15 : network and broadcast address calculator

Description:this task takes an IPv4 address and subnet mask, converts them into binary,
and calculates the network address and the broadcast address of that subnet.

Concept explained:
Every IP subnet has:
 - a network address (all host bits = 0)
 - a broadcast address (all host bits = 1)

Understanding how to calculate these is the foundation for subnetting, routing,
and IP planning. This program shows each step clearly.
"""

from CN10 import is_valid_ipv4
from CN13 import is_valid_subnet_mask


def ip_to_binary(ip: str) -> str:
    """Converts dotted IPv4 string to a 32-bit binary string."""
    return "".join(f"{int(octet):08b}" for octet in ip.split("."))


def binary_to_ip(binary: str) -> str:
    """Converts a 32-bit binary string to dotted IPv4."""
    octets = [str(int(binary[i:i+8], 2)) for i in range(0, 32, 8)]
    return ".".join(octets)


def calculate_network_address(ip: str, mask: str) -> str:
    ip_bin = ip_to_binary(ip)
    mask_bin = ip_to_binary(mask)

    #network address = IP AND mask
    network_bin = "".join(
        "1" if ip_bin[i] == "1" and mask_bin[i] == "1" else "0"
        for i in range(32)
    )
    return binary_to_ip(network_bin)


def calculate_broadcast_address(ip: str, mask: str) -> str:
    ip_bin = ip_to_binary(ip)
    mask_bin = ip_to_binary(mask)

    # broadcast = Network address + set all host bits to 1
    broadcast_bin = "".join(
        "1" if mask_bin[i] == "0" else ("1" if ip_bin[i] == "1" else "0")
        for i in range(32)
    )
    return binary_to_ip(broadcast_bin)


def main():
    print("=== Task CN15 : Network & Broadcast Address Calculator ===\n")

    while True:
        ip = input("Enter IPv4 address (or 'q' to quit): ").strip()

        if ip.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break

        mask = input("Enter subnet mask: ").strip()

        # validate inputs
        if not is_valid_ipv4(ip):
            print("Invalid IPv4 address.\n")
            continue

        if not is_valid_subnet_mask(mask):
            print("Invalid subnet mask.\n")
            continue

        network = calculate_network_address(ip, mask)
        broadcast = calculate_broadcast_address(ip, mask)

        print(f"\nNetwork address : {network}")
        print(f"Broadcast address: {broadcast}\n")

#program entry point
if __name__ == "__main__":
    main()
