##Programmer: Dinh Nguyen
##Team: Oracle


## sensor.py
##import server.py
##import client.py
import RPi.GPIO as GPIO
import socket

import time

GPIO.setmode(GPIO.BCM)

PIR_PIN = 7
PIR_PIN2 = 11

GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(PIR_PIN2, GPIO.IN)

createTrigger = "POST /sensor/0/ HTTP/1.1\r\n\r\n"
requestTrigger = "POST /sensor/0/trigger HTTP/1.1\r\n\r\n"
deleteTrigger = "DELETE  /sensor/0 HTTP/1.1\r\n\r\n"

try:

        print "CTRL+C to exit"

        time.sleep(1)

        print "Sensors: Activated"

        try:
                ##host = 'nu.sacst.net'
                host = "172.31.174.40"
                port = 5707
                size = 1024
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host,port))
                print "Socket Status: Opened"
                s.send(createTrigger.encode())

        except Exception, ne:
                print "Socket Status: Not Opened", ne.message
                print traceback.print_exc()
                sys.exit(-1)
                
        while True:

##                if GPIO.input(PIR_PIN):
##
##                        print "Motion Detected!"
##                
##                        s.send(requestTrigger.encode())
##                        
##                        time.sleep(.5)

                if (GPIO.input(PIR_PIN) or GPIO.input(PIR_PIN2)):
                        if(GPIO.input(PIR_PIN)):
                        
                              print "Motion Detected at Sensor 1!"

                              s.send(requestTrigger.encode())

                              time.sleep(.5)

                        if(GPIO.input(PIR_PIN2)):

                              print "Motion Detected at Sensor 2!"

                              s.send(requestTrigger.encode())

                              time.sleep(.5)
                        

except KeyboardInterrupt:

        print "\nSensors: Deactivated"
        s.send(deleteTrigger.encode())
               
        GPIO.cleanup()
