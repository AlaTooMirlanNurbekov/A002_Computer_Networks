"""
Task CN27 : DNS query resolver simulation

Description:
This task simulates how DNS resolution works WITHOUT using the internet
- How a DNS query is formed
- How recursive resolution works
- How DNS records (A, AAAA, CNAME, MX) are searched
- How caching speeds up future lookups
- How failures occur (NXDOMAIN, timeout)

This is a full teaching simulator — perfect for students to understand DNS
step by step, without requiring real DNS or external libraries.

The simulator contains a built-in "fake DNS database" with zones and records.
- Query domains like "google.com", "mail.example.com"
- Inspect how the resolver walks through CNAME chains
- View cache content
- Clear the cache
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

# ------------------------------
# DNS RECORD DEFINITIONS
# ------------------------------
@dataclass
class ARecord:
    name: str
    address: str

@dataclass
class AAAARecord:
    name: str
    address: str

@dataclass
class CNAMERecord:
    name: str
    alias_to: str

@dataclass
class MXRecord:
    name: str
    priority: int
    mail_server: str

# ------------------------------
# FAKE DNS DATABASE
# ------------------------------
FAKE_DNS_DB = {
    "google.com": {
        "A": [ARecord("google.com", "142.250.190.78")],
        "AAAA": [AAAARecord("google.com", "2a00:1450:4009:80b::200e")],
        "MX": [MXRecord("google.com", 10, "smtp.google.com")],
        "CNAME": [],
    },
    "smtp.google.com": {
        "A": [ARecord("smtp.google.com", "74.125.140.27")],
        "AAAA": [],
        "MX": [],
        "CNAME": [],
    },
    "example.com": {
        "A": [ARecord("example.com", "93.184.216.34")],
        "AAAA": [],
        "MX": [MXRecord("example.com", 20, "mail.example.com")],
        "CNAME": [],
    },
    "mail.example.com": {
        "A": [ARecord("mail.example.com", "93.184.216.40")],
        "AAAA": [],
        "CNAME": [],
        "MX": [],
    },
    "api.service.com": {
        "A": [],
        "AAAA": [],
        "CNAME": [CNAMERecord("api.service.com", "backend.service.com")],
        "MX": [],
    },
    "backend.service.com": {
        "A": [ARecord("backend.service.com", "10.20.30.40")],
        "AAAA": [],
        "CNAME": [],
        "MX": [],
    },
}


# ------------------------------
# DNS CACHE
# ------------------------------

class DNSCache:
    def __init__(self):
        self.cache: Dict[str, Dict[str, List]] = {}

    def get(self, name: str):
        return self.cache.get(name)

    def store(self, name: str, records: Dict[str, List]):
        self.cache[name] = records

    def clear(self):
        self.cache.clear()

    def print_cache(self):
        if not self.cache:
            print("\n(Cache is empty)\n")
            return
        print("\n=== DNS Cache ===")
        for domain, data in self.cache.items():
            print(f"\n{domain}:")
            for k, v in data.items():
                print(f"  {k}: {v}")
        print()


DNS_CACHE = DNSCache()


# ------------------------------
# DNS RESOLUTION LOGIC
# ------------------------------
def resolve(domain: str, record_type: str = "A", depth: int = 0):
    """
    Resolve a DNS query with:
    - Cache check
    - CNAME following
    - Fake database lookup
    """

    indent = "  " * depth
    print(f"{indent}Resolving {domain} ({record_type}) ...")

    # 1. check cache first
    cached = DNS_CACHE.get(domain)
    if cached:
        print(f"{indent}→ Cache HIT for {domain}")
        if cached.get(record_type):
            return cached[record_type]
        # continue to deeper resolution if needed (e.g., CNAME chain)

    # 2.zone exists?
    zone = FAKE_DNS_DB.get(domain)
    if not zone:
        print(f"{indent}→ NXDOMAIN: No such domain")
        return None

    # 3. CNAME handling
    if zone["CNAME"]:
        cname_rec = zone["CNAME"][0]  # only one for simplicity
        print(f"{indent}→ CNAME found: {domain} → {cname_rec.alias_to}")
        result = resolve(cname_rec.alias_to, record_type, depth + 1)
        if result:
            DNS_CACHE.store(domain, {record_type: result})
        return result

    # 4.Direct record lookup
    result = zone.get(record_type)
    if result:
        print(f"{indent}→ Found {record_type} record(s) for {domain}")
        DNS_CACHE.store(domain, {record_type: result})
        return result

    print(f"{indent}→ No {record_type} record found.")
    return None


# ------------------------------
# INTERACTIVE MENU
# ------------------------------
def print_menu():
    print("\n=== Task CN27 : DNS Query Resolver Simulation ===")
    print("1) Query A record")
    print("2) Query AAAA record")
    print("3) Query CNAME")
    print("4) Query MX")
    print("5) Show DNS cache")
    print("6) Clear cache")
    print("7) Exit")

def query_record(record_type: str):
    domain = input(f"\nEnter domain to query {record_type}: ").strip().lower()
    answer = resolve(domain, record_type)
    print("\n=== Answer ===")
    if not answer:
        print("No records found.\n")
    else:
        for rec in answer:
            print(rec)
        print()

def main():
    while True:
        print_menu()
        choice = input("Choose an option (1–7): ").strip()
        if choice == "1":
            query_record("A")
        elif choice == "2":
            query_record("AAAA")
        elif choice == "3":
            query_record("CNAME")
        elif choice == "4":
            query_record("MX")
        elif choice == "5":
            DNS_CACHE.print_cache()
        elif choice == "6":
            DNS_CACHE.clear()
            print("\nCache cleared.\n")
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.\n")

if __name__ == "__main__":
    main()
