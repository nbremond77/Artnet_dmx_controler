#Cue: cueName2
#{'fixtureList': {}, 'groupList': {'odds': {'transitionTime': 2, 'FX': {}, 'value': [10, 150, 150]}, 'evens': {'transitionTime': 2, 'FX': {'blinkGroup': {'timeOFF': 1, 'timeON': 0.5}}, 'value': [150, 15, 250]}}}
#Cue: cueName1
#{'fixtureList': {'slimpar_1': {'transitionTime': 2, 'FX': {'blinkFixture': {'timeOFF': 10, 'timeON': 25}}, 'value': [10, 20, 150]}, 'slimpar_2': {'transitionTime': 2, 'FX': {}, 'value': [120, 200, 50]}, 'slimpar_4': {'transitionTime': 2, 'FX': {}, 'value': [30, 40, 12]}}, 'groupList': {'odds': {'transitionTime': 2, 'FX': {}, 'value': [10, 150, 150]}}}
#Cue: cueName3
#{'fixtureList': {'slimpar_3': {'transitionTime': 2, 'FX': {}, 'value': [10, 20, 150]}, 'slimpar_4': {'transitionTime': 2, 'FX': {}, 'value': [120, 200, 50]}}, 'groupList': {}}
#Chase: chaseName2

#Cue: cueName1
"""
{
  'initialTransitionTime': 2,
  'fixtureList': {
    'slimpar_1': {'setColor': '#FE1233BB', 'setStrobe':12, 'setIntensity':200}, 
    'slimpar_2': {'setColor': '#FE1233', 'setIntensity':200}, 
    'slimpar_4': {'setIntensity':200}
  }, 
  'groupList': {
    'odds': {'setColor': '#FE1233BB', 'setStrobe':12, 'setIntensity':200}
  }
  'effectList': {
    'blinkFixture': {{'group':'odd', 'group':'even', 'fixture':'slimpar_1'}, {'timeOFF': 10, 'timeON': 25}},
  }
}
"""

import time,  logging
from artnet import dmx_frame, dmx_fixture, dmx_effects

logging.basicConfig(format='%(levelname)s:%(message)s', filename='artNet_controller.log', level=logging.DEBUG)
log = logging.getLogger(__name__)

class Cue(object):
    def __init__(self, cueName, fixtureList={},  groupList={},  effectList = {}, initialTransitionDuration = 0):
        # Parameters
        #   cueName = "Cue blue ambiance"
        #   fixtureList  = {}
        #   groupList = {}
        #   effectList = {}
        #   initialTransitionDuration = 3

        self.name = cueName
        self.fixtureList = fixtureList
        self.groupList = groupList
        self.effectList = effectList
        self.initialTransitionDuration = initialTransitionDuration
#        self.controls = dict()

#        self.configure()


    def update(self,  fixtureList=None,  groupList=None,  effectList = None, initialTransitionDuration = None):
        if fixtureList:
            self.fixtureList = fixtureList
        if groupList:
            self.groupList = groupList
        if effectList:
            self.effectList = effectList
        if initialTransitionDuration:
            self.initialTransitionDuration = initialTransitionDuration

        self.configure()

        

    def getFrame(self):
        theFrame = dmx_frame.Frame()
        
        # Set the values of the fixture
        for fixtureName, actions in self.fixtureList.items():
            log.debug("Cue: %s Fixture: %s" % (self.name, fixtureName))
            for actionCommand, actionValue in actions.items():
                log.debug(" - action: %s - %s" % (actionCommand, actionValue))
                fixtureName.actionCommand(actionValue)
            
            # Merge this values in the current frame
            theFrame.merge(fixtureName.getFrame())
            
        # Set the values of the group
        for groupName, actions in self.groupList.items():
            log.debug("Cue: %s Group: %s" % (self.cueName, groupName))
            for actionCommand, actionValue in actions.items():
                log.debug(" - action: %s - %s" % (actionCommand, actionValue))
                groupName.actionCommand(actionValue)

            # Merge this values in the current frame
            theFrame.merge(groupName.getFrame())

        # Set the values of the effect

                

#      t = time.time()
#    while(True):
#        g.setColor('#0000ff')
#        g.setIntensity(255)
#        yield g.getFrame()
#        if(secs and time.time() - t >= secs):
#            return
