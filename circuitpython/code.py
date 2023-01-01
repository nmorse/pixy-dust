import asyncio
import board
import keypad
import busio


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
async def ble_listener():
    global msg
    while True:
        if ble.connected:
            if uart_service.in_waiting:
                line = uart_service.readline()
                if line:
                    print("full", line.decode('utf-8'))
                    
                    msg += line[:-1].decode('utf-8')
                    print(msg)
                    if line[-2:].decode('utf-8') == '\n\n':
                        print("last part", msg)
                        new_da = json.loads(msg)
                        with open("/recent_data.json", "w") as fp2:
                            fp2.write(json.dumps(new_da))
                        msg = ""
        await asyncio.sleep(.3333)

# using Adafruit 16x9 Charlieplexed PWM LED Matrix
from adafruit_is31fl3731.matrix import Matrix as Display
i2c = busio.I2C(board.SCL, board.SDA, frequency=50000) # was 100000
display = Display(i2c, address=0x75)


async def catch_pin_transitions(pin):
    global animate_delay
    """Print a message when pin goes low and when it goes high."""
    with keypad.Keys((pin,), value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                if event.pressed:
                    if pin == board.D7:
                        animate_delay *= 0.5
                        load_default_images(15)

                    if pin == board.D11:
                        animate_delay *= 2
                        load_default_images(0)

                elif event.released:
                    pass
                    # print("pin went high", pin)
            await asyncio.sleep(0)

animate = True
frame_dir = 1
frame_i = 0
animate_delay = 2

async def animator():
    global frame_i
    while True:
        if animate:
            frame_i += frame_dir
            if frame_i > 7:
                frame_i = 0
            if frame_i < 0:
                frame_i = 7
            display.frame(frame_i)
        await asyncio.sleep(animate_delay)

def load_default_images(x):
    for f in range(8):
        display.frame(f, show=False)
        display.fill(0)
        display.pixel(x, f, 10)


async def main():
    load_default_images(0)
    interrupt_task7 = asyncio.create_task(catch_pin_transitions(board.D7))
    interrupt_task11 = asyncio.create_task(catch_pin_transitions(board.D11))
    interrupt_animator = asyncio.create_task(animator())
    interrupt_ble_con = asyncio.create_task(ble_connetor())
    interrupt_ble_lis = asyncio.create_task(ble_listener())
    await asyncio.gather(interrupt_task7, interrupt_task11, 
        interrupt_animator, interrupt_ble_con, interrupt_ble_lis)

import json
def init_data_and_animation(jsonstr):
    global da
    print (jsonstr)
    da = json.loads(jsonstr)

with open("/recent_data.json", "r") as fp:
    init_data_and_animation(fp.read())

asyncio.run(main())