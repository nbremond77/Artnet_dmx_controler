# From gitHub : philchristensen/python-artnet
# https://github.com/philchristensen/python-artnet


#    "fixtures": {
#        "rgbw1": {
#            "address": 1,
#            "config": "generic/generic_RGBW.yaml"
#        },
#        "rgbw2": {
#            "address": 5,
#            "config": "generic/generic_RGBW.yaml"
#        },
#        "rgbw3": {
#            "address": 9,
#            "config": "generic/generic_RGBW.yaml"
#        },
#        "dimmer4": {
#            "address": 13,
#            "config": "generic/generic_dimmer.yaml"
#        },
#        "rgbw5": {
#            "address": 14,
#            "config": "generic/generic_RGB.yaml"
#        },
#    },
#    
#    "groups": {
#        "all": ["rgbw1", "rgbw2", "rgbw3", "dimmer4", "rgbw5"],
#        "odds": ["rgbw1", "rgbw3"],
#        "evens": ["rgbw2", "rgbw5"],
#        "dimmers": ["dimmer4"]
#    },
    
    
import yaml
import logging
import pkg_resources as pkg

from artnet import dmx_frame

from artnet import shared
#logging.basicConfig(format='%(levelname)s:%(message)s', filename='artNet_controller.log', level=logging.DEBUG)
#log = logging.getLogger(__name__)

