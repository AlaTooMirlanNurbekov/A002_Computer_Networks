"""
Task CN31 : DHCP server simulator
Description: this task simulates a very simple DHCP server for an IPv4 LAN.
You can:
- Configure a small IP pool (start/end, subnet mask, gateway, DNS, lease time)
- Request a new lease for a client MAC address (DISCOVER/OFFER/REQUEST/ACK flow)
- Renew an existing lease
- Release an IP address
- Age leases so they expire
- Show all current leases
Concept: In real networks, DHCP servers:
- Keep an address pool (e.g. 192.168.1.100–192.168.1.200)
- When a client broadcasts DHCPDISCOVER, the server replies with DHCPOFFER
- After DHCPREQUEST from client, server confirms with DHCPACK
- Leases have a timer. If the client does not renew, the address returns to the pool.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
try:
    # Reuse from previous tasks if available
    from CN10 import is_valid_ipv4  # type: ignore
except ImportError:
    def is_valid_ipv4(ip: str) -> bool:
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        try:
            nums = [int(p) for p in parts]
        except ValueError:
            return False
        return all(0 <= n <= 255 for n in nums)

def ip_to_int(ip: str) -> int:
    parts = [int(p) for p in ip.split(".")]
    value = 0
    for p in parts:
        value = (value << 8) | p
    return value

def int_to_ip(value: int) -> str:
    return ".".join(str((value >> (8 * i)) & 0xFF) for i in range(3, -1, -1))


def in_range(ip: str, start: str, end: str) -> bool:
    """Check if IP is between start and end inclusive."""
    ip_i = ip_to_int(ip)
    s_i = ip_to_int(start)
    e_i = ip_to_int(end)
    return s_i <= ip_i <= e_i

# data structures
@dataclass
class DHCPLease:
    ip: str
    mac: str
    ttl: int  # seconds remaining
    state: str  # "active", "expired", "released"
class DHCPServer:
    def __init__(
        self,
        pool_start: str = "192.168.1.100",
        pool_end: str = "192.168.1.150",
        subnet_mask: str = "255.255.255.0",
        gateway: str = "192.168.1.1",
        dns_server: str = "8.8.8.8",
        lease_time: int = 3600,
    ):
        # Basic configuration
        self.pool_start = pool_start
        self.pool_end = pool_end
        self.subnet_mask = subnet_mask
        self.gateway = gateway
        self.dns_server = dns_server
        self.lease_time = lease_time

        # IP -> DHCPLease
        self.leases: Dict[str, DHCPLease] = {}

    def set_pool(self, start: str, end: str):
        if not (is_valid_ipv4(start) and is_valid_ipv4(end)):
            raise ValueError("Pool start/end must be valid IPv4 addresses.")
        if ip_to_int(start) > ip_to_int(end):
            raise ValueError("Pool start must be <= pool end.")
        self.pool_start = start
        self.pool_end = end
    def set_options(self, subnet_mask: str, gateway: str, dns_server: str, lease_time: int):
        if not is_valid_ipv4(subnet_mask):
            raise ValueError("Invalid subnet mask.")
        if not is_valid_ipv4(gateway):
            raise ValueError("Invalid gateway IP.")
        if not is_valid_ipv4(dns_server):
            raise ValueError("Invalid DNS server IP.")
        if lease_time <= 0:
            raise ValueError("Lease time must be positive.")

        self.subnet_mask = subnet_mask
        self.gateway = gateway
        self.dns_server = dns_server
        self.lease_time = lease_time

    def _find_existing_lease_by_mac(self, mac: str) -> Optional[DHCPLease]:
        for lease in self.leases.values():
            if lease.mac.lower() == mac.lower() and lease.state == "active":
                return lease
        return None

    def _find_free_ip(self) -> Optional[str]:
        """
        Returns a free IP in the pool or None if none left.
        IP is free if:
        - Not in leases at all
        - Or exists but state != active
        """
        start_i = ip_to_int(self.pool_start)
        end_i = ip_to_int(self.pool_end)

        for ip_i in range(start_i, end_i + 1):
            candidate = int_to_ip(ip_i)
            lease = self.leases.get(candidate)
            if lease is None or lease.state != "active":
                return candidate
        return None

    def request_lease(self, mac: str) -> Optional[DHCPLease]:
        """
        Simulate DISCOVER/OFFER/REQUEST/ACK for a client MAC.
        Returns the lease or None if no address available.
        """
        #if client already has an active lease, renew and return same IP
        existing = self._find_existing_lease_by_mac(mac)
        if existing:
            existing.ttl = self.lease_time
            existing.state = "active"
            return existing
        free_ip = self._find_free_ip()
        if not free_ip:
            return None

        lease = DHCPLease(ip=free_ip, mac=mac.lower(), ttl=self.lease_time, state="active")
        self.leases[free_ip] = lease
        return lease

    def renew_lease(self, mac: str) -> Optional[DHCPLease]:
        lease = self._find_existing_lease_by_mac(mac)
        if not lease:
            return None
        lease.ttl = self.lease_time
        lease.state = "active"
        return lease
    def release_ip(self, ip: str) -> bool:
        lease = self.leases.get(ip)
        if not lease:
            return False
        lease.state = "released"
        lease.ttl = 0
        return True

    def age_leases(self, seconds: int):
        for lease in self.leases.values():
            if lease.state == "active":
                lease.ttl -= seconds
                if lease.ttl <= 0:
                    lease.ttl = 0
                    lease.state = "expired"

    # Display
    def print_config(self):
        print("\nDHCP Server Configuration")
        print("-------------------------")
        print(f"Pool start   : {self.pool_start}")
        print(f"Pool end     : {self.pool_end}")
        print(f"Subnet mask  : {self.subnet_mask}")
        print(f"Gateway      : {self.gateway}")
        print(f"DNS server   : {self.dns_server}")
        print(f"Lease time   : {self.lease_time} seconds\n")

    def print_leases(self):
        if not self.leases:
            print("\nNo leases yet.\n")
            return
        print("\nCurrent DHCP Leases")
        print("-------------------")
        print(f"{'IP address':<16} {'MAC address':<18} {'TTL':<8} State")
        print("-" * 55)
        for lease in sorted(self.leases.values(), key=lambda l: ip_to_int(l.ip)):
            print(f"{lease.ip:<16} {lease.mac:<18} {lease.ttl:<8} {lease.state}")
        print()

#interactive CLI
def print_menu():
    print("=== Task CN31 : DHCP Server Simulator ===")
    print("1) Show DHCP config")
    print("2) Change DHCP pool & options")
    print("3) Show current leases")
    print("4) Request/obtain lease for a client (MAC)")
    print("5) Renew lease for a client (MAC)")
    print("6) Release an IP address")
    print("7) Simulate time passing (age leases)")
    print("8) Exit")

def handle_change_config(server: DHCPServer):
    print("\nChange DHCP pool & options")
    print("--------------------------")
    start = input(f"Pool start IP [{server.pool_start}]: ").strip()
    end = input(f"Pool end IP   [{server.pool_end}]: ").strip()
    mask = input(f"Subnet mask   [{server.subnet_mask}]: ").strip()
    gw = input(f"Gateway IP    [{server.gateway}]: ").strip()
    dns = input(f"DNS server    [{server.dns_server}]: ").strip()
    lease_raw = input(f"Lease time (seconds) [{server.lease_time}]: ").strip()

    if not start:
        start = server.pool_start
    if not end:
        end = server.pool_end
    if not mask:
        mask = server.subnet_mask
    if not gw:
        gw = server.gateway
    if not dns:
        dns = server.dns_server
    if not lease_raw:
        lease_time = server.lease_time
    else:
        if not lease_raw.isdigit():
            print("Lease time must be a positive integer.\n")
            return
        lease_time = int(lease_raw)

    try:
        server.set_pool(start, end)
        server.set_options(mask, gw, dns, lease_time)
        print("DHCP configuration updated.\n")
    except ValueError as e:
        print(f"Error updating config: {e}\n")

def handle_request_lease(server: DHCPServer):
    print("\nRequest new lease")
    print("-----------------")
    mac = input("Enter client MAC address (any string, e.g. aa:bb:cc:dd:ee:ff): ").strip()
    if not mac:
        print("MAC address cannot be empty.\n")
        return

    #simulate DHCPDISCOVER / DHCPOFFER / DHCPREQUEST / DHCPACK
    print("\n[Client]  → DHCPDISCOVER (broadcast)")
    print("[Server]  → DHCPOFFER (proposing an IP if available)")
    lease = server.request_lease(mac)
    if not lease:
        print("[Server]  No IP addresses left in pool. OFFER failed.")
        print("[Client]  No lease obtained.\n")
        return

    print(f"[Server]  Offered IP: {lease.ip}")
    print("[Client]  → DHCPREQUEST (I want this IP)")
    print("[Server]  → DHCPACK (lease granted)\n")
    print("Lease details:")
    server.print_leases()

def handle_renew_lease(server: DHCPServer):
    print("\nRenew lease")
    print("-----------")
    mac = input("Enter client MAC address: ").strip()
    if not mac:
        print("MAC cannot be empty.\n")
        return

    lease = server.renew_lease(mac)
    if not lease:
        print("No active lease found for this MAC.\n")
    else:
        print(f"Lease for IP {lease.ip} renewed. TTL reset to {lease.ttl} seconds.\n")


def handle_release_ip(server: DHCPServer):
    print("\nRelease IP")
    print("----------")
    ip = input("Enter IP to release: ").strip()
    if not is_valid_ipv4(ip):
        print("Invalid IP address.\n")
        return

    if not in_range(ip, server.pool_start, server.pool_end):
        print("This IP is not in the DHCP pool range.\n")
        return

    success = server.release_ip(ip)
    if success:
        print(f"IP {ip} released. It can be reused in future leases.\n")
    else:
        print("No lease found for this IP.\n")

def handle_age_leases(server: DHCPServer):
    print("\nSimulate time passing")
    print("---------------------")
    raw = input("Enter number of seconds to age: ").strip()
    if not raw.isdigit():
        print("Please enter a positive integer.\n")
        return

    seconds = int(raw)
    if seconds <= 0:
        print("Seconds must be > 0.\n")
        return

    server.age_leases(seconds)
    print(f"Aged leases by {seconds} seconds.")
    print("Some leases might have expired.\n")

def main():
    #default  configuration
    dhcp = DHCPServer()
    while True:
        print_menu()
        choice = input("Choose an option (1–8): ").strip()
        if choice == "1":
            dhcp.print_config()
        elif choice == "2":
            handle_change_config(dhcp)
        elif choice == "3":
            dhcp.print_leases()
        elif choice == "4":
            handle_request_lease(dhcp)
        elif choice == "5":
            handle_renew_lease(dhcp)
        elif choice == "6":
            handle_release_ip(dhcp)
        elif choice == "7":
            handle_age_leases(dhcp)
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1–8.\n")

# program entry point
if __name__ == "__main__":
    main()
