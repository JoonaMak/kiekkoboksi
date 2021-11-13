import RPi.GPIO as GPIO
import asyncio

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Button 
class Button:

    def __init__(self, pin):
        GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        self.pin = pin

    async def read(self):
        return GPIO.input(self.pin)

# Class for a single box
class Box:
    
    def __init__(self, servoPin, switchPin):
        GPIO.setup(servoPin, GPIO.OUT)
        GPIO.setup(switchPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        self.servo = GPIO.PWM(servoPin, 50)
        self.switchPin = switchPin
        self.owner = None
        self.discs = []
        self.servo.start(2.5)

    async def returnDisc(self, discCode, owner, socket):
        print("Inside return function")
        self.servo.ChangeDutyCycle(5.0)
        await asyncio.sleep(0.5)
        while True:
            if GPIO.input(self.switchPin):
                await asyncio.sleep(0.2)
                print("Put disc in and close door")
                break
        self.servo.ChangeDutyCycle(2.5)
        self.discs.append(discCode)
        await socket.emit('RETURNSTATUS', discCode)
        self.owner = owner
        self.p()
        await asyncio.sleep(0.2)

    async def takeDiscs(self, socket):
        self.servo.ChangeDutyCycle(5.0)
        await asyncio.sleep(0.5)
        while True:
            if GPIO.input(self.switchPin):
                await asyncio.sleep(0.2)
                print("Take discs out and close door")
                break
        self.servo.ChangeDutyCycle(2.5)
        await socket.emit('TAKESTATUS', ' '.join(map(str, self.discs)))
        self.discs.clear()
        self.owner = None
        print("Take discs")
        await asyncio.sleep(0.2)
 
    def p(self):
        print("\nOwner: " + self.owner + "\nDiscs inside: " + ' '.join(map(str, self.discs)) + "\n")
