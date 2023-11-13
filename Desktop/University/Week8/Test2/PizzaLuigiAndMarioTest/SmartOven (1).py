import time, sys
import pip._vendor.requests
from fhict_cb_01.custom_telemetrix import CustomTelemetrix
import time


#-----------
# Constants
#-----------
BUTTON1 = 8
REDLEDPIN = 4
BUZZER = 3
GREENLEDPIN = 5
#------------------------------
# Initialized global variables
#------------------------------
level = None
prevLevel = 0
timer = 30

#-----------
# functions
#-----------


def setup():
    global board
    board = CustomTelemetrix()
    board.set_pin_mode_digital_input_pullup(BUTTON1, callback = ButtonChanged)
    board.set_pin_mode_digital_output(REDLEDPIN)
    board.set_pin_mode_digital_output(GREENLEDPIN)
    board.set_pin_mode_digital_output(BUZZER)


def ButtonChanged(data):
    global level
    level = data[2]

def systemStart(button):
    if (button == 0):
        board.digital_write(REDLEDPIN, 1)
        board.digital_write(GREENLEDPIN, 0)
        countdown(5)
        removeOrder = {"status": True}  # Dictionary to be sent as JSON
        response = pip._vendor.requests.post('http://localhost:5000/smartOven', json=removeOrder)
    
    if timer == "00.01":
        board.digital_write(REDLEDPIN, 0)
        board.digital_write(GREENLEDPIN, 1)
        board.displayShow("done")


        

            

             


def countdown(t): 
	global timer
	while t: 
		mins, secs = divmod(t, 60) 
		timer = '{:02d}.{:02d}'.format(mins, secs) 
		board.displayShow(timer) 
		time.sleep(1) 
		t -= 1




def loop():
    global prevLevel
    systemStart(level)
    if (prevLevel != level):
        print(level)
        prevLevel = level

    # Put your code here.
    time.sleep(0.1) # Give Firmata some time to handle the protocol.

# Put your functions here.

#--------------
# main program
#--------------
setup()
while True:
    try:
        loop()
    except KeyboardInterrupt: # Shutdown Firmata on Crtl+C.
        print ('shutdown')
        board.shutdown()
        sys.exit(0)