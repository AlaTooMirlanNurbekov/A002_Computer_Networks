"""
Task CN22 : simple TCP reliability & retransmission simulator
Description:
This task simulates how TCP provides reliable delivery on top of an
unreliable network. It does NOT send real packets. Instead, it:

- Splits a short message into segments (like TCP segments with data)
- Assigns sequence numbers to each segment
- "Sends" segments over an unreliable network where some segments are lost
- Uses acknowledgments (ACKs) and timeouts to retransmit lost segments

Concept explained:
TCP guarantees reliable, ordered delivery. If a segment is lost, the sender
does not just give up. It waits for an ACK. If no ACK comes within a timeout,
the sender retransmits the unacknowledged segment.

In this simplified simulator:
- We assume a connection is already established (3-way handshake done).
- We send segments with a fixed amount of data (MSS).
- The network may randomly "drop" a segment.
- The receiver only ACKs correctly received, in-order segments.
- The sender retransmits segments when they time out.
"""
import random
from typing import List, Optional

class Segment:
    """
    Represents a simplified TCP segment with:
    - seq: sequence number
    - data: payload (string)
    """
    def __init__(self, seq: int, data: str):
        self.seq = seq
        self.data = data
    def __repr__(self) -> str:
        return f"Segment(seq={self.seq}, data='{self.data}')"
class UnreliableNetwork:
    """
    A toy "network" that can randomly drop segments
    drop_probability: float between 0.0 and 1.0
    """

    def __init__(self, drop_probability: float = 0.3):
        self.drop_probability = drop_probability
    def send(self, segment: Segment) -> bool:
        """
        Returns True if the segment is delivered to the receiver,
        False if it is "lost" in the network.
        """
        if random.random() < self.drop_probability:
            print(f"  [Network] Segment with SEQ={segment.seq} was LOST ❌")
            return False
        else:
            print(f"  [Network] Segment with SEQ={segment.seq} delivered ✔")
            return True

class TcpReceiver:
    """
    A simplified TCP receiver that:
    - Accepts in-order segments
    - Sends ACK for the next expected sequence number
    """
    def __init__(self):
        self.expected_seq = 0
        self.received_data: List[str] = []
    def receive(self, segment: Segment) -> int:
        """
        Receives a segment.
        If SEQ matches expected_seq, accepts it and increases expected_seq.
        Returns the next expected sequence number (ACK number).
        """
        print(f"  [Receiver] Got segment SEQ={segment.seq}, DATA='{segment.data}'")
        if segment.seq == self.expected_seq:
            self.received_data.append(segment.data)
            self.expected_seq += len(segment.data)
            print(
                f"  [Receiver] Accepted. New next expected SEQ: {self.expected_seq}"
            )
        else:
            print(
                f"  [Receiver] Out-of-order segment. Still expecting SEQ={self.expected_seq}"
            )

        ack_number = self.expected_seq
        print(f"  [Receiver] Sending ACK={ack_number}\n")
        return ack_number
    def reconstructed_message(self) -> str:
        """Returns the reconstructed full message."""
        return "".join(self.received_data)

class TcpSender:
    """
    A simplified TCP sender that:
    - Splits a message into segments
    - Sends segments one by one
    - Waits for ACKs
    - Retransmits when ACK does not advance (simulated timeout)
    """
    def __init__(self, message: str, mss: int = 5):
        self.message = message
        self.mss = mss
        self.segments = self._create_segments()
        self.base_seq = 0  # initial sequence number
        self.unacked_index = 0  # index of first unacknowledged segment
        self.next_seq = 0
    def _create_segments(self) -> List[Segment]:
        """Splits the message into segments with sequential SEQ values."""
        segments: List[Segment] = []
        seq = 0
        for i in range(0, len(self.message), self.mss):
            chunk = self.message[i : i + self.mss]
            segments.append(Segment(seq, chunk))
            seq += len(chunk)
        return segments

    def send_all(self, network: UnreliableNetwork, receiver: TcpReceiver) -> None:
        """
        Sends all segments reliably using stop-and-wait ARQ logic:
        - Send one segment
        - If ACK is not the one we expect (or it doesn't advance), retransmit
        """
        print(f"=== TCP Reliable Data Transfer Simulation ===")
        print(f"Message to send (length {len(self.message)}): '{self.message}'")
        print(f"MSS (max segment size): {self.mss} bytes\n")

        total_segments = len(self.segments)
        current_ack: Optional[int] = 0

        while self.unacked_index < total_segments:
            seg = self.segments[self.unacked_index]
            print(f"[Sender] Sending segment index {self.unacked_index} → SEQ={seg.seq}")

            delivered = network.send(seg)

            if delivered:
                # Delivered, so the receiver will process and send ACK
                ack = receiver.receive(seg)
            else:
                # Not delivered: receiver never sees it, so no ACK.
                print("  [Sender] No ACK received (simulated timeout).")
                ack = current_ack  # no progress

            # Check if ACK advanced
            if ack is not None and ack > (current_ack or 0):
                print(
                    f"[Sender] ACK={ack} received. Segment SEQ={seg.seq} successfully delivered.\n"
                )
                current_ack = ack
                self.unacked_index += 1  # move to next segment
            else:
                print(
                    "[Sender] ACK did not advance. Assuming loss → will retransmit the same segment.\n"
                )
                # In real TCP, a timeout or duplicate ACK logic triggers retransmission.
                # Here, we just loop and send again.

        print("=== All segments successfully delivered. ===")
        print(f"[Receiver] Final reconstructed message: '{receiver.reconstructed_message()}'\n")


def main():
    print("=== Task CN22 : Simple TCP Reliability & Retransmission Simulator ===\n")

    # Ask user for a message or use a default one
    text = input(
        "Enter a short message to send (or press Enter to use a default example): "
    ).strip()
    if not text:
        text = "Hello, TCP world! This is a reliable transfer demo."

    mss_input = input("Enter MSS (max bytes per segment, default 5): ").strip()
    if mss_input.isdigit() and int(mss_input) > 0:
        mss = int(mss_input)
    else:
        mss = 5

    drop_input = input(
        "Enter approximate drop probability between 0.0 and 1.0 (default 0.3): "
    ).strip()
    try:
        drop_prob = float(drop_input)
        if not (0.0 <= drop_prob <= 1.0):
            raise ValueError
    except ValueError:
        drop_prob = 0.3

    print()

    # Initialize components
    network = UnreliableNetwork(drop_probability=drop_prob)
    receiver = TcpReceiver()
    sender = TcpSender(message=text, mss=mss)

    # Run simulation
    sender.send_all(network, receiver)

    print("Simulation finished. You can run it again with different parameters.\n")


# program entry point
if __name__ == "__main__":
    main()
