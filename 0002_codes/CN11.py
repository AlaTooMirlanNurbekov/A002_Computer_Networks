"""
Task CN11 : private vs public IP checker

Description: This task checks whether a given IPv4 address belongs to the private IP
ranges defined by RFC1918 or if it is a public IP.

Private IPv4 ranges:
 - 10.0.0.0     → 10.255.255.255       (10.0.0.0/8)
 - 172.16.0.0   → 172.31.255.255        (172.16.0.0/12)
 - 192.168.0.0  → 192.168.255.255       (192.168.0.0/16)

Concept explained: laptop, phone, and home router usually use private IP ranges. These IPs
do not route on the public internet. Public IPs, on the other hand, are used
for direct internet communication. This tool helps you understand how to
recognize private vs public space
"""

from CN10 import is_valid_ipv4  # reuse the checker from previous task


def is_private_ipv4(ip: str) -> bool:
    """Returns True if the IPv4 address is in a private RFC1918 range."""
    parts = [int(p) for p in ip.split(".")]

    # 10.0.0.0/8
    if parts[0] == 10:
        return True

    # 172.16.0.0 – 172.31.255.255  (/12)
    if parts[0] == 172 and 16 <= parts[1] <= 31:
        return True

    # 192.168.0.0/16
    if parts[0] == 192 and parts[1] == 168:
        return True

    return False


def main():
    print("=== Task CN11 : Private vs Public IP Checker ===\n")

    while True:
        ip = input("Enter an IPv4 address to check (or 'q' to quit): ").strip()

        if ip.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break

        # Step 1: Validate format
        if not is_valid_ipv4(ip):
            print(f"'{ip}' is NOT a valid IPv4 address.\n")
            continue

        # Step 2: Check private/public
        if is_private_ipv4(ip):
            print(f"'{ip}' is a PRIVATE IPv4 address.\n")
        else:
            print(f"'{ip}' is a PUBLIC IPv4 address.\n")


# program entry point
if __name__ == "__main__":
    main()
