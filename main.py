import time, sys, tty, termios, re, io
from gattlib import DiscoveryService, GATTRequester

ADDRESS = "A4:CF:12:72:64:76"
HANDLE_NAME = 0x16
HANDLE_WRITE_REQUEST = 0x2B
HANDLE_WRITE = 0x2D

HEX_STR_RESET = "A55A 0240 0205 02C8 9B"
HEX_STR_MOVE = {
    "right": "A55A 0011 05FF B600 FDFF 913B",
    "up": "A55A 0011 05FF 0C00 4BFF 4016",
    "left": "A55A 0011 05FF 4DFF 1F00 801D",
    "down": "A55A 0011 05FF 0300 B600 C3B9"
}

def discover_devices():
    service = DiscoveryService("hci0")
    return service.discover(2)

def gimbal_found(devices):
    return any(address == ADDRESS for address in devices)

def enable_writes(requester):
    print("Enable writes")
    requester.write_by_handle(HANDLE_WRITE_REQUEST, bytes.fromhex("0100"))

def reset_gimbal(requester):
    print("Reset gimbal")
    requester.write_cmd(HANDLE_WRITE, bytes.fromhex(HEX_STR_RESET))

class CleanOutput(io.StringIO):
    def write(self, s):
        cleaned_output = re.sub(r'(\x1b\[[;\d]*[A-Za-z])', '', s)
        super().write(cleaned_output)

def keyboard_control(requester):
    original_settings = termios.tcgetattr(sys.stdin)
    original_stdout = sys.stdout

    try:
        tty.setcbreak(sys.stdin.fileno())
        sys.stdout = CleanOutput()

        print("Use arrow keys to control the gimbal. Press 'q' to quit.")
        
        while True:
            key = sys.stdin.read(1)
            if ord(key) == 27:
                key += sys.stdin.read(2)
                arrow_keys = ['\x1b[A', '\x1b[B', '\x1b[C', '\x1b[D']
                directions = ["up", "down", "right", "left"]
                if key in arrow_keys:
                    direction = directions[arrow_keys.index(key)]
                    requester.write_cmd(HANDLE_WRITE, bytes.fromhex(HEX_STR_MOVE[direction]))
            elif key == 'r':
                reset_gimbal(requester)
            elif key == 'q':
                break

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_settings)
        sys.stdout = original_stdout

def main():
    devices = discover_devices()
    if gimbal_found(devices):
        requester = GATTRequester(ADDRESS, True)
        enable_writes(requester)
        keyboard_control(requester)
        print("Done")
    else:
        print("Gimbal not found in the discovered devices.")

if __name__ == "__main__":
    main()
