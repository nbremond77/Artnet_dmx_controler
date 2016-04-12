
import time,  logging
from artnet import dmx_frame, dmx_fixture, dmx_effects, dmx_rig

logging.basicConfig(format='%(levelname)s:%(message)s', filename='artNet_controller.log', level=logging.DEBUG)
log = logging.getLogger(__name__)

class Cue(object):
    def __init__(self, cueName, fixtureList={},  groupList={},  effectList = {}, initialTransitionDuration = 0):
 
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
            log.debug("Cue: %s Fixture: %s" % (self.name, fixture))
            for actionCommand, actionValue in parameter.items():
                log.debug(" - action: %s - %s" % (actionCommand, actionValue))
                if (actionCommand == "setIntensity"):
                    if hasattr(fixture, 'setIntensity'):
                        fixture.setIntensity(actionValue)
                if (actionCommand == "setColor"):
                    if hasattr(fixture, 'setColor'):
                        fixture.setColor(actionValue)
                if (actionCommand == "setStrobe"):
                    if hasattr(fixture, 'setStrobe'):
                        fixture.setStrobe(actionValue)
            
            # Merge this values in the current frame
            theFrame.merge(fixture.getFrame())
            
        # Set the values of the group
        for group, parameter in self.cueGroupList.items():
            log.debug("Cue: %s Group: %s" % (self.name, group))
            for actionCommand, actionValue in parameter.items():
                log.debug(" - action: %s - %s" % (actionCommand, actionValue))
                groupName.actionCommand(actionValue)
                if (actionCommand == "setIntensity"):
                    if hasattr(group, 'setIntensity'):
                        group.setIntensity(actionValue)
                if (actionCommand == "setColor"):
                    if hasattr(group, 'setColor'):
                        group.setColor(actionValue)
                if (actionCommand == "setStrobe"):
                    if hasattr(group, 'setStrobe'):
                        group.setStrobe(actionValue)
            # Merge this values in the current frame
            theFrame.merge(group.getFrame())

        # Set the values of the effect

                
        return theFrame
#      t = time.time()
#    while(True):
#        g.setColor('#0000ff')
#        g.setIntensity(255)
#        yield g.getFrame()
#        if(secs and time.time() - t >= secs):
#            return
