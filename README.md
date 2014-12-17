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

Install & startup:
1. Install third party libraries
2. Start server
3. Edit socket connections in all client code (client, camera, IR sensor) to use server ip address
4. Start client programs in any order

