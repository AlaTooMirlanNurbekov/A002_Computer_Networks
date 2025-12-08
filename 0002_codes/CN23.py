"""
Task CN23 : UDP communication simulator

Description:
This task demonstrates how UDP communication works compared to TCP.
It does NOT send real network traffic. Instead, it simulates:

- A sender that sends datagrams (UDP packets)
- An unreliable network where packets may be delivered, delayed, or lost
- A receiver that receives whatever arrives, without acknowledgments
- No retransmissions, no sequence tracking, no ordering

Concept explained:
UDP is a connectionless, unreliable protocol. Unlike TCP:

- There is no handshake
- No sequence numbers
- No acknowledgments
- No retransmissions
- Packets may arrive out of order or not at all

This simulator makes the differences visible.
"""

import random
import time

class UdpDatagram:
    """
    Represents a UDP datagram with:
    - data: the payload
    - id: a simple identifier
    """

    def __init__(self, datagram_id: int, data: str):
        self.id = datagram_id
        self.data = data

    def __repr__(self) -> str:
        return f"UDPDgram(id={self.id}, data='{self.data}')"


class UnreliableUdpNetwork:
    """
    Simulates an unreliable network for UDP datagrams.
    - drop_probability: chance a packet disappears completely
    - delay_probability: chance a packet is delayed
    """

    def __init__(self, drop_probability: float = 0.2, delay_probability: float = 0.2):
        self.drop_probability = drop_probability
        self.delay_probability = delay_probability

    def transmit(self, datagram: UdpDatagram) -> bool:
        """
        Handles packet transmission.
        Returns True if delivered, False if dropped.
        Delay is simulated by sleeping.
        """
        # Random drop
        if random.random() < self.drop_probability:
            print(f"  [Network] Datagram ID={datagram.id} LOST ❌")
            return False

        # Random artificial delay
        if random.random() < self.delay_probability:
            delay = random.uniform(0.2, 1.0)
            print(f"  [Network] Datagram ID={datagram.id} DELAYED {delay:.2f}s ⏳")
            time.sleep(delay)

        print(f"  [Network] Datagram ID={datagram.id} delivered ✔")
        return True


class UdpSender:
    """
    Sends data chunks as UDP datagrams.
    """

    def __init__(self, message: str):
        self.message = message

    def create_datagrams(self, chunk_size: int):
        """Splits the message into datagrams of size chunk_size."""
        datagrams = []
        idx = 0
        for i in range(0, len(self.message), chunk_size):
            chunk = self.message[i : i + chunk_size]
            datagrams.append(UdpDatagram(idx, chunk))
            idx += 1
        return datagrams

    def send_all(self, network: UnreliableUdpNetwork, receiver, chunk_size: int = 8):
        """
        Sends datagrams without waiting for acknowledgments.
        """
        print(f"=== UDP Communication Simulation ===")
        print(f"Message to send: '{self.message}'")
        print(f"Chunk size: {chunk_size} bytes\n")

        datagrams = self.create_datagrams(chunk_size)

        for d in datagrams:
            print(f"[Sender] Sending datagram ID={d.id}")
            delivered = network.transmit(d)
            if delivered:
                receiver.receive(d)
            else:
                # For UDP, we simply do NOT retransmit.
                print(f"  [Sender] Datagram ID={d.id} lost. UDP will NOT retry.\n")

        print("=== UDP transmission finished (no reliability guaranteed). ===\n")

class UdpReceiver:
    """
    Receives UDP datagrams and prints them in arrival order.
    """

    def __init__(self):
        self.received = []

    def receive(self, datagram: UdpDatagram):
        print(f"  [Receiver] Received datagram ID={datagram.id}, DATA='{datagram.data}'")
        self.received.append(datagram)

    def show_summary(self):
        print("\n=== UDP Receiver Summary ===")
        print(f"Total received: {len(self.received)} datagram(s)")
        print("Arrival order:")
        for d in self.received:
            print(f"  ID={d.id}, DATA='{d.data}'")
        print("\nNote: Missing or out-of-order datagrams are NORMAL in UDP.\n")


def main():
    print("=== Task CN23 : UDP Communication Simulator ===\n")

    text = input(
        "Enter a short message to send via UDP (or press Enter for default): "
    ).strip()
    if not text:
        text = "Hello, UDP! Packets may be lost or delayed."

    chunk_input = input("Enter datagram size (default 8): ").strip()
    if chunk_input.isdigit() and int(chunk_input) > 0:
        chunk_size = int(chunk_input)
    else:
        chunk_size = 8

    drop_input = input("Enter drop probability (0 to 1, default 0.2): ").strip()
    try:
        drop_prob = float(drop_input)
    except ValueError:
        drop_prob = 0.2

    delay_input = input("Enter delay probability (0 to 1, default 0.2): ").strip()
    try:
        delay_prob = float(delay_input)
    except ValueError:
        delay_prob = 0.2

    print()

    network = UnreliableUdpNetwork(drop_probability=drop_prob, delay_probability=delay_prob)
    sender = UdpSender(text)
    receiver = UdpReceiver()

    sender.send_all(network, receiver, chunk_size)
    receiver.show_summary()

# program entry point
if __name__ == "__main__":
    main()
