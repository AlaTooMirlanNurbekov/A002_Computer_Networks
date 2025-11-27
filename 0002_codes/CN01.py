"""
Task CN01 : OSI layer mapper

Description: I created this taks foy you to understand how data moves through the basic layers
of a network model. The program takes a simple message and shows how it
would conceptually pass through four layers: application, transport,
network, and link.

Concept explained: In real networks, data is not sent directly. It is processed step by step.
Each layer adds its own information before passing the data down to the
next layer. This layered structure is one of the core ideas behind modern
network communication.
"""

def application_layer(message):
    # represents the application preparing data for transmission
    return f"AppData({message})"

def transport_layer(app_data):
    # adds transport-related information such as port numbers
    return f"TransportHeader + {app_data}"

def network_layer(transport_data):
    # adds logical addressing (IP addresses) in real communication
    return f"NetworkHeader + {transport_data}"

def link_layer(network_data):
    # final layer before physical transmission (MAC addresses, frame info)
    return f"LinkHeader + {network_data}"


# program entry point
if __name__ == "__main__":
    message = "Ping request"

    # passing message through layers
    a = application_layer(message)
    t = transport_layer(a)
    n = network_layer(t)
    l = link_layer(n)

    print("Final encapsulated data:")
    print(l)
