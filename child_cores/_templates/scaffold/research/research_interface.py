def accept(packet):
    if packet.get("source") != "PM_CORE":
        raise ValueError("Invalid research source")
    return packet