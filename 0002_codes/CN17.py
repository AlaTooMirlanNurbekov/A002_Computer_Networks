"""
Task CN17 : subnet size advisor (hosts → CIDR)

Description:
This task helps you choose a subnet size when you know how many hosts
you need. You enter the required number of hosts, and the program:

- Finds the smallest prefix length (like /27, /26, /25, ...)
  that can support at least that many hosts.
- Shows the corresponding subnet mask in dotted-decimal form.
- Shows how many usable hosts that subnet provides.

Concept explained:
When designing networks, you rarely start from an IP and mask. Instead,
you start from requirements: "I need around 50 hosts", "this VLAN needs
200 devices", etc. This program shows how the number of host bits
determines the subnet mask and the usable host count.
"""

from CN14 import cidr_to_mask  # reuse CIDR → mask converter from previous task


def required_prefix_for_hosts(required_hosts: int) -> int:
    """
    Given a required host count, return the smallest prefix length (0–30)
    that can support at least that many usable hosts.

    For normal subnets, usable hosts = 2^(host_bits) - 2.
    We do not generate /31 or /32 here because they have 0 usable hosts
    in traditional unicast host addressing (used only in special cases).
    """
    if required_hosts <= 0:
        raise ValueError("Required hosts must be a positive integer.")

    # We try all prefixes from /30 down to /0 and choose the smallest that fits.
    # Note: host_bits = 32 - prefix
    best_prefix = None

    for prefix in range(30, -1, -1):
        host_bits = 32 - prefix
        usable_hosts = (1 << host_bits) - 2  # 2^host_bits - 2

        if usable_hosts >= required_hosts:
            best_prefix = prefix

    if best_prefix is None:
        # Should not happen for any reasonable required_hosts
        raise ValueError("Cannot find a suitable prefix for the given host count.")

    return best_prefix

def explain_subnet_choice(required_hosts: int) -> dict:
    """
    Returns a dictionary with details about the suggested subnet:

    - required_hosts
    - prefix
    - subnet_mask
    - total_addresses
    - usable_hosts
    """
    prefix = required_prefix_for_hosts(required_hosts)
    host_bits = 32 - prefix
    total_addresses = 1 << host_bits  # 2^host_bits
    usable_hosts = total_addresses - 2
    subnet_mask = cidr_to_mask(prefix)

    return {
        "required_hosts": required_hosts,
        "prefix": prefix,
        "subnet_mask": subnet_mask,
        "total_addresses": total_addresses,
        "usable_hosts": usable_hosts,
    }

def print_subnet_advice(info: dict) -> None:
    """
    Nicely prints the subnet planning advice for the user.
    """
    print("\nSuggested subnet size:")
    print("----------------------")
    print(f"Required hosts          : {info['required_hosts']}")
    print(f"Recommended prefix      : /{info['prefix']}")
    print(f"Subnet mask             : {info['subnet_mask']}")
    print(f"Total addresses in block: {info['total_addresses']}")
    print(f"Usable host addresses   : {info['usable_hosts']}")
    print("----------------------")
    print("Note: Usable hosts = total addresses - 2 "
          "(network + broadcast in traditional IPv4 subnets).")
    print("In special point-to-point cases, /31 can be used, but this tool")
    print("focuses on normal host subnets.\n")

def main():
    print("=== Task CN17 : Subnet Size Advisor (Hosts → CIDR) ===\n")

    while True:
        raw = input("Enter required number of hosts (or 'q' to quit): ").strip()

        if raw.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break
        if not raw.isdigit():
            print("Please enter a positive integer for the host count.\n")
            continue

        required_hosts = int(raw)

        if required_hosts <= 0:
            print("Host count must be greater than 0.\n")
            continue
        try:
            info = explain_subnet_choice(required_hosts)
            print_subnet_advice(info)
        except ValueError as e:
            print(f"Error: {e}\n")

# program entry point
if __name__ == "__main__":
    main()
