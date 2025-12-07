"""
Task CN09 : network glossary helper
Description: this task gives you a small interactive network glossary. You can type a
networking term (like 'latency', 'throughput', 'MAC address') and the program
will show a short explanation. You can also list all available terms.

Concept explained: networking uses many specific words. If you do not remember what a term
means, it is easy to get lost. This program helps you quickly review basic
networking vocabulary so you can connect theory with the correct terms.
"""
GLOSSARY = {
    "bandwidth": (
        "The maximum amount of data that can be transferred over a network "
        "connection in a given amount of time, usually measured in bits per "
        "second (bps)."
    ),
    "throughput": (
        "The actual amount of data successfully transferred over a network "
        "connection in a given time. It is usually lower than the bandwidth "
        "because of overhead and network conditions."
    ),
    "latency": (
        "The time it takes for a data packet to travel from source to "
        "destination. Often measured in milliseconds (ms)."
    ),
    "jitter": (
        "The variation in latency over time. High jitter means the delay of "
        "packets is not consistent, which is bad for real-time applications."
    ),
    "mac address": (
        "A unique hardware address assigned to a network interface card (NIC). "
        "It works at the Data Link layer and is usually written as "
        "six pairs of hexadecimal numbers, for example: AA:BB:CC:DD:EE:FF."
    ),
    "ip address": (
        "A logical address assigned to a device on an IP network. It works at "
        "the Network layer and helps routers forward packets to the correct "
        "destination."
    ),
    "default gateway": (
        "The router that your device uses to send traffic to other networks. "
        "If the destination is not in your local network, packets go to the "
        "default gateway first."
    ),
    "dns": (
        "Domain Name System. It translates human-friendly domain names "
        "(like example.com) into IP addresses that computers can use."
    ),
    "port": (
        "A logical number used by the Transport layer to identify specific "
        "applications or services on a device, for example port 80 for HTTP "
        "or port 443 for HTTPS."
    ),
    "firewall": (
        "A security device or software that monitors and controls network "
        "traffic based on predefined rules. It can allow or block traffic."
    ),
    "router": (
        "A device that forwards packets between different networks. It decides "
        "where to send packets based on IP addresses and routing tables."
    ),
    "switch": (
        "A device used in local area networks (LANs) to connect multiple "
        "devices. It forwards frames based on MAC addresses and builds a MAC "
        "address table."
    ),
}

def normalize_term(term: str) -> str:
    """Normalizes user input for matching in the glossary."""
    return term.strip().lower()

def look_up_term(term: str):
    """Looks up a term and prints its explanation if found."""
    key = normalize_term(term)

    if key in GLOSSARY:
        print(f"\n{term.strip()} :")
        print(GLOSSARY[key])
        print()
    else:
        print("\nSorry, this term is not in the glossary yet.")
        print("You can try another word or type 'list' to see all terms.\n")

def list_terms():
    """Prints all available glossary terms."""
    print("\nAvailable terms in the glossary:")
    print("---------------------------------")
    for term in sorted(GLOSSARY.keys()):
        print(f"- {term}")
    print("---------------------------------\n")

# program entry point
if __name__ == "__main__":
    print("=== Task CN09 : Network Glossary Helper ===")
    print("Type a networking term to see its meaning.")
    print("Type 'list' to see all available terms.")
    print("Type 'q' to quit.\n")

    while True:
        user_input = input("Enter a term ('list' or 'q'): ")

        if not user_input:
            continue

        lowered = user_input.strip().lower()

        if lowered in ("q", "quit", "exit"):
            print("Goodbye! Keep reviewing your network vocabulary.")
            break
        elif lowered == "list":
            list_terms()
        else:
            look_up_term(user_input)
