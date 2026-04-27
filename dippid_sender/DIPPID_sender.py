import socket
import time
import numpy

IP = '127.0.0.1'
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

counter = 0

while True:

    accelerometerX = numpy.sin(counter)
    accelerometerY = numpy.sin(counter * 2 + 0.7)
    accelerometerZ = numpy.sin(counter * 3 + 0.3)

    buttonData = numpy.random.randint(0,2)

    message = f"""{{
                 "heartbeat": {str(counter)},
                 "accelerometer": {{
                    "x": {accelerometerX},
                    "y": {accelerometerY},
                    "z": {accelerometerZ}
                 }},
                 "button_1": {buttonData}
               }}"""
    print(message)

    sock.sendto(message.encode(), (IP, PORT))

    counter += 1
    time.sleep(1)
