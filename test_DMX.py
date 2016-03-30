#!/usr/bin/env python
## @package test_DMX
#  Documentation for this module.
#
#  More details.

import dmx_NBRLib


fixtureList = []
groupList = []
sceneList = []
chaseList = []

sampleTime = 0.1


# Create fixtures
RGB1 = dmx_NBRLib.DMXfixture("RGB#1", 0x10, ["R", "G", "B", "Mode"],  [1, 1, 1, 1],  [True, True, True, False] ,  [{}, {}, {}, {'RGB':1, 'Color':10, 'Auto':20, 'Music':30}])
fixtureList.append(RGB1)

RGB2 = dmx_NBRLib.DMXfixture("RGB#2", 0x14, ["R", "G", "B", "Mode"],  [1, 1, 1, 1],  [True, True, True, False] ,  [{}, {}, {}, {'RGB':1, 'Color':10, 'Auto':20, 'Music':30}])
fixtureList.append(RGB2)

RGB3 = dmx_NBRLib.DMXfixture("RGB#3", 0x18, ["R", "G", "B", "Mode"],  [1, 1, 1, 1],  [True, True, True, False] ,  [{}, {}, {}, {'RGB':1, 'Color':10, 'Auto':20, 'Music':30}])
fixtureList.append(RGB3)

# Create the stage
theStage = dmx_NBRLib.stageSetup("My stage",  fixtureList,  groupList)


# Add fixture to stage
RGB4 = dmx_NBRLib.DMXfixture("RGB#4", 0x18, ["R", "G", "B", "Mode"],  [1, 1, 1, 1],  [True, True, True, False] ,  [{}, {}, {}, {'RGB':1, 'Color':10, 'Auto':20, 'Music':30}])
#fixtureList.append(RGB4)

theStage.addFixture(RGB4)


# Create new scenes
myScene1 = dmx_NBRLib.scene(theStage,  "Scene1",  theStage.getFixtureList(),  [[10, 120, 30, "RGB"], [10, 120, 30, "Color"], [10, 120, 30, "Auto"], [10, 120, 30, "Music"]], [],  [], 5)
sceneList.append(myScene1)

myScene2 = dmx_NBRLib.scene(theStage,  "Scene2",  theStage.getFixtureList(),  [[10, 120, 30, "RGB"], [10, 120, 30, "Color"], [10, 120, 30, "Auto"], [10, 120, 30, "Music"]], [],  [], 5)
sceneList.append(myScene2)

myScene3 = dmx_NBRLib.scene(theStage,  "Scene3",  theStage.getFixtureList(),  [[10, 120, 30, "RGB"], [10, 120, 30, "Color"], [10, 120, 30, "Auto"], [10, 120, 30, "Music"]], [],  [], 5)
sceneList.append(myScene3)

myScene4 = dmx_NBRLib.scene(theStage,  "Scene4",  theStage.getFixtureList(),  [[10, 120, 30, "RGB"], [10, 120, 30, "Color"], [10, 120, 30, "Auto"], [10, 120, 30, "Music"]], [],  [], 5)
sceneList.append(myScene4)

# Create a chase
myChase1 = dmx_NBRLib.chase(theStage,  "Chase1",  sceneList,  [10,  5,  12,  11])
chaseList.append(myChase1)

# Activate a scene
currentTime = 2
myScene3.activate(currentTime, sampleTime)

# Activate a chase

print("End of processing\n")
