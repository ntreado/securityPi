from twisted.web import server, resource
from twisted.internet import reactor, endpoints
import time
import json

objects = {}

class data_object:
  def __init__(self, id):
    self.id = id

class sensor(data_object):
  def __init__(self, id):
    self.id = sen_id(id)
    self.sub = {}

class camera(data_object):
  def __init__(self, id):
    self.id = cam_id(id)
    self.events = []

class client(data_object):
  def __init__(self, id):
    self.id = cli_id(id)
    self.events = []

def cam_id(id): return 'cam_' + id
def sen_id(id): return 'sen_' + id
def cli_id(id): return 'cli_' + id

def is_cam_id(id): return id[0:3] == 'cam_'
def is_sen_id(id): return id[0:3] == 'sen_'
def is_cli_id(id): return id[0:3] == 'cli_'

class Server(resource.Resource):
  isLeaf = True
  snapshot = ""

  def notfound(self, request):
    request.setResponseCode(404)
    return "not found"

  def notimplemented(self, request):
    return "NOT IMPLEMENTED"

  def exists(self, request):
    return self.notfound(request)

  def render_GET(self, request):
    print "R " + request.method + " " + request.uri
    global objects

    method = request.method
    request.setHeader("content-type", "application/json")

    rs = [ s for s in request.uri.split("/") if s != "" ]
    #print "rs", rs

    if len(rs) == 0:
      self.notfound(request)

    id = rs[1] if len(rs) > 1 else None

    # POST /camera/id
    if method == "POST" and len(rs) == 2 and rs[0] == "camera":
      if cam_id(id) in objects:
        return self.exists(request)
      objects[cam_id(id)] = camera(id)
      for s in objects:
        if isinstance(objects[s], sensor):
          objects[s].sub[cam_id(id)] = True
      return ""
    # DELETE /camera/id
    elif method == "DELETE" and len(rs) == 2 and rs[0] == "camera":
      if not cam_id(id) in objects:
        return self.notfound(request)
      for s in objects:
        if isinstance(objects[s], sensor):
          del objects[s].sub[cam_id(id)]
      del objects[cam_id(id)]
      return ""
    # GET /camera/id/events
    elif method == "GET" and len(rs) == 3 and rs[0] == "camera" and rs[2] == "events":
      if not cam_id(id) in objects:
        return self.notfound(request)
      events = objects[cam_id(id)].events
      objects[cam_id(id)].events = []
      return json.dumps({"count": len(events), "events": events})
    # POST /camera/id/stopstream
    elif method == "POST" and len(rs) == 3 and rs[0] == "camera" and rs[2] == "stopstream":
      if not cam_id(id) in objects:
        return self.notfound(request)
      event = {"source": "", "time": time.time(), "message": request.content.read(), "type": "stop stream"}
      objects[cam_id(id)].events.append(event)
      return ""
    # POST /camera/id/startstream
    elif method == "POST" and len(rs) == 3 and rs[0] == "camera" and rs[2] == "startstream":
      if not cam_id(id) in objects:
        return self.notfound(request)
      event = {"source": "", "time": time.time(), "message": request.content.read(), "type": "start stream"}
      objects[cam_id(id)].events.append(event)
      return ""
    # POST /sensor/id
    elif method == "POST" and len(rs) == 2 and rs[0] == "sensor":
      if sen_id(id) in objects:
        return self.exists(request)
      objects[sen_id(id)] = sensor(id)
      for s in objects:
        if isinstance(objects[s], camera):
          objects[sen_id(id)].sub[s] = True
      return ""
    # DELETE /sensor/id
    elif method == "DELETE" and len(rs) == 2 and rs[0] == "sensor":
      if not sen_id(id) in objects:
        return self.notfound(request)
      del objects[sen_id(id)]
      return ""
    # POST /sensor/id/trigger
    elif method == "POST" and len(rs) == 3 and rs[0] == "sensor" and rs[2] == "trigger":
      if not sen_id(id) in objects:
        return self.notfound(request)
      event = {"source": id, "time": time.time(), "message": request.content.read(), "type": "start stream"}
      for s in objects[sen_id(id)].sub:
        #print "camera " + sen_id(id) + " subscribes " + s
        objects[s].events.append(event)
      return ""
    # POST /client/id
    elif method == "POST" and len(rs) == 2 and rs[0] == "client":
      if cli_id(id) in objects:
        return self.exists(request)
      objects[cli_id(id)] = client(id)
      for s in objects:
        if isinstance(objects[s], sensor):
          objects[s].sub[cli_id(id)] = True
      return ""
    # DELETE /client/id
    elif method == "DELETE" and len(rs) == 2 and rs[0] == "client":
      if not cli_id(id) in objects:
        return self.notfound(request)
      for s in objects:
        if isinstance(objects[s], sensor) and cli_id(id) in objects[s].sub:
          del objects[s].sub[cli_id(id)]
      del objects[cli_id(id)]
      return ""
    # GET /client/id/events
    elif method == "GET" and len(rs) == 3 and rs[0] == "client" and rs[2] == "events":
      if not cli_id(id) in objects:
        return self.notfound(request)
      events = objects[cli_id(id)].events
      objects[cli_id(id)].events = []
      return json.dumps({"count": len(events), "events": events})
    else:
#      print "[ objects ]"
#      for s in objects:
#        if isinstance(objects[s], sensor):
#          print "  sensor", s
#        elif isinstance(objects[s], camera):
#          print "  camera", s
#        elif isinstance(objects[s], client):
#          print "  client", s
#        else:
#          print "  what?", s
      #print "objects", objects
#      print
      return self.notfound(request)

  def render_OPEN(self, request):
    return "OPEN"

  def render_CLOSE(self, request):
    return "CLOSE"

  def render_POTATO(self, request):
    print "POTATO"
    request.setHeader("content-type", "image/jpeg")
    return self.snapshot
    #return "POTATO"

  def render_STREAM(self, request):
    print "stream"
    self.snapshot = request.content.read()
    print "done " + str(len(self.snapshot))
    return ""

  def render_POST(self, request):
    return self.render_GET(request)

  def render_DELETE(self, request):
    return self.render_GET(request)

endpoints.serverFromString(reactor, "tcp:5707").listen(server.Site(Server()))
reactor.run()

#/camera/id
#POST
#objects[cam_id(id)] = camera(id)
#for s in objects:
#  if s is sensor:
#    objects[s.id].sub[s] = True
#DELETE
#for s in objects:
#  if s is sensor:
#    del s.sub[cam_id(id)]
#del objects[cam_id(id)]
#
#/camera/id/events
#GET
#events = objects[cam_id(id)].events
#objects[cam_id(id)].events = []
#json.dumps({'count': len(events), 'events': events})
#
#/sensor/id
#POST
#objects[sen_id(id)] = []
#for s in objects[cam_id(id)]:
#  objects[sen_id(id)].sub[s.id] = True
#DELETE
#del objects[sen_id(id)]
#
#/sensor/id/trigger
#POST
#event = {'source': id, 'time': time(), 'message': request_body}
#for s in objects[
#
##/client/id
##POST
##DELETE
##
##/client/id/events

