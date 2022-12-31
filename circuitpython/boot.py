
import storage
import digitalio
import board

button = digitalio.DigitalInOut(board.D11)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP
 
storage.remount("/", readonly=(not button.value))


