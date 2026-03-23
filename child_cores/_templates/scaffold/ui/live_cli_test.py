from ..execution.run import run
from .live_test_packet import build_packet
from .cli_renderer import render

def main():
    packet = build_packet()
    output = run(packet)
    render(output)

if __name__ == "__main__":
    main()