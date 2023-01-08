import asyncio
import board
import keypad
import busio

import statemachine

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
# from adafruit_bluefruit_connect.packet import Packet
ble = BLERadio()
uart_service = UARTService()
advertisement = ProvideServicesAdvertisement(uart_service)

async def ble_connetor():
    while True:
        if not ble.connected:
            # Advertise when not connected.
            ble.stop_advertising()
            ble.start_advertising(advertisement)
        await asyncio.sleep(10)

msg = ""
flow = {}
async def ble_listener():
    global msg, flow
    while True:
        if ble.connected:
            if uart_service.in_waiting:
                line = uart_service.readline()
                if line:
                    # print("full", line.decode('utf-8'))
                    msg += line[:-1].decode('utf-8')
                    # print(line[-1:])
                    if line[-1:] == b'\x03': #EOT code 3
                        # print("last part", msg)
                        with open("/recent_data.json", "w") as fp2:
                            fp2.write(json.dumps(flow))
                        init_data_and_animation(msg)
                        msg = ""
                        await asyncio.sleep(2)
                await asyncio.sleep(0)
        await asyncio.sleep(0)

# using Adafruit 16x9 Charlieplexed PWM LED Matrix
from adafruit_is31fl3731.matrix import Matrix as Display
i2c = busio.I2C(board.SCL, board.SDA, frequency=50000) # was 100000
display = Display(i2c, address=0x75)

async def catch_pin_transitions(pin):
    global flow
    with keypad.Keys((pin,), value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                if event.pressed:
                    if pin == board.D7:
                        statemachine.enqueue("speed")

                    if pin == board.D11:
                        statemachine.enqueue("next")

                elif event.released:
                    pass
                    # print("pin went high", pin)
            await asyncio.sleep(0)

animate = True
frame_i = 0

# async def animator():
#     global frame_i, flow
#     while True:
#         if animate:
#             frame_i += flow["animate"]["dir"]
#             if frame_i > flow["animate"]["last"]:
#                 frame_i = flow["animate"]["first"]
#             if frame_i < flow["animate"]["first"]:
#                 frame_i = flow["animate"]["last"]
#             display.frame(frame_i)
#         await asyncio.sleep(flow["animate"]["delay"])

def load_default_images(x):
    for f in range(8):
        display.frame(f, show=False)
        display.fill(0)
        display.pixel(x, f, 10)

timer_delay = -1
async def timer():
    global timer_delay
    while True:
        if timer_delay > 0:
            await asyncio.sleep(timer_delay)
            statemachine.enqueue("timer")
        else:
            await asyncio.sleep(0)

def animate0_enter(state):
    global timer_delay
    state["fi"] = 0
    timer_delay = state["timer_delay"]

def animate0_reenter(state):
    state["fi"] += 1
    state["fi"] %= 8
    display.frame(state["fi"])
    
def animate0_exit(_state):
    global timer_delay
    timer_delay = -1

stateFuncs = {
    "animate0":{"enter":animate0_enter, "reenter":animate0_reenter, "exit":animate0_exit}
}

# state_machine_inst = {
#     "states":{"first":{ "timer_delay":1.25, "enter":animate0_enter, "reenter":animate0_reenter, "exit":animate0_exit}
#     },
#     "transi":{
#         "first": {
#             "timer": {"to":"first", "hist": True},
#             "next": {"to":"first"}
#         }
#     }
# }

import json
def safeSetFlow(jsonstr) :
    global flow
    flow = json.loads(jsonstr)
    # check on the minimum required props
    if not "stateMach" in flow:
        flow["stateMach"] = {
        "states":{"first":{ "timer_delay":1.25, "type":"animate0"}
        },
        "transi":{
            "first": {
                "timer": {"to":"first", "hist": True},
                "next": {"to":"first"}
            }
        }
    }
    #unpack some nodes
    for n in flow["stateMach"]["states"]:
        print ("n", n)
        if "type" in flow["stateMach"]["states"][n]:
            print (flow["stateMach"]["states"][n]["type"])
            fnType = flow["stateMach"]["states"][n]["type"]
            flow["stateMach"]["states"][n]["enter"] = stateFuncs[fnType]["enter"]
            flow["stateMach"]["states"][n]["reenter"] = stateFuncs[fnType]["reenter"]
            flow["stateMach"]["states"][n]["exit"] = stateFuncs[fnType]["exit"]
    print (flow["stateMach"]["states"])
    if not "frames" in flow:
        flow["frames"] = [
        [
            "8123456789abcdef",
            "4123456789abcdef",
            "1123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "2123456789abcdef"
        ],
        [
            "3123456789abcdef",
            "8123456789abcdef",
            "2123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef"
        ],
        [
            "1123456789abcdef",
            "4123456789abcdef",
            "8123456789abcdef",
            "3123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef"
        ],
        [
            "0123456789abcdef",
            "2123456789abcdef",
            "4123456789abcdef",
            "8123456789abcdef",
            "2123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef"
        ],
        [
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "3123456789abcdef",
            "8123456789abcdef",
            "3123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef"
        ],
        [
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "2123456789abcdef",
            "8123456789abcdef",
            "3123456789abcdef",
            "2123456789abcdef",
            "0123456789abcdef"
        ],
        [
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "2123456789abcdef",
            "8123456789abcdef",
            "4123456789abcdef",
            "2123456789abcdef"
        ],
        [
            "2123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "0123456789abcdef",
            "2123456789abcdef",
            "4123456789abcdef",
            "8123456789abcdef"
        ],
    ]
def resetAllFramesfromFlow():
    for f in range(8):
        display.frame(f, show=False)
        for y in range(9):
            col = flow["frames"][f][y]
            for x in range(16):
                display.pixel(x, y, int(col[x], 16)*2)

def init_data_and_animation(jsonstr):
    # print (jsonstr)
    safeSetFlow(jsonstr)
    resetAllFramesfromFlow()

with open("/recent_data.json", "r") as fp:
    init_data_and_animation(fp.read())

async def main():
    interrupt_task7 = asyncio.create_task(catch_pin_transitions(board.D7))
    interrupt_task11 = asyncio.create_task(catch_pin_transitions(board.D11))
    interrupt_statemachine = asyncio.create_task(statemachine.state_change(flow["stateMach"]))
    interrupt_timer_message = asyncio.create_task(timer())
    interrupt_ble_con = asyncio.create_task(ble_connetor())
    interrupt_ble_lis = asyncio.create_task(ble_listener())
    await asyncio.gather(interrupt_task7, interrupt_task11, 
        interrupt_statemachine, interrupt_timer_message, interrupt_ble_con, interrupt_ble_lis)

asyncio.run(main())