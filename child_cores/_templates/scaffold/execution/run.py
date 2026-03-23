from .ingress_processor import validate_ingress

def run(packet):
    validated = validate_ingress(packet)

    return {
        "status": "ok",
        "core_id": "{{CORE_ID}}"
    }