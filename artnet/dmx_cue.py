#    "cues": {
#        "cueName1": {
#            "fixtureList": {
#                  "rgbw1": {"setColor":"#22F35515", "FX":{"blinkFixture":{"timeON":25, "timeOFF":10} } },
#                  "rgbw2": {"setColor":"#EEBBAA", "setIntensity":103,"FX":{} },
#                  "rgbw5": {"setColor":"#12345678", "FX":{} }
#            },
#            "groupList": {
#                  "odds": {"setColor":"#EEBBAA", "FX":{} }
#            },
#            "effectList": {},
#            "initialTransitionDuration": 5
#        },
#        "cueName2": {
#            "fixtureList": {},
#            "groupList": {
#                  "odds": {"setColor":"#22F35515", "setIntensity":44,"FX":{} },
#                  "evens": {"setColor":"#EEBBAA", "FX":{"blinkGroup":{"timeON":0.5, "timeOFF":1} } }
#            },
#            "effectList": {},
#            "initialTransitionDuration": 8
#        },
#        "cueName3": {
#            "fixtureList": {
#                  "rgbw3": {"setColor":"#22F35515", "setIntensity":133,"FX":{} },
#                  "dimmer4": {"setIntensity":231, "FX":{} }
#            },
#            "groupList": {},
#            "effectList": {},
#            "initialTransitionDuration": 3
#        }
#    },
    
    
import time,  logging
from artnet import dmx_frame, dmx_fixture, dmx_effects, dmx_rig

from artnet import shared
#logging.basicConfig(format='%(levelname)s:%(message)s', filename='artNet_controller.log', level=logging.DEBUG)
#log = logging.getLogger(__name__)

class Cue(object):
    def __init__(self, rig,  cueName, fixtureList={},  groupList={},  effectList = {}, initialTransitionDuration = 0):
        self.rig = rig
        self.cueFixtureList  = {}
        self.cueGroupList = {}
        self.cueEffectList = {}
 
        self.name = cueName
        self.initialTransitionDuration = initialTransitionDuration

        for index,  fixture in enumerate(fixtureList):
            parameters = fixtureList[fixture]
            self.cueFixtureList[fixture] = parameters
        
        for index,  group in enumerate(groupList):
            parameters = groupList[group]
            self.cueGroupList[group] = parameters
        
        for index,  effect in enumerate(effectList):
            parameters = effectList[effect]
            self.cueEffectList[effect] = parameters



    def update(self,  fixtureList=None,  groupList=None,  effectList = None, initialTransitionDuration = None):
        if fixtureList:
            for index,  fixture in enumerate(fixtureList):
                parameters = fixtureList[fixture]
                self.cueFixtureList[fixture] = parameters
        if groupList:
            for index,  group in enumerate(groupList):
                parameters = groupList[group]
                self.cueGroupList[group] = parameters
        if effectList:
            for index,  effect in enumerate(effectList):
                parameters = effectList[effect]
                self.cueEffectList[effect] = parameters
        if initialTransitionDuration:
            self.initialTransitionDuration = initialTransitionDuration
       

    def getFrame(self):
        theFrame = dmx_frame.Frame()
        
        # Set the values of the fixture
        for fixture, parameter in self.cueFixtureList.items():
            shared.log.debug("Cue: %s Fixture: %s" % (self.name, fixture))
            for actionCommand, actionValue in parameter.items():
                #shared.log.debug(" - action: %s - %s" % (actionCommand, actionValue))
                fixture.setCommand(actionCommand, actionValue)
                
            # Merge this values in the current frame
            theFrame.merge(fixture.getFrame())
            
        # Set the values of the group
        for group, parameter in self.cueGroupList.items():
            shared.log.debug("Cue: %s Group: %s" % (self.name, group))
            for actionCommand, actionValue in parameter.items():
                for fixture in self.rig.groups[group]:
                    fixture.setCommand(actionCommand, actionValue)
                
            # Merge this values in the current frame
            theFrame.merge(self.rig.groups[group].getFrame())

        # Set the values of the effect
# TO BE DONE
                
        return theFrame

