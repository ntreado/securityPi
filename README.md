securityPi
==========

A security system using Raspberry Pi's that broadcasts a live feed.

Files:
  client.py: Contains client code. Receives video from the server when user requests it or when sensor is triggered.
  server.py: Contains the server code. Handles communication between the sensor and client and between the visual                 system and the client.
  sensor.py: Contains the sensor code. Sends trigger message to the server when sensor is triggered.
  visual.py: Contains the code that streams video using cv2 and sends to the server.
  
Libraries Used:
  OPENCV
  TWISTED
  TKINTER
  GPIO
