def validate_ingress(packet):
    if packet.get("source") != "PM_CORE":
        raise ValueError("Invalid ingress source")

    if "receipt" not in packet:
        raise ValueError("Missing receipt")

    return packet