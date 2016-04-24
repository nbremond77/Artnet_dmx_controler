# From gitHub : philchristensen/python-artnet
# https://github.com/philchristensen/python-artnet

import sys
import threading
import socket
import time
import logging
import json

#import artnet
#from artnet import packet, STANDARD_PORT, OPCODES, STYLE_CODES

from artnet import dmx_packet
from artnet import dmx_definitions

from artnet import shared
#logging.basicConfig(format='%(levelname)s:%(message)s', filename='artNet_controller.log', level=logging.DEBUG)
#log = logging.getLogger(__name__)

#def main(config):
#    shared.log.info("Running script %s" % __name__)
#    d = Poller(config.get('base', 'address'))
#    d.run()

class Poller(threading.Thread):
    def __init__(self, address, nodaemon=False, runout=False):
        super(Poller, self).__init__()
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        self.sock.bind(('', dmx_definitions.STANDARD_PORT))
        self.sock.settimeout(0.0)
        
        self.broadcast_address = '<broadcast>'
        self.last_poll = 0
        self.address = address

        self.nodaemon = nodaemon
        self.daemon = not nodaemon
        self.running = True

    def run(self):
        now = time.time()
        while(self.running):
            self.handle_artnet()
    
    def read_artnet(self):
        try:
            data, addr = self.sock.recvfrom(1024)
        except socket.error as e:
            time.sleep(0.1)
            return None
        
        return dmx_packet.ArtNetPacket.decode(addr, data)
    
    def handle_artnet(self):
        if(time.time() - self.last_poll >= 4):
            self.last_poll = time.time()
            self.send_poll()
        
        p = self.read_artnet()
        if(p is None):
            return
        
        shared.log.debug("recv: %s" % p)
        if(p.opcode == dmx_definitions.OPCODES['OpPoll']):
            self.send_poll_reply(p)
    
    def send_dmx(self, frame, universe=0):
        p = dmx_packet.DmxPacket(frame, universe=universe)
        self.sock.sendto(p.encode(), (self.address, dmx_definitions.STANDARD_PORT))
        shared.log.debug("Send DMX: u:%s - %s - frame: %s" % (universe,  p, frame[0:30]))
    
    def send_poll(self):
        p = dmx_packet.PollPacket(address=self.broadcast_address)
        self.sock.sendto(p.encode(), (p.address, dmx_definitions.STANDARD_PORT))
    
    def send_poll_reply(self, poll):
        ip_address = socket.gethostbyname(socket.gethostname())
        style = dmx_definitions.STYLE_CODES['StNode'] if isinstance(self, Poller) else dmx_definitions.STYLE_CODES['StController']
        
        r = dmx_packet.PollReplyPacket(address=self.broadcast_address)
        r.style = style
        
        shared.log.debug("send: %s" % r)
        self.sock.sendto(r.encode(), (r.address, dmx_definitions.STANDARD_PORT))

