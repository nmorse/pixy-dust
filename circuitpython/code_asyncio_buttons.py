import asyncio
import board
import keypad

async def catch_pin_transitions(pin):
    """Print a message when pin goes low and when it goes high."""
    with keypad.Keys((pin,), value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                if event.pressed:
                    print("pin went low", pin)
                elif event.released:
                    print("pin went high", pin)
            await asyncio.sleep(0)

async def main():
    interrupt_task10 = asyncio.create_task(catch_pin_transitions(board.D10))
    interrupt_task9 = asyncio.create_task(catch_pin_transitions(board.D9))
    await asyncio.gather(interrupt_task10, interrupt_task9)

asyncio.run(main())