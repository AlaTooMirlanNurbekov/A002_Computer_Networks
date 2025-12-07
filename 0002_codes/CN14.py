"""
Task CN14 : CIDR to subnet mask converter

Description: This task converts a CIDR prefix length (for example: /24 or 24) into a
dotted-decimal subnet mask (for example: 255.255.255.0).

Concept explained:CIDR (Classless Inter-Domain Routing) uses a prefix length to show how many
bits are used for the network part of an IP address. For example, /24 means
that the first 24 bits are network bits, and the remaining 8 bits are host bits.
This program helps you see how a prefix like /n becomes a normal subnet mask.
"""


def cidr_to_mask(prefix_length: int) -> str:
    """
    Converts a prefix length (0–32) into a dotted-decimal subnet mask.

    Example:
        24 -> "255.255.255.0"
        16 -> "255.255.0.0"
        0  -> "0.0.0.0"
    """
    if not (0 <= prefix_length <= 32):
        raise ValueError("Prefix length must be between 0 and 32.")

    #build a 32-bit binary string: n ones followed by (32 - n) zeros
    binary_mask = "1" * prefix_length + "0" * (32 - prefix_length)

    octets = []
    for i in range(0, 32, 8):
        octet_bits = binary_mask[i:i + 8]
        octets.append(str(int(octet_bits, 2)))

    return ".".join(octets)


def parse_input_to_prefix(user_input: str) -> int:
    """
    Parses user input that may look like '/24' or '24' and returns the integer prefix length.
    """
    text = user_input.strip()

    if text.startswith("/"):
        text = text[1:]

    if not text.isdigit():
        raise ValueError("Prefix must be a number (for example: 24 or /24).")

    return int(text)


def main():
    print("=== Task CN14 : CIDR to Subnet Mask Converter ===\n")

    while True:
        user_input = input("Enter CIDR prefix (e.g., 24 or /24), or 'q' to quit: ").strip()

        if user_input.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break

        try:
            prefix = parse_input_to_prefix(user_input)
            mask = cidr_to_mask(prefix)
            print(f"/{prefix} corresponds to subnet mask: {mask}\n")
        except ValueError as e:
            print(f"Error: {e}\n")

# program entry point
if __name__ == "__main__":
    main()
