"""
Task CN10 : IPv4 format checker

Description: this task checks whether a given IPv4 address is written in a valid format.
A valid IPv4 address must have exactly four octets separated by dots, and each
octet must be a number between 0 and 255.

Concept explained: many networking tasks start with validating IP addresses. Before you calculate
subnets, ranges, or classify addresses, you must first confirm the IP structure
is correct. This program helps you understand what a correct IPv4 address
looks like.
"""

def is_valid_ipv4(ip: str) -> bool:
    """Returns True if the IPv4 address is in valid dotted-decimal format."""

    parts = ip.strip().split(".")

    # Must have exactly 4 octets
    if len(parts) != 4:
        return False

    for part in parts:
        # Each part must be numeric
        if not part.isdigit():
            return False
        num = int(part)
        # Each octet must be between 0 and 255
        if num < 0 or num > 255:
            return False
        # Leading zeros are not allowed (e.g., '01', '001') unless the part is exactly '0'
        if part != "0" and part.startswith("0"):
            return False

    return True

def main():
    print("=== Task CN10 : IPv4 Format Checker ===\n")

    while True:
        ip = input("Enter an IPv4 address to check (or 'q' to quit): ").strip()

        if ip.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break

        if is_valid_ipv4(ip):
            print(f"'{ip}' is a valid IPv4 address.\n")
        else:
            print(f"'{ip}' is NOT a valid IPv4 address.\n")

# program entry point
if __name__ == "__main__":
    main()
