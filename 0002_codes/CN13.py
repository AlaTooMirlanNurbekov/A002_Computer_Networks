"""
Task CN13 : subnet mask validator

Description: This task checks whether a subnet mask is valid. A valid subnet mask must:
 - Be written in dotted-decimal format (e.g., 255.255.255.0)
 - Contain only octets that appear in real masks: 255, 254, 252, 248,
   240, 224, 192, 128, or 0
 - Have continuous 1-bits followed only by 0-bits (no patterns like 11101100)

Concept explained: subnet masks define how many bits are used for the network portion of an IP.
This task teaches you what valid masks look like and why only certain octets
are allowed in each position.
"""

VALID_MASK_OCTETS = {255, 254, 252, 248, 240, 224, 192, 128, 0}


def is_valid_subnet_mask(mask: str) -> bool:
    """Returns True if mask is a valid dotted-decimal subnet mask."""
    parts = mask.strip().split(".")

    if len(parts) != 4:
        return False

    #convert to numbers
    try:
        octets = [int(p) for p in parts]
    except ValueError:
        return False

    # Check each octet is allowed
    for octet in octets:
        if octet not in VALID_MASK_OCTETS:
            return False

    #check continuity of 1s then 0s
    # Convert mask to a complete 32-bit binary string
    binary_mask = "".join(f"{octet:08b}" for octet in octets)

    if "01" in binary_mask:
        # Pattern 01 inside the mask means something like 11101111 (invalid)
        return False

    return True


def main():
    print("=== Task CN13 : Subnet Mask Validator ===\n")

    while True:
        mask = input("Enter a subnet mask to check (or 'q' to quit): ").strip()

        if mask.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break

        if is_valid_subnet_mask(mask):
            print(f"'{mask}' is a valid subnet mask.\n")
        else:
            print(f"'{mask}' is NOT a valid subnet mask.\n")


# program entry point
if __name__ == "__main__":
    main()
