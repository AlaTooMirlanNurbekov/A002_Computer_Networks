"""
Task CN25 : educational packet sniffer (mock packet parser)

Description: this is an educational tool that simulates how packet analyzers
like Wireshark interpret raw packet data

You enter a fake hex string representing:
- Ethernet header (14 bytes)
- IPv4 header (minimum 20 bytes)
- TCP or UDP header (first 8–20 bytes)

The program will:
- Validate hex input
- Parse Ethernet MAC addresses
- Parse a simplified IPv4 header
- Parse TCP or UDP header fields
- Print a structured analysis of the packet

Concept explained:
Packet sniffing tools decode raw bytes into meaningful protocol fields.
This program teaches how that decoding works without requiring root/admin
privileges or real traffic capture
"""

import sys


def clean_hex_string(h: str) -> str:
    """Remove spaces and ensure even-length hex."""
    h = h.replace(" ", "").replace("\n", "").replace("\t", "")
    if len(h) % 2 != 0:
        raise ValueError("Hex string must contain an even number of characters.")
    int(h, 16)  # Validate hex
    return h


def hex_to_bytes(h: str) -> bytes:
    """Convert hex string into bytes."""
    return bytes.fromhex(h)


def parse_mac(addr: bytes) -> str:
    """Return MAC address in human-readable form."""
    return ":".join(f"{b:02x}" for b in addr)


def parse_ipv4(addr: bytes) -> str:
    """Return IPv4 address in dotted-decimal."""
    return ".".join(str(b) for b in addr)


def parse_ethernet(frame: bytes) -> dict:
    if len(frame) < 14:
        raise ValueError("Frame must be at least 14 bytes")
    dest = parse_mac(frame[0:6])
    src = parse_mac(frame[6:12])
    ethertype = int.from_bytes(frame[12:14], "big")

    return {
        "dest_mac": dest,
        "src_mac": src,
        "ethertype": f"0x{ethertype:04x}",
        "is_ipv4": ethertype == 0x0800,
    }


def parse_ipv4_header(packet: bytes) -> dict:
    if len(packet) < 20:
        raise ValueError("IPv4 header must be at least 20 bytes")

    version_ihl = packet[0]
    version = version_ihl >> 4
    ihl = (version_ihl & 0x0F) * 4
    ttl = packet[8]
    protocol = packet[9]
    src = parse_ipv4(packet[12:16])
    dst = parse_ipv4(packet[16:20])

    return {
        "version": version,
        "ihl": ihl,
        "ttl": ttl,
        "protocol": protocol,
        "src_ip": src,
        "dst_ip": dst,
    }
def parse_tcp_header(segment: bytes) -> dict:
    if len(segment) < 20:
        raise ValueError("TCP header must be at least 20 bytes")

    src_port = int.from_bytes(segment[0:2], "big")
    dst_port = int.from_bytes(segment[2:4], "big")
    seq = int.from_bytes(segment[4:8], "big")
    ack = int.from_bytes(segment[8:12], "big")
    flags = segment[13]
    flag_list = []
    if flags & 0x01: flag_list.append("FIN")
    if flags & 0x02: flag_list.append("SYN")
    if flags & 0x10: flag_list.append("ACK")

    return {
        "src_port": src_port,
        "dst_port": dst_port,
        "seq": seq,
        "ack": ack,
        "flags": flag_list,
    }

def parse_udp_header(segment: bytes) -> dict:
    if len(segment) < 8:
        raise ValueError("UDP header must be at least 8 bytes")

    src_port = int.from_bytes(segment[0:2], "big")
    dst_port = int.from_bytes(segment[2:4], "big")
    length = int.from_bytes(segment[4:6], "big")

    return {"src_port": src_port, "dst_port": dst_port, "length": length}
def main():
    print("=== Task CN25 : Educational Packet Sniffer (Mock Parser) ===\n")
    print("Enter a raw hex string representing a fake packet.")
    print("At minimum include:")
    print("  - Ethernet header (14 bytes)")
    print("  - IPv4 header (20 bytes)")
    print("Example:\n  ff ff ff ff ff ff aa bb cc dd ee ff 08 00 45 00 00 34 ...\n")

    raw = input("Enter hex string (or 'q' to quit): ").strip()
    if raw.lower() in ("q", "quit", "exit"):
        print("Goodbye!")
        sys.exit()
    try:
        cleaned = clean_hex_string(raw)
        data = hex_to_bytes(cleaned)
    except Exception as e:
        print(f"Invalid hex input: {e}")
        return
    print("\n=== Decoding Ethernet Header ===")
    eth = parse_ethernet(data)
    for k, v in eth.items():
        print(f"{k:15}: {v}")
    if not eth["is_ipv4"]:
        print("\nThis demo only parses IPv4 packets.\n")
        return

    ipv4_offset = 14
    ipv4_header = parse_ipv4_header(data[ipv4_offset:])

    print("\n=== Decoding IPv4 Header ===")
    for k, v in ipv4_header.items():
        print(f"{k:15}: {v}")

    protocol = ipv4_header["protocol"]
    transport_offset = ipv4_offset + ipv4_header["ihl"]

    if protocol == 6:  # TCP
        print("\n=== Decoding TCP Header ===")
        tcp = parse_tcp_header(data[transport_offset:])
        for k, v in tcp.items():
            print(f"{k:15}: {v}")
    elif protocol == 17:  # UDP
        print("\n=== Decoding UDP Header ===")
        udp = parse_udp_header(data[transport_offset:])
        for k, v in udp.items():
            print(f"{k:15}: {v}")
    else:
        print("\nTransport protocol not supported in this demo.\n")

if __name__ == "__main__":
    main()