"""
Task CN08 : layered path explainer

Description: this task explains which layers and protocols are involved when you perform
common network actions such as browsing a website, sending an email, resolving
a domain name, or transferring a file

Concept explained: every network activity touches multiple layers of the TCP/IP model. For example,
web browsing uses HTTP (application layer), TCP (transport layer), IP (network layer),
and Ethernet/Wi-Fi (network access layer). This program helps you understand that
different actions rely on different protocols at different layers
"""

ACTIONS = {
    "web": {
        "name": "Web Browsing",
        "application": ["HTTP", "HTTPS"],
        "transport": ["TCP (port 80/443)"],
        "network": ["IP (IPv4/IPv6)"],
        "link": ["Ethernet", "Wi-Fi"],
    },
    "email": {
        "name": "Email Sending",
        "application": ["SMTP (sending)", "IMAP", "POP3 (receiving)"],
        "transport": ["TCP"],
        "network": ["IP"],
        "link": ["Ethernet", "Wi-Fi"],
    },
    "dns": {
        "name": "DNS Lookup",
        "application": ["DNS"],
        "transport": ["UDP (mostly)", "TCP (for large responses)"],
        "network": ["IP"],
        "link": ["Ethernet", "Wi-Fi"],
    },
    "file": {
        "name": "File Transfer",
        "application": ["FTP", "SFTP", "HTTP download"],
        "transport": ["TCP"],
        "network": ["IP"],
        "link": ["Ethernet", "Wi-Fi"],
    },
}


def explain_action(action_key):
    """Prints the layered explanation for the chosen network activity."""

    action = ACTIONS[action_key]

    print(f"\n=== {action['name']} ===")
    print("Application layer:")
    for proto in action["application"]:
        print(f" - {proto}")

    print("Transport layer:")
    for proto in action["transport"]:
        print(f" - {proto}")

    print("Network layer:")
    for proto in action["network"]:
        print(f" - {proto}")

    print("Network Access layer:")
    for proto in action["link"]:
        print(f" - {proto}")

    print("----------------------------------------")
    print("This is the layered stack used during this activity.\n")


def show_menu():
    """Displays the available network actions."""
    print("Choose a network activity to explore:")
    print("  1 - Web browsing")
    print("  2 - Email sending")
    print("  3 - DNS lookup")
    print("  4 - File transfer")
    print("  q - Quit")
    print("----------------------------------------")


# Program entry point
if __name__ == "__main__":
    print("=== Task CN08 : Layered Path Explainer ===\n")

    while True:
        show_menu()
        choice = input("Enter your choice: ").strip().lower()

        if choice == "1":
            explain_action("web")
        elif choice == "2":
            explain_action("email")
        elif choice == "3":
            explain_action("dns")
        elif choice == "4":
            explain_action("file")
        elif choice in ("q", "quit", "exit"):
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.\n")
