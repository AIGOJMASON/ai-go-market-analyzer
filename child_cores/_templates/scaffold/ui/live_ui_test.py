from ..execution.run import run
from .live_test_packet import build_packet
from .ui_payload_builder import build_payload

def main():
    packet = build_packet()
    output = run(packet)
    payload = build_payload(output)
    print(payload)

if __name__ == "__main__":
    main()