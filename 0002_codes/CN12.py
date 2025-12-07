"""
Task CN12 : IP class detector

Description: this task checks the first octet of an IPv4 address and tells you which
historical IP class (A, B, C, D, or E) it belongs to. It also explains
if the address is in a special or reserved range (like 127.x.x.x for loopback).
Concept explained:
Older networking books often describe IPv4 using classes:
  - Class A: 1–126
  - Class B: 128–191
  - Class C: 192–223
  - Class D: 224–239 (multicast)
  - Class E: 240–254 (experimental)

Today, CIDR is used instead of strict classes, but the idea of classes is
still useful for learning and for understanding old documentation.
"""

from CN10 import is_valid_ipv4  # reuse the format checker

def get_ip_class(ip: str) -> str:
    """
    Returns a text description of the IP class based on the first octet.
    Also mentions special ranges like 0.x.x.x and 127.x.x.x.
    """
    parts = [int(p) for p in ip.split(".")]
    first = parts[0]

    # Special cases
    if first == 0:
        return "Special: 0.x.x.x is used for 'this network' and is not a normal host address."
    if first == 127:
        return "Special: 127.x.x.x is the loopback range (localhost)."

    if 1 <= first <= 126:
        return "Class A (historical) – default mask /8, many hosts per network."
    elif 128 <= first <= 191:
        return "Class B (historical) – default mask /16, balance of networks and hosts."
    elif 192 <= first <= 223:
        return "Class C (historical) – default mask /24, many small networks."
    elif 224 <= first <= 239:
        return "Class D – reserved for multicast traffic."
    elif 240 <= first <= 254:
        return "Class E – experimental, not used for normal hosts."
    elif first == 255:
        return "Special: 255.x.x.x often used for broadcast (depends on mask)."
    else:
        # Should not happen with valid IPv4, but just in case
        return "Unknown or out-of-range first octet."


def main():
    print("=== Task CN12 : IP Class Detector ===\n")

    while True:
        ip = input("Enter an IPv4 address (or 'q' to quit): ").strip()

        if ip.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break

        if not is_valid_ipv4(ip):
            print(f"'{ip}' is NOT a valid IPv4 address.\n")
            continue

        result = get_ip_class(ip)
        print(f"Result for {ip}:")
        print(result)
        print()

# program entry point
if __name__ == "__main__":
    main()
