"""
Task CN03 : simple packet builder
Description: This task demonstrates how a basic packet can be represented in code.
You enter source and destination information, and the program builds
a simple text-based packet that shows how data is wrapped together.
Concept explained: Real network packets contain multiple headers (link, network, transport)
and then the actual data. Here you create a very simplified version of
a packet to understand the idea of combining addressing information with
the message before sending it across the network.
"""

def build_packet(src_ip, dst_ip, src_port, dst_port, payload):
    # simplified conceptual packet structure (not real protocol format)
    packet = {
        "source_ip": src_ip,
        "destination_ip": dst_ip,
        "source_port": src_port,
        "destination_port": dst_port,
        "data": payload
    }
    return packet
# program entry point
if __name__ == "__main__":
    # example values
    src_ip = "192.168.0.10"
    dst_ip = "172.16.5.20"
    src_port = 5000
    dst_port = 80
    message = "GET /index.html"
    packet = build_packet(src_ip, dst_ip, src_port, dst_port, message)
    print("Packet created:")
    print(packet)

