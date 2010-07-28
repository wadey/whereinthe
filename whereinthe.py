from twisted.web import server, resource
from twisted.web.static import File
from twisted.web.util import Redirect
from twisted.web.server import NOT_DONE_YET
from twisted.application import service, internet
from twisted.internet.defer import inlineCallbacks

import simplejson as json

from simplegeo import Record
from simplegeo.twisted import Client

import settings

LAYER = settings.LAYER

START = {"geometry": {"type": "Point", "coordinates": [settings.START_LON, settings.START_LAT]}}

client = Client(settings.OAUTH_KEY, settings.OAUTH_SECRET)

def webInlineCallbacks(function):
    function = inlineCallbacks(function)
    
    def __func__(*args, **kwargs):
        function(*args, **kwargs)
        return NOT_DONE_YET
    
    return __func__

class Update(resource.Resource):
    isLeaf = True

    def render_POST(self, request):
        lat = request.args["lat"][0];
        lon = request.args["lon"][0];
        accuracy = request.args["accuracy"][0];
        #uid = request.getSession().uid;
        uid = request.getCookie('uid')

        print "saving: %s: %s,%s (%s)" % (uid, lat, lon, accuracy)

        record = Record(LAYER, uid, lat, lon, accuracy=accuracy)
        client.add_record(record)
        return json.dumps(record.to_dict())

class Nearby(resource.Resource):
    isLeaf = True

    @webInlineCallbacks
    def render_GET(self, request):
        lat = request.args["lat"][0];
        lon = request.args["lon"][0];
        #uid = request.getSession().uid;
        uid = request.getCookie('uid')
        
        nearby = yield client.get_nearby(LAYER, lat, lon)

        nearby = nearby['features']

        # don't include the user
        print "uid: %s" % uid
        nearby = [e for e in nearby if e['id'] != uid]

        request.write(json.dumps(nearby))
        request.finish()

class Start(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        uid = request.getCookie('uid')

        if not uid:
            uid = request.getSession().uid
            request.addCookie('uid', uid)

        return json.dumps(START)

class WhereInThe(resource.Resource):    
    isLeaf = False
    
    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild('static', File('static'))
        self.putChild('start.json', Start())
        self.putChild('update.json', Update())
        self.putChild('nearby.json', Nearby())
        self.putChild('', Redirect('/static/index.html'))

site = server.Site(WhereInThe())
tcpserver = internet.TCPServer(settings.PORT, site)
application = service.Application("WhereInThe")

tcpserver.setServiceParent(application)
