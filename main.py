import time, keyboard, sys, tty, termios, re ,io
from gattlib import DiscoveryService, GATTRequester

service = DiscoveryService("hci0")
devices = service.discover(2)

addr = "A4:CF:12:72:64:76"
uuid_service = "0000ffff-0000-1000-8000-00805f9b34fb"
uuid_notify = "0000ff02-0000-1000-8000-00805f9b34fb"
uuid_write = "0000ff01-0000-1000-8000-00805f9b34fb"

handle_name = 0x16
handle_write_request = 0x2B
handle_write = 0x2D

sleep_time = 5

hex_string_reset = "A55A 0240 0205 02C8 9B"
hex_string_move_right = "A55A 0011 05FF B600 FDFF 913B"
hex_string_move_up = "A55A 0011 05FF 0C00 4BFF 4016"
hex_string_move_left = "A55A 0011 05FF 4DFF 1F00 801D"
hex_string_move_down = "A55A 0011 05FF 0300 B600 C3B9"

hex_string_moves = [hex_string_move_right, hex_string_move_up, hex_string_move_left, hex_string_move_down]
hex_strings_moves_literal = ["right", "up", "left", "down"]
def list_handles():
    req = GATTRequester(addr, True)
    j = 0
    while j < 0x2d:
        j_hex = format(j, '#x')
        print('current [%d]\r'%j, end="")
        try:
            steps = req.read_by_handle(j)[0]
            print(j_hex, steps.hex(), steps)
            j+=1
        except:
            j+=1
    req.disconnect()


def find_gimbal():
    found = False
    for address, name in devices.items():
        if address == addr:
            found = True
    return found


def verify_gimbal_name(req):
    # verify G6 gimbal name
    steps = req.read_by_handle(handle_name)[0]
    
    if steps == b'FY_G6_75':
        print("name is correct", steps)
    else:
        print("name not correct", steps.hex())
        exit()
        
def enable_writes(req):
    # enable writes command
    print("enable writes")
    req.write_by_handle(handle_write_request, bytes.fromhex("0100")) 

def reset_gimbal(req):
    # reset command
    print("reset gimbal")
    req.write_cmd(handle_write, bytes.fromhex(hex_string_reset))
       

def test_moves(req):
    # move command 
    i = 0
    j = 100
    while i < j:
        time.sleep(0.4)
        if i < j * 0.25:
            req.write_cmd(handle_write, bytes.fromhex(hex_string_moves[0]))
        elif i < j * 0.5:
            req.write_cmd(handle_write, bytes.fromhex(hex_string_moves[1]))
        elif i < j* 0.75:
            req.write_cmd(handle_write, bytes.fromhex(hex_string_moves[2]))
        else:
            req.write_cmd(handle_write, bytes.fromhex(hex_string_moves[3]))
        i += 1

class LineBuffer(io.StringIO):
    def write(self, s):
        cleaned_output = re.sub(r'(\x1b\[[;\d]*[A-Za-z])', '', s)
        super().write(cleaned_output)

def keyboard_ctrl(req):
    # Save the current terminal settings and stdout
    original_settings = termios.tcgetattr(sys.stdin)
    original_stdout = sys.stdout

    try:
        # Disable local echo and redirect stdout
        tty.setcbreak(sys.stdin.fileno())
        sys.stdout = LineBuffer()

        while True:
            key = sys.stdin.read(1)
            if ord(key) == 27:  # Escape character
                key += sys.stdin.read(2)
                if key == '\x1b[A':  # Up arrow key
                    req.write_cmd(handle_write, bytes.fromhex(hex_string_move_up))
                elif key == '\x1b[B':  # Down arrow key
                    req.write_cmd(handle_write, bytes.fromhex(hex_string_move_down))
                elif key == '\x1b[C':  # Right arrow key
                    req.write_cmd(handle_write, bytes.fromhex(hex_string_move_right))
                elif key == '\x1b[D':  # Left arrow key
                    req.write_cmd(handle_write, bytes.fromhex(hex_string_move_left))
            elif key == 'r':
                reset_gimbal(req)
            elif key == 'q':  # Quit the program
                break

    finally:
        # Restore the original terminal settings and stdout
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_settings)
        sys.stdout = original_stdout

def main():
    if find_gimbal():
        
        req = GATTRequester(addr, True)
            
        enable_writes(req)

        # ~ test_moves(req)
        
        keyboard_ctrl(req)
            
        print("done")
    else:
        print("Device not found in the discovered devices.")


if __name__ == "__main__":
    main()
