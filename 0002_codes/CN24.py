"""
Task CN24 : common ports & services helper
Description:
This task is an interactive helper for learning common TCP/UDP ports
It lets you:

- Enter a port number and see which common service(s) use it
- Enter a service name (like 'http', 'dns') and see the default port(s)
- List all known ports in the built-in table

Concept explained:
Many application protocols are associated with "well-known" ports.
For example:
 - HTTP  → 80/tcp
 - HTTPS → 443/tcp
 - DNS   → 53/udp (and sometimes 53/tcp)
Remembering these ports is useful for exams, firewall rules, and troubleshooting
This tool is a quick way to explore and practice them
"""

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PortInfo:
    port: int
    protocol: str  # "tcp", "udp", or "tcp/udp"
    service: str
    description: str

#basic table of common ports and services
COMMON_PORTS: List[PortInfo] = [
    PortInfo(20, "tcp", "ftp-data", "FTP data transfer"),
    PortInfo(21, "tcp", "ftp", "FTP control (file transfer)"),
    PortInfo(22, "tcp", "ssh", "Secure Shell remote login"),
    PortInfo(23, "tcp", "telnet", "Unencrypted remote terminal"),
    PortInfo(25, "tcp", "smtp", "Simple Mail Transfer Protocol"),
    PortInfo(53, "udp", "dns", "Domain Name System (queries)"),
    PortInfo(53, "tcp", "dns", "Domain Name System (zone transfers & some queries)"),
    PortInfo(67, "udp", "dhcp-server", "DHCP server"),
    PortInfo(68, "udp", "dhcp-client", "DHCP client"),
    PortInfo(69, "udp", "tftp", "Trivial File Transfer Protocol"),
    PortInfo(80, "tcp", "http", "Hypertext Transfer Protocol (web)"),
    PortInfo(110, "tcp", "pop3", "Post Office Protocol v3 (mail retrieval)"),
    PortInfo(119, "tcp", "nntp", "Network News Transfer Protocol"),
    PortInfo(123, "udp", "ntp", "Network Time Protocol"),
    PortInfo(143, "tcp", "imap", "Internet Message Access Protocol"),
    PortInfo(161, "udp", "snmp", "Simple Network Management Protocol"),
    PortInfo(162, "udp", "snmp-trap", "SNMP traps/notifications"),
    PortInfo(389, "tcp", "ldap", "Lightweight Directory Access Protocol"),
    PortInfo(443, "tcp", "https", "HTTP over TLS/SSL (secure web)"),
    PortInfo(465, "tcp", "smtps", "SMTP over TLS/SSL"),
    PortInfo(587, "tcp", "submission", "Mail submission (SMTP)"),
    PortInfo(993, "tcp", "imaps", "IMAP over TLS/SSL"),
    PortInfo(995, "tcp", "pop3s", "POP3 over TLS/SSL"),
    PortInfo(1433, "tcp", "mssql", "Microsoft SQL Server"),
    PortInfo(1521, "tcp", "oracle", "Oracle database listener"),
    PortInfo(3306, "tcp", "mysql", "MySQL / MariaDB database"),
    PortInfo(3389, "tcp", "rdp", "Remote Desktop Protocol"),
    PortInfo(4433, "tcp", "test-https", "Example custom HTTPS-like service"),
    PortInfo(5060, "udp", "sip", "Session Initiation Protocol (VoIP)"),
    PortInfo(8080, "tcp", "http-alt", "Alternative HTTP / proxy"),
]

def build_indices(ports: List[PortInfo]):
    """
    Builds helper dictionaries:
    - by_port: port → list of PortInfo
    - by_service: service_name(lowercase) → list of PortInfo
    """
    by_port: Dict[int, List[PortInfo]] = {}
    by_service: Dict[str, List[PortInfo]] = {}

    for entry in ports:
        by_port.setdefault(entry.port, []).append(entry)
        by_service.setdefault(entry.service.lower(), []).append(entry)
    return by_port, by_service


BY_PORT, BY_SERVICE = build_indices(COMMON_PORTS)


def lookup_by_port(port: int) -> List[PortInfo]:
    """
    Returns a list of PortInfo entries matching the given port number.
    There may be multiple entries (different protocols or uses).
    """
    return BY_PORT.get(port, [])

def lookup_by_service(name: str) -> List[PortInfo]:
    """
    Returns a list of PortInfo entries matching the given service name.
    """
    return BY_SERVICE.get(name.lower(), [])

def print_port_infos(infos: List[PortInfo]) -> None:
    """Nicely prints a list of PortInfo entries."""
    if not infos:
        print("  (no entries found)\n")
        return
    for info in infos:
        print(f"  Port      : {info.port}/{info.protocol}")
        print(f"  Service   : {info.service}")
        print(f"  Description: {info.description}")
        print("-" * 40)
    print()

def show_all_ports() -> None:
    """Prints all known ports and services in a compact table."""
    print("\nKnown ports and services:")
    print("-------------------------")
    for info in sorted(COMMON_PORTS, key=lambda x: (x.port, x.protocol)):
        print(f"{info.port:5d}/{info.protocol:<4}  {info.service:<12}  {info.description}")
    print()

def main_menu() -> None:
    """
    Shows the main menu and handles user input.
    """
    while True:
        print("=== Task CN24 : Common Ports & Services Helper ===")
        print("1) Look up by port number")
        print("2) Look up by service name")
        print("3) List all known ports")
        print("4) Exit")
        choice = input("Choose an option (1-4): ").strip()
        if choice == "1":
            handle_lookup_port()
        elif choice == "2":
            handle_lookup_service()
        elif choice == "3":
            show_all_ports()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.\n")

def handle_lookup_port() -> None:
    """
    Asks for a port number and prints matching services.
    """
    raw = input("\nEnter a port number (e.g., 80): ").strip()
    if not raw.isdigit():
        print("Please enter a valid integer port number.\n")
        return
    port = int(raw)
    infos = lookup_by_port(port)

    if not infos:
        print(f"No common service found for port {port}.\n")
    else:
        print(f"\nCommon services for port {port}:")
        print_port_infos(infos)

def handle_lookup_service() -> None:
    """
    Asks for a service name and prints matching ports.
    """
    name = input("\nEnter a service name (e.g., http, dns, ssh): ").strip()
    if not name:
        print("Service name cannot be empty.\n")
        return

    infos = lookup_by_service(name)

    if not infos:
        print(f"No entries found for service '{name}'.\n")
    else:
        print(f"\nCommon ports for service '{name}':")
        print_port_infos(infos)

def main():
    main_menu()

#program entry point
if __name__ == "__main__":
    main()
