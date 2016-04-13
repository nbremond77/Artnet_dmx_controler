# From gitHub : philchristensen/python-artnet
# https://github.com/philchristensen/python-artnet
import time, sys, socket, logging, threading, itertools

#from artnet import STANDARD_PORT, OPCODES, packet, daemon

from artnet import shared
#logging.basicConfig(format='%(levelname)s:%(message)s', filename='artNet_controller.log', level=logging.DEBUG)
#log = logging.getLogger(__name__)

class Frame(list):
    def __init__(self, channels=None):
        super(Frame, self).__init__((channels[i] if channels else None for i in range(512)))
    
    def __setitem__(self, index, value):
        if not(isinstance(index, int)):
            raise TypeError("Invalid channel index: %r" % index)
        if not(0 <= index < 512):
            raise ValueError("Invalid channel index: %r" % index)
        if not(isinstance(value, int)):
            raise TypeError("Invalid value type: %r" % value)
        if not(0 <= value < 256):
            raise ValueError("Invalid value index: %r" % value)
        super(Frame, self).__setitem__(index, value)
    
    def merge(self, frame):
        result = Frame()
        for i in range(512):
            value = self[i] if frame[i] is None else frame[i]
            if(value is not None):
                result[i] = value
        return result

class AutoCycler(object):
    def __init__(self, controller):
        self.controller = controller
        self.enabled = False
    
    def __enter__(self):
        self.enabled = True
    
    def __exit__(self, etype, e, trace):
        self.enabled = False
        return False
