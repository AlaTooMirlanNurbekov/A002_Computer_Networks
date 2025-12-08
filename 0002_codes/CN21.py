"""
Task CN21 : TCP 3-way handshake simulator

Description:
This task simulates the TCP 3-way handshake between a client and a server.
It does NOT send real network traffic. Instead, it prints each step of
the handshake with sequence (SEQ) and acknowledgment (ACK) numbers.

You can:
- Choose an initial client sequence number
- Watch how SYN, SYN+ACK, and ACK are exchanged
- See how a TCP connection is established conceptually

Concept explained:
TCP is a connection-oriented protocol. Before sending data, the client and
server perform a 3-way handshake:

  1) Client → Server:  SYN, SEQ = x
  2) Server → Client:  SYN+ACK, SEQ = y, ACK = x+1
  3) Client → Server:  ACK, SEQ = x+1, ACK = y+1

After this, both sides consider the connection "established" and are ready
to send data reliably using sequence and acknowledgment numbers.
"""

import random

def simulate_handshake(initial_client_seq: int | None = None) -> None:
    """
    Simulates a TCP 3-way handshake and prints each step.

    If initial_client_seq is None, a random 32-bit sequence number is chosen.
    """
    print("=== TCP 3-Way Handshake Simulation ===\n")
    if initial_client_seq is None:
        client_isn = random.randint(0, 2**32 - 1)
        print(f"[Info] Random client initial sequence number (ISN) chosen: {client_isn}")
    else:
        client_isn = initial_client_seq
        print(f"[Info] Client initial sequence number (ISN) set by you: {client_isn}")
    #for simplicity, choose a random server ISN as well.
    server_isn = random.randint(0, 2**32 - 1)
    print(f"[Info] Server initial sequence number (ISN): {server_isn}\n")

    # Step 1: Client sends SYN
    print("Step 1: Client → Server")
    print("  Client sends:")
    print("    Flags : SYN")
    print(f"    SEQ   : {client_isn}")
    print("    ACK   : (not set)")
    print()

    # Step 2: Server replies with SYN+ACK
    print("Step 2: Server → Client")
    print("  Server receives client's SYN and replies with:")
    print("    Flags : SYN, ACK")
    print(f"    SEQ   : {server_isn}")
    print(f"    ACK   : {client_isn + 1}  (client ISN + 1)")
    print()

    # Step 3: Client sends final ACK
    print("Step 3: Client → Server")
    print("  Client receives server's SYN+ACK and replies with:")
    print("    Flags : ACK")
    print(f"    SEQ   : {client_isn + 1}")
    print(f"    ACK   : {server_isn + 1}  (server ISN + 1)")
    print()

    print("Result:")
    print("-------")
    print("The TCP connection is now ESTABLISHED.")
    print("Both sides agreed on initial sequence numbers and are ready to")
    print("exchange data segments reliably.\n")


def ask_initial_seq() -> int | None:
    """
    Asks the user if they want to choose a specific initial sequence number.
    Returns an integer or None if the user prefers a random value.
    """
    while True:
        choice = input(
            "Do you want to enter a custom client initial sequence number? (y/n): "
        ).strip().lower()

        if choice in ("n", "no"):
            return None
        elif choice in ("y", "yes"):
            value = input("Enter a non-negative integer (e.g., 1000): ").strip()
            if not value.isdigit():
                print("Please enter a valid non-negative integer.\n")
                continue
            return int(value)
        else:
            print("Please answer with 'y' or 'n'.\n")


def main():
    print("=== Task CN21 : TCP 3-Way Handshake Simulator ===\n")

    while True:
        custom_seq = ask_initial_seq()
        print()
        simulate_handshake(custom_seq)

        again = input("Simulate another handshake? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            print("Goodbye!")
            break
        print()

# program entry point
if __name__ == "__main__":
    main()
