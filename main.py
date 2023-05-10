import time
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
       

def main():
    if find_gimbal():
        
        req = GATTRequester(addr, True)
            
        enable_writes(req)
        # ~ print("sleep %s sec" % sleep_time)
        # ~ time.sleep(sleep_time)
        
        # ~ reset_gimbal(req)
        # ~ print("sleep %s sec" % sleep_time)
        # ~ time.sleep(sleep_time)   
             
        # move command 
        i = 0
        j = 100
        while i < j:
            time.sleep(0.5)
            if i < j * 0.25:
                req.write_cmd(handle_write, bytes.fromhex(hex_string_moves[0]))
            elif i < j * 0.5:
                req.write_cmd(handle_write, bytes.fromhex(hex_string_moves[1]))
            elif i < j* 0.75:
                req.write_cmd(handle_write, bytes.fromhex(hex_string_moves[2]))
            else:
                req.write_cmd(handle_write, bytes.fromhex(hex_string_moves[3]))
            i += 1
            
        
        print("done")
    else:
        print("Device not found in the discovered devices.")


if __name__ == "__main__":
    main()
