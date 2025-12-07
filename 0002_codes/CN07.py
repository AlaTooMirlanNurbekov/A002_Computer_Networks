"""
Task CN07 : OSI vs TCP/IP layer mapper
Description: this task helps you see the relationship between the 7-layer OSI model and
the simpler TCP/IP model. You can type the name or number of an OSI layer
and the program will show which TCP/IP layer it roughly maps to

Concept explained: in networking theory, the OSI model has 7 layers and the TCP/IP model has 4
In practice, many people use both models when they talk about networks
This task helps you understand how OSI layers are grouped inside the TCP/IP
model, so that you do not get confused when different books use different
layer names
"""

# A simple mapping from OSI layer names/numbers to TCP/IP layers
OSI_TO_TCPIP = {
    1: ("Physical", "Network Access"),
    2: ("Data Link", "Network Access"),
    3: ("Network", "Internet"),
    4: ("Transport", "Transport"),
    5: ("Session", "Application"),
    6: ("Presentation", "Application"),
    7: ("Application", "Application"),
}

TCPIP_LAYERS = {
    "Network Access": ["Physical", "Data Link"],
    "Internet": ["Network"],
    "Transport": ["Transport"],
    "Application": ["Session", "Presentation", "Application"],
}


def show_all_mappings():
    """Prints a small table of OSI → TCP/IP mappings."""
    print("OSI to TCP/IP layer mapping")
    print("---------------------------")
    print("OSI # | OSI Layer      →  TCP/IP Layer")
    print("------+----------------+----------------")
    for num in range(1, 8):
        osi_name, tcpip_name = OSI_TO_TCPIP[num]
        print(f"  {num}   | {osi_name:<14} →  {tcpip_name}")
    print("---------------------------")
    print("Note: This is a common mapping used in many textbooks.")
    print("      Different sources may group layers slightly differently.\n")


def lookup_osi_layer(user_input):
    """
    Takes user input (layer number or name) and prints the mapped TCP/IP layer.
    """

    # Try to interpret as layer number first
    try:
        num = int(user_input)
        if num in OSI_TO_TCPIP:
            osi_name, tcpip_name = OSI_TO_TCPIP[num]
            print(f"OSI layer {num} ({osi_name}) maps to TCP/IP layer: {tcpip_name}")
            return
        else:
            print("Unknown OSI layer number. Please enter a value from 1 to 7.")
            return
    except ValueError:
        # Not a number, treat as text
        pass

    normalized = user_input.strip().lower()
    # Search by OSI layer name
    for num, (osi_name, tcpip_name) in OSI_TO_TCPIP.items():
        if normalized == osi_name.lower():
            print(f"OSI layer {num} ({osi_name}) maps to TCP/IP layer: {tcpip_name}")
            return
    print("Could not recognize that OSI layer name.")
    print("Try names like: Physical, Data Link, Network, Transport, Session,")
    print("               Presentation, Application, or use numbers 1–7.")

def show_tcpip_layers():
    """Prints the TCP/IP layers and which OSI layers they group."""
    print("TCP/IP layers and grouped OSI layers")
    print("------------------------------------")
    for tcpip_layer, osi_list in TCPIP_LAYERS.items():
        osi_joined = ", ".join(osi_list)
        print(f"{tcpip_layer:<15} ← {osi_joined}")
    print("------------------------------------\n")

# program entry point
if __name__ == "__main__":
    print("=== Task CN07 : OSI vs TCP/IP layer mapper ===\n")
    show_all_mappings()
    show_tcpip_layers()
    while True:
        user_input = input(
            "Enter an OSI layer number (1-7) or name "
            "(or 'q' to quit): "
        )
        if user_input.strip().lower() in ("q", "quit", "exit"):
            print("Exiting the mapper. Goodbye!")
            break
        lookup_osi_layer(user_input)
        print()  # blank line for readability
