"""
Task CN02 : port and service helper

Description: This task helps you connect port numbers with common network services.
The program asks you to enter a port number and then shows which well-known
service usually uses that port (for example, 80 → HTTP, 443 → HTTPS).

Concept explained: Transport layer protocols such as TCP and UDP use port numbers to identify
which application should handle incoming data. Certain ports are considered
"well-known" and are commonly associated with specific services. By learning
these, you start to recognize patterns when reading network diagrams,
firewall rules, or packet captures.
"""

def get_service_name(port):
    # minimal list of common well-known ports
    port_map = {
        20: "FTP (data)",
        21: "FTP (control)",
        22: "SSH",
        23: "Telnet",
        25: "SMTP (email)",
        53: "DNS",
        80: "HTTP (web)",
        110: "POP3 (email)",
        143: "IMAP (email)",
        443: "HTTPS (secure web)",
        3389: "RDP (remote desktop)"
    }

    return port_map.get(port, "unknown or not in this simple list")


# program entry point
if __name__ == "__main__":
    try:
        user_input = input("Enter a TCP/UDP port number: ")
        port = int(user_input)

        service = get_service_name(port)

        print(f"Port: {port}")
        print(f"Common service: {service}")
        print("Note: in real networks, many other ports and services exist.")

    except ValueError:
        print("Please enter a valid integer port number.")
