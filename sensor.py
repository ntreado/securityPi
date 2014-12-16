##Programmer: Dinh Nguyen
##Team: Oracle

import RPi.GPIO as GPIO
import socket

import time

GPIO.setmode(GPIO.BOARD)

PIR_PIN = 7

GPIO.setup(PIR_PIN, GPIO.IN)

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
	flag = 0
        while True:
                ##print GPIO.input(PIR_PIN)
                ##time.sleep(1)
		##print flag
		##print GPIO.input(PIR_PIN)
		##if flag is 0:
		##	print "flag is 0"
		##if GPIO.input(PIR_PIN) is 1:
		##	print "input is 1"
		if flag is 0 and GPIO.input(PIR_PIN) is 1:
                ##if GPIO.input(PIR_PIN):
                 	print "Motion Detected!"
                        s.send(requestTrigger.encode())
		
		flag = GPIO.input(PIR_PIN)
		time.sleep(.1)
                        
except KeyboardInterrupt:

        print "\nSensors: Deactivated"
        s.send(deleteTrigger.encode())
               
        GPIO.cleanup()
