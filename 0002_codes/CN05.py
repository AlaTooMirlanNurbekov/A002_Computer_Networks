"""
Task CN05 : encapsulation visualizer
Description: This task helps you visualize how encapsulation works in a layered
network model. You give a simple message, and the program shows how each
layer adds its own header around the data: application → transport → network → link
Concept explained: In real networks, data is encapsulated step by step. Each layer
adds its own control information (headers, and sometimes trailers) before
passing the data to the next layer. By seeing how the original message is
wrapped at every step, you build an intuition for what "encapsulation"
really means when people talk about frames, packets, and segments
"""

def encapsulate_data(message):
    """
    Takes a plain message and returns a dictionary representing
    the encapsulated data at each layer.
    """
    # Application layer: user data
    application_data = f"APP_DATA({message})"
    # Transport layer: add a simple "transport header"
    transport_segment = f"TP_HDR | {application_data}"
    # Network layer: add a simple "network header"
    network_packet = f"NW_HDR | {transport_segment}"
    # Link layer: add a simple "link header" and "link trailer"
    link_frame = f"LK_HDR | {network_packet} | LK_TRL"
    return {
        "application": application_data,
        "transport": transport_segment,
        "network": network_packet,
        "link": link_frame,
    }

def show_encapsulation(steps):
    """
    Nicely prints the encapsulation steps from application down to link.
    """
    print("Encapsulation steps (top → bottom):")
    print("-----------------------------------")
    print(f"Application layer: {steps['application']}")
    print(f"Transport  layer: {steps['transport']}")
    print(f"Network    layer: {steps['network']}")
    print(f"Link       layer: {steps['link']}")
    print("-----------------------------------")
    print("Notice how each layer wraps the previous data with its own header.")
    print("In real networks, these headers contain control information,")
    print("such as ports, IP addresses, and MAC addresses.")

# program entry point
if __name__ == "__main__":
    # You can change this message or later let the user input a message.
    user_message = "Request: send file"
    encapsulated = encapsulate_data(user_message)
    show_encapsulation(encapsulated)
