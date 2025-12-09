"""
Task CN00 : hello packet world
Description: This is an introductory task for the Computer Networks coding folder.
The purpose is to show the basic idea of sending a message from one device to another.
The program simulates the simplest form of communication: sender → medium → receiver.

Concept explained: Before dealing with real protocols and packet headers, you should understand
the flow of data. Even a basic print-based “simulation” helps visualize the idea
that data travels through steps before it reaches another device.
"""
def send_message(sender, receiver, message):
    # simple conceptual demonstration of transferring a message
    print(f"{sender} wants to send a message to {receiver}...")
    print("Preparing message...")
    print("Placing data on the network medium...")
    print("Transmitting...")
    print("Message delivered!")
    print(f"{receiver} received: {message}")


# program entry point
if __name__ == "__main__":
    sender_device = "PC_A"
    receiver_device = "PC_B"
    data = "Hello, packet world!"

    send_message(sender_device, receiver_device, data)