def load(defpath):
    if(defpath.startswith('/')):
        f = open(defpath, 'r')
    else:
        f = pkg.resource_stream('fixtures', defpath)
    try:
        return yaml.safe_load(f)
    finally:
        f.close()


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    if lv > 6:
        value = value[0:6] # skip the last part (the white part) of the color string
        lv = len(value)
    return tuple(int(value[i:i+lv//3], 16) for i in range(0, lv, lv//3))


def rgb_to_hex(rgb):
    if len(rgb) > 3:
        rgb = rgb[0:3] # skip the last part (the white part) of the color tuple
    return '#%02x%02x%02x' % rgb


def hex_to_rgbw(value):
    value = value.lstrip('#')
    lv = len(value)
    while lv < 8:
        value = value + "0"
        lv = len(value)
            
    return tuple(int(value[i:i+lv//4], 16) for i in range(0, lv, lv//4))
        

def rgbw_to_hex(rgbw):
    while len(rgbw) < 4:
        rgbw = rgbw + (0,)
        
    return '#%02x%02x%02x%02x' % rgbw

class FixtureGroup(list):
    def __init__(self, fixtures=None):
        super(FixtureGroup, self).__init__(fixtures if fixtures else [])
    
    def __getattr__(self, funcname):
        def _dispatch(*args, **kwargs):
            results = []
            for fixture in self:
                func = getattr(fixture, funcname)
                if(callable(func)):
                    results.append(func(*args, **kwargs))
            return results
        return _dispatch
    
    def setCommand(self, actionCommand, actionValue):
        for fixture in self:
            shared.log.debug("Group - set fixture %s to action: %s - %s" % (fixture, actionCommand, actionValue))
            fixture.setCommand(actionCommand, actionValue)

    
    def getFrame(self):
        frame = dmx_frame.Frame()
        for f in self:
            for offset, value in f.getState():
                if(offset is None):
                    continue
                frame[(f.address - 1) + offset] = value

        shared.log.debug("getFrame: %s" % frame[0:30])            
        
        return frame


class Fixture(object):
    def __init__(self, address):
        self.address = address
        self.controls = dict()
        self.capabilities = []
    
    @classmethod
    def create(cls, address, fixture_path):
        f = cls(address)
        f.configure(load(fixture_path))
        return f
    
    def __getattr__(self, fixture_func):
        for label, ctrls in self.controls.items():
            for ctrl in ctrls:
                func = getattr(ctrl, fixture_func, None)
                if(callable(func)):
                    return getattr(ctrl, fixture_func)
        #raise AttributeError(fixture_func)
        return None
    
    def configure(self, fixturedef):
        if "rgb_offsets" in fixturedef:
                ctrl = RGBControl()
                label = ctrl.configure(fixturedef)
                self.addControl(label, ctrl)
                self.capabilities.append("setColor")

        if "rgbw_offsets" in fixturedef:
                ctrl = RGBWControl()
                label = ctrl.configure(fixturedef)
                self.addControl(label, ctrl)
                self.capabilities.append("setColor")
        
        if "xy_offsets" in fixturedef:
                ctrl = XYControl()
                label = ctrl.configure(fixturedef)
                self.addControl(label, ctrl)
                self.capabilities.append("setPosition")

        if "strobe_offset" in fixturedef:
                ctrl = StrobeControl()
                label = ctrl.configure(fixturedef)
                self.addControl(label, ctrl)
                self.capabilities.append("setStrobe")

        if "intensity_offset" in fixturedef:
                ctrl = IntensityControl()
                label = ctrl.configure(fixturedef)
                self.addControl(label, ctrl)
                self.capabilities.append("setIntensity")

        if "program_channels" in fixturedef:
                for channel in fixturedef.get('program_channels', []):
                    ctrl = ProgramControl()
                    label = ctrl.configure(channel, fixturedef)
                    self.addControl(label, ctrl)
                self.capabilities.append("setMacro")


    def hasCapability(self, capability):
        return capability in self.capabilities

    def addControl(self, label, control):
        self.controls.setdefault(label, []).append(control)
    
    def getState(self):
        #do program channels last, since we might be using strobe for speed
#        prg_cmp = lambda a,b: [-1,1][a[0] == 'program']
#        titi = self.controls.items()
#        toto = sorted(titi, prg_cmp) ## Sorting is not working in python 3... removed...
#        for clist in titi:
#            for c in clist[1]:
#                for x in c.getState():
#                    shared.log.debug(x)
#        return [x for clist in sorted(self.controls.items(), prg_cmp) for c in clist[1] for x in c.getState()]
        tmp = [x for clist in (self.controls.items()) for c in clist[1] for x in c.getState()]
        shared.log.debug("getState: %s" % tmp)
        return tmp
    
    def getFrame(self):
        frame = dmx_frame.Frame()
        for offset, value in self.getState():
            if(offset is None):
                continue
            frame[(self.address - 1) + offset] = value
            
        shared.log.debug("getFrame: %s" % frame[0:30])            
        return frame
    
    def triggerMacro(self, macro_type, macro, speed=None):
        for label, ctrls in self.controls.items():
            if(label != 'program'):
                continue
            for ctrl in ctrls:
                if(ctrl.macro_type == macro_type and ctrl.hasMacro(macro)):
                    ctrl.triggerMacro(macro, speed=speed)

    def setCommand(self, actionCommand, actionValue):
        shared.log.debug("Fixture %s run action: %s - %s" % (self, actionCommand, actionValue))
        if (actionCommand == "setIntensity"):
            if self.hasCapability('setIntensity'):
                self.setIntensity(actionValue)
        elif (actionCommand == "setColor"):
            if self.hasCapability('setColor'):
                self.setColor(actionValue)
        elif (actionCommand == "setStrobe"):
            if self.hasCapability('setStrobe'):
                self.setStrobe(actionValue)
        elif (actionCommand == "setMacro"):
            if self.hasCapability('setMacro'):
                self.setMacro(actionValue)
        elif (actionCommand == "setPosition"):
            if self.hasCapability('setPosition'):
                self.setPosition(actionValue)
                    
class RGBControl(object):
    def __init__(self):
        self.red_offset = None
        self.green_offset = None
        self.blue_offset = None
        self.red_level = 0
        self.green_level = 0
        self.blue_level = 0
    
    def configure(self, fixturedef):
        self.red_offset = fixturedef['rgb_offsets']['red']
        self.green_offset = fixturedef['rgb_offsets']['green']
        self.blue_offset = fixturedef['rgb_offsets']['blue']
#        self.capabilities.append("setColor")
        return 'rgb'
    
    def setColor(self, hexcode):
        # for some reason this is out of order
        r, b, g = hex_to_rgb(str(hexcode))
        self.red_level = r
        self.green_level = g
        self.blue_level = b
    
    def getColor(self):
        # for some reason this is out of order
        return rgb_to_hex((
            self.red_level, 
            self.blue_level,
            self.green_level,
        ))
    
    def getState(self):
        return [
            (self.red_offset, self.red_level),
            (self.green_offset, self.green_level),
            (self.blue_offset, self.blue_level)
        ]


class RGBWControl(object):
    def __init__(self):
        self.red_offset = None
        self.green_offset = None
        self.blue_offset = None
        self.white_offset = None
        self.red_level = 0
        self.green_level = 0
        self.blue_level = 0
        self.white_level = 0
    
    def configure(self, fixturedef):
        self.red_offset = fixturedef['rgbw_offsets']['red']
        self.green_offset = fixturedef['rgbw_offsets']['green']
        self.blue_offset = fixturedef['rgbw_offsets']['blue']
        self.white_offset = fixturedef['rgbw_offsets']['white']
#        self.capabilities.append("setColor")
        return 'rgbw'
    
    def setColor(self, hexcode):
        # for some reason this is out of order
        r, b, g, w = hex_to_rgbw(str(hexcode))
        self.red_level = r
        self.green_level = g
        self.blue_level = b
        self.white_level = w
        shared.log.debug("SetColor RGBW: (r:%s, b:%s, g:%s, w:%s)" % (r, b, g,  w))
    
    def getColor(self):
        # for some reason this is out of order
        return rgbw_to_hex((
            self.red_level, 
            self.blue_level,
            self.green_level,
            self.white_level,
        ))
    
    def getColorRGBW(self):
        return rgbw_to_hex((
            self.red_level, 
            self.blue_level,
            self.green_level,
            self.white_level,
        ))
    
    def getState(self):
        return [
            (self.red_offset, self.red_level),
            (self.green_offset, self.green_level),
            (self.blue_offset, self.blue_level), 
            (self.white_offset, self.white_level)
        ]
        
class XYControl(object):
    def __init__(self):
        self.has_fine_control = False
        self.x_offset = None
        self.xfine_offset = None
        self.y_offset = None
        self.yfine_offset = None
        self.x_level = 0
        self.xfine_level = 0
        self.y_level = 0
        self.yfine_level = 0
    
    def setPosition(self, x, y,  xfine=0,  yfine=0):
        self.x_level = x
        self.xfine_level = xfine
        self.y_level = y
        self.yfine_level = yfine
        return
    
    def configure(self, fixturedef):
        self.has_fine_control = ( ('xfine' in fixturedef['xy_offsets']) and ('yfine' in fixturedef['xy_offsets']))
        self.x_offset = fixturedef['xy_offsets']['x']
        self.y_offset = fixturedef['xy_offsets']['y']
        if(self.has_fine_control):
            self.xfine_offset = fixturedef['xy_offsets']['xfine']
            self.yfine_offset = fixturedef['xy_offsets']['yfine']
#        self.capabilities.append("setPosition")
        return 'xy'
    
    def getState(self):
        xy = [
            (self.x_offset, self.x_level),
            (self.y_offset, self.y_level)
        ]
        if(self.has_fine_control):
            xy.append((self.xfine_offset, self.xfine_level))
            xy.append((self.yfine_offset, self.yfine_level))
        return xy

class StrobeControl(object):
    def __init__(self):
        self.strobe_offset = None
        self.strobe_value = 0
    
    def configure(self, fixturedef):
        self.strobe_offset = fixturedef['strobe_offset']
#        self.capabilities.append("setStrobe")
        return 'strobe'
    
    def setStrobe(self, value):
        self.strobe_value = value
    
    def getStrobe(self):
        return self.strobe_value
    
    def getState(self):
        return [
            (self.strobe_offset, self.strobe_value)
        ]

class ProgramControl(object):
    def __init__(self):
        self.program_offset = None
        self.program_speed_offset = None
        self.macro_type = None
        self.program_macros = dict()
        self.program_value = 0
        self.program_speed_value = 0
    
    def hasMacro(self, label):
        return label in self.program_macros
    
    def setMacro(self, label, value, speed):
        self.program_macros[label] = (value, speed)
    
    def triggerMacro(self, label, speed=None):
        value, original_speed = self.program_macros[label]
        self.program_value = value
        self.program_speed_value = speed or original_speed
        
    def configure(self, channel, fixturedef):
        self.program_offset = channel['offset']
        self.macro_type = channel['type']
        if(channel['type'] == 'program'):
            self.program_speed_offset = channel.get('speed_offset', fixturedef.get('strobe_offset', None))
        for label, conf in channel.get('macros', {}).items():
            if(isinstance(conf, int)):
                self.setMacro(label, conf, None)
            else:
                self.setMacro(label, conf['value'], conf['speed'])
#        self.capabilities.append("setMacro")
        return 'program'
    
    def getState(self):
        result = []
        if(self.program_value):
            result.append((self.program_offset, self.program_value))
            if(self.program_speed_offset):
                result.append((self.program_speed_offset, self.program_speed_value))
        return result

class IntensityControl(object):
    def __init__(self):
        self.intensity_offset = None
        self.intensityfine_offset = None
        self.intensity_value = 0
        self.intensityfine_value = 0
    
    def configure(self, fixturedef):
        self.intensity_offset = fixturedef['intensity_offset']
        self.intensityfine_offset = fixturedef.get('intensityfine_offset', None)
#        self.capabilities.append("setIntensity")
        return 'intensity'
    
    def setIntensity(self, value):
        self.intensity_value = value
        shared.log.debug("SetIntensity: %s" % self.intensity_value)
    
    def getIntensity(self):
        return self.intensity_value
    
    def getState(self):
        fine = []
        if(self.intensityfine_offset is not None):
            fine = [
                (self.intensityfine_offset, self.intensityfine_value)
            ]
        return fine + [
            (self.intensity_offset, self.intensity_value)
        ]

#available_controls = [
#    RGBControl,
#    RGBWControl,
#    XYControl,
#    StrobeControl,
#    ProgramControl,
#    IntensityControl
#]
