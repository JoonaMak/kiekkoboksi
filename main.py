import asyncio
import socketio
import cv2
import sys
import time
from Box import Box
from Box import Button

sio = socketio.AsyncClient()

detector = cv2.QRCodeDetector()

global ownerOfDisc
ownerOfDisc = None

global takerOfDisc
takerOfDisc = None

boxes = [
    Box(2,14)
]

button = Button(4)

@sio.event
async def connect():
    print('connection established')

@sio.event
async def disconnect():
    print('disconnected from server')

@sio.event
async def OPEN(data):
    print('message received with ', data)
    global takerOfDisc
    takerOfDisc  = data

@sio.event
async def USER(data):
    print('Owner (' + data + ') name received from server')
    global ownerOfDisc
    ownerOfDisc = data

# Scan once for disc qr return None or Disc data
async def scan():
    cap = cv2.VideoCapture(0)
    _, img = cap.read()
    cap.release()
    data, _, _ = detector.detectAndDecode(img)
    if (type(data) == str and len(data) > 0):
        try:
            parsedCode = data.split("=")[1]
            if (parsedCode):
                return parsedCode
        except:
            print("Invalid qr code scanned")
    return None
    

# When this function is called return sequence is started
async def returnDisc(code):
    await sio.emit('DISCFOUND', code)
    global ownerOfDisc
    # Loop until we get response
    while (ownerOfDisc == None):
        print("Waiting for owner of scanned disc")
        await asyncio.sleep(0.2)
    # Call open door
    for box in boxes:
        if box.owner == ownerOfDisc:
            print("Found existing")
            await box.returnDisc(code, ownerOfDisc, sio)
            ownerOfDisc = None
            return None
    for box in boxes:
        if box.owner == None:
            print("Crated new")
            await box.returnDisc(code, ownerOfDisc, sio)
            break
    ownerOfDisc = None
    takerOfDisc = None

# When this function is called take sequence is started
async def takeDiscs(taker):
    for box in boxes:
        if box.owner == taker:
            await box.takeDiscs(sio)
            break
    global takerOfDisc
    takerOfDisc = None

# This is the main loop of the code
async def mainLoop():
    while True:
        pressed = await button.read()
        if (pressed == 1):
            codeRed = await scan()
            print("scanning")
            if (codeRed):
                await returnDisc(codeRed)
        if (takerOfDisc):
            await takeDiscs(takerOfDisc)
        await asyncio.sleep(0.5)
        print("looping")

async def main():
    await sio.connect('http://localhost:3000')
    # Task for listening sockets
    listenerTask = asyncio.create_task(sio.wait())
    # Task for main loop
    mainTask = asyncio.create_task(mainLoop())
    await listenerTask
    await mainTask
    listenerTask.cancel()
    await sio.disconnect()
if __name__ == '__main__':
    asyncio.run(main())