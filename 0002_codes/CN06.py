"""
Task CN06 : decapsulation visualizer
Description: it shows how decapsulation works when data travels from the physical/link
layer upward to the application layer. You start with a fully wrapped "frame"
and the program removes each header step-by-step: link → network → transport → application

Concept explained: decapsulation is the reverse of encapsulation. When data reaches the receiver,
each layer removes its own header and passes the remaining data upward.
This task helps you understand how frames become packets, packets become segments,
and finally how segments reveal the original application data
"""

def decapsulate_data(link_frame):
    """
    Takes a fully wrapped link-layer frame and simulates removing headers
    layer by layer.
    """

    print("Decapsulation steps (bottom → top):")
    print("-----------------------------------")
    print(f"Received frame: {link_frame}")

    # Remove Link header and trailer
    without_link = link_frame.replace("LK_HDR | ", "").replace(" | LK_TRL", "")
    print(f"After removing Link layer: {without_link}")

    # Remove Network header
    without_network = without_link.replace("NW_HDR | ", "")
    print(f"After removing Network layer: {without_network}")

    # Remove Transport header
    without_transport = without_network.replace("TP_HDR | ", "")
    print(f"After removing Transport layer: {without_transport}")

    # What remains is the application data
    application_data = without_transport
    print(f"Application layer data: {application_data}")
    print("-----------------------------------")
    print("This is how a receiver unwraps the data layer by layer!")


# program entry point
if __name__ == "__main__":
    # This input mirrors the structure produced by CN05
    sample_frame = "LK_HDR | NW_HDR | TP_HDR | APP_DATA(Request: send file) | LK_TRL"

    decapsulate_data(sample_frame)
