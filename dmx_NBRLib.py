## @package pyexample
#  Documentation for this module.
#
#  More details.

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)

import logging


class DMXelement():
    def __init__(self, name, offsetDMXaddress, addressNbOfByte=1,  softTransition=True,  disreteValues={}):

        self.name = name
        self.baseDMXaddress = 0
        self.offsetDMXaddress = offsetDMXaddress
        self.addressNbOfByte = addressNbOfByte
        self.softTransition = softTransition
        self.disreteValues  = disreteValues

        self.minValue = 0
        self.maxValue = 255
        self.gain = 1.0
        self.offset = 0

        self.DMXvalue = 0
        self.DMXtargetValue = 0
        self.DMXtargetTime = 0.0
        self.DMXincrement = 0.0
        self.DMXoverrideValue = 0
        self.DMXoldValue = 0
        self.DMXdefaultValue = 0

        self.isOverrided = False

    def setBaseDMXaddress(self, baseDMXaddress):
        if baseDMXaddress > 0:
            self.baseDMXaddress = baseDMXaddress
        else:
            self.baseDMXaddress = 0

        logging.debug("setBaseDMXaddress: DMX Element %s : set baseDMXaddress: %s, offset: %s --> %s -- %s", self.name, self.baseDMXaddress, self.offsetDMXaddress, self.baseDMXaddress + self.offsetDMXaddress, self)


    def setGainAndOffset(self, gain, offset, minValue, maxValue):
        self.minValue = minValue
        self.maxValue = maxValue
        self.gain = gain
        self.offset = offset
        #print("DMX: ", self.name, " Set gain to : ", self.gain)

    def getGainAndOffset(self):
        return self.gain, self.offset, self.minValue, self.maxValue


    def resetToDefaultValue(self):
        self.DMXvalue = self.DMXdefaultValue
        self.DMXtargetValue = self.DMXdefaultValue
        self.DMXoverrideValue = self.DMXdefaultValue
        self.DMXoldValue = self.DMXdefaultValue - 1 # Set a different value to force sending the data to DMX
        self.isOverrided = False

    def resetOverride(self):
        self.isOverrided = False

    def isOverrided(self):
        return self.isOverrided


    def calculateDMXdata(self, DMXdata, currentTime, forceOutput = False):

        if self.addressNbOfByte > 0:
            mask = int("0xFF", 16)
            
            if (currentTime > self.DMXtargetTime) or (self.softTransition == False):
                self.DMXvalue = self.DMXtargetValue
            else: 
                if (self.DMXvalue != self.DMXtargetValue):
                    self.DMXvalue = self.DMXvalue + self.DMXincrement

            # Compare new and old values
            if self.isOverrided:
                if (self.DMXoverrideValue != self.DMXoldValue) or forceOutput:
                    if self.addressNbOfByte == 1:
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress] = self.DMXoverrideValue
                    elif self.addressNbOfByte == 2:
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress + 1] = (self.DMXoverrideValue >> 8) & mask
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress] = self.DMXoverrideValue & mask
                    elif self.addressNbOfByte == 3:
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress + 2] = (self.DMXoverrideValue >> 16) & mask
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress + 1] = (self.DMXoverrideValue >> 8) & mask
                        DMXdata[self.baseDMXaddress] = self.DMXoverrideValue & mask
                    elif self.addressNbOfByte == 4:
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress + 3] = (self.DMXoverrideValue >> 24) & mask
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress + 2] = (self.DMXoverrideValue >> 16) & mask
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress + 1] = (self.DMXoverrideValue >> 8) & mask
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress] = self.DMXoverrideValue & mask

                    self.DMXoldValue = self.DMXoverrideValue
            else:
                if (self.DMXvalue != self.DMXoldValue) or forceOutput:
                    if self.addressNbOfByte == 1:
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress] = self.DMXvalue
                    elif self.addressNbOfByte == 2:
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress + 1] = (self.DMXvalue >> 8) & mask
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress] = self.DMXvalue & mask
                    elif self.addressNbOfByte == 3:
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress + 2] = (self.DMXvalue >> 16) & mask
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress + 1] = (self.DMXvalue >> 8) & mask
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress] = self.DMXvalue & mask
                    elif self.addressNbOfByte == 4:
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress + 3] = (self.DMXvalue >> 24) & mask
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress + 2] = (self.DMXvalue >> 16) & mask
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress + 1] = (self.DMXvalue >> 8) & mask
                        DMXdata[self.baseDMXaddress + self.offsetDMXaddress] = self.DMXvalue & mask

                    self.DMXoldValue = self.DMXvalue

        return DMXdata


    def setValue(self, value,  transitionDuration = 0.0,  currentTime = 0.0,  sampleTime = 1.0):
        if self.addressNbOfByte > 0:
            self.DMXtargetValue = int(value*self.gain + self.offset)
        else:
            self.DMXtargetValue = 0

        if self.DMXtargetValue > self.maxValue:
            self.DMXtargetValue = self.maxValue

        if self.DMXtargetValue < self.minValue:
            self.DMXtargetValue = self.minValue

        self.DMXtargetTime = currentTime + transitionDuration
        if transitionDuration >= sampleTime:
            self.DMXincrement = (self.DMXtargetValue - self.DMXvalue)*sampleTime/transitionDuration
        else:
            self.DMXincrement = 0
            self.DMXvalue = self.DMXtargetValue
### MANQUE GESTION DES MODES DISCRET...

    def setOverrideValue(self, value):
        self.isOverrided = True
        if self.addressNbOfByte > 0:
            self.DMXoverrideValue = int(value*self.gain + self.offset)

        if self.DMXoverrideValue > self.maxValue:
            self.DMXoverrideValue = self.maxValue

        if self.DMXoverrideValue < self.minValue:
            self.DMXoverrideValue = self.minValue
### MANQUE GESTION DES MODES DISCRET...


class DMXfixture():
    def __init__(self, fixtureName, baseDMXaddress, fixtureDMXelements,  fixtureDMXnbOfBytes,  softTransition,  disreteValues):
        # Parameters
        #   fixtureName = "Chauvet_RGB56#1"
        #   offsetDMXaddress  = 0x10
        #   fixtureDMXelements = ["R", "G", "B", "Mode"]
        #   fixtureDMXnbOfBytes = [1, 1, 1, 1]
        #   softTransition = [True, True, True, False]          // True for analog values, False for mode and discrete values
        #   disreteValues = [{}, {}, {}, {'RGB':1, 'Color':10, 'Auto':20, 'Music':30}] // List of possible values for discrete parameters

        self.name = fixtureName
        self.baseDMXaddress = baseDMXaddress
        self.fixtureDMXelements = fixtureDMXelements
        self.fixtureDMXnbOfBytes = fixtureDMXnbOfBytes
        self.softTransition = softTransition
        self.disreteValues = disreteValues
        self.elementList = []
        offset = 0

        # Create the required DMXelement
        for i, elt in enumerate(self.fixtureDMXelements):
            theDMXelement = DMXelement(elt, baseDMXaddress + offset, fixtureDMXnbOfBytes[i], softTransition[i],  disreteValues[i] )
            theDMXelement.setBaseDMXaddress(baseDMXaddress + offset)
            offset = offset + fixtureDMXnbOfBytes[i]
            self.elementList.append(theDMXelement)


    def setValue(self,  values,  transitionDuration = 0,  currentTime = 0.0,  sampleTime = 1.0):
        # Parameters
        #   values = [10, 120, 30, "RGB"]
        #   ...
        for i, elt in enumerate(self.elementList):
            elt.setValue(values[i],  transitionDuration,  currentTime,  sampleTime)


    def setOverrideValue(self,  values):
        # Parameters
        #   values = [10, 120, 30, "RGB"]
        #   ...
        for i, elt in enumerate(self.elementList):
            elt.setOverrideValue(values[i])


    def resetToDefaultValue(self):
        for i, elt in enumerate(self.elementList):
            elt.resetToDefaultValue()


    def resetOverride(self):
        for i, elt in enumerate(self.elementList):
            elt.resetOverride()        


    def calculateDMXdata(self,  DMXdata, currentTime, forceOutput = False):
        for i, elt in enumerate(self.elementList):
            DMXdata = elt.calculateDMXdata(DMXdata, currentTime, forceOutput)
        
        return DMXdata
        
    def GetFixture(self,  fixtureName):
        if fixtureName == self.name:
            return self
        else:
            return None



class stageSetup():
    def __init__(self, setupName,  fixtureList = [],  groupList = []):
        # Parameters
        #   setupName = "Théatre du rond point - Scene 1"
        #   fixtureList  = [fixture1, fixture2, fixture3, fixture4]
        #   groupList = ["group1", "group2", "group3"}
        self.name = setupName
        self.fixtureList = fixtureList
        self.groupList = groupList

    
    def addFixture(self,  fixture):
        self.fixtureList.append(fixture)
        
    def addFixtureToGroupList(self, groupName,  fixture):
        self.groupList[groupName].append(fixture)
        
    def getFixtureList(self):
        return self.fixtureList

#    def getFixtureAddressList(self,  myFixtureList):
#        fixtureAddressList = {}
#        for fixture in myFixtureList:
#            for elt in self.fixtureList:
#                if elt.GetFixture(fixtureName) != None:
#                    fixtureAddressList.append(elt)
#        return fixtureAddressList

    def getAllFixtureAddressList(self):
        return self.fixtureList



class scene():
    def __init__(self, stageSetup,  sceneName,  fixtureList,  valueList, groupList,  groupValueList,  transitionDuration = 0):
        # Parameters
        #   stageSetup = MyStageSetup
        #   sceneName = "Scene intime"
        #   fixtureList  = ["Chauvet_RGB56#1", "Chauvet_RGB56#2", "Chauvet_RGB56#3", "Chauvet_RGB56#4"]
        #   valueList =  [[10, 120, 30, "RGB"], [10, 120, 30, "Color"], [10, 120, 30, "Auto"], [10, 120, 30, "Music"]]
        #   groupList = ["group1", "group2"]
        #   groupValueList = [[10, 120, 30, "RGB"], [10, 120, 30, "RGB"]]
        #   transitionDuration = 3

        self.stageSetup = stageSetup
        self.name = sceneName
        self.fixtureList = fixtureList
        self.valueList = valueList
        self.groupList = groupList
        self.groupValueList = groupValueList
        self.transitionDuration = transitionDuration
#        self.fixtureAddressList = stageSetup.getFixtureAddressList(fixtureList)
#        self.fixtureAddressList = fixtureList


    def updateFixtureValues(self,  fixtureList,  valueList,  transitionDuration):
        self.fixtureList = fixtureList
        self.valueList = valueList
        self.transitionDuration = transitionDuration
#        self.fixtureAddressList = self.stageSetup.getFixtureAddressList(self.fixtureList)
#        self.fixtureAddressList = self.stageSetup.getFixtureAddressList(self.fixtureList)

    def updateValues(self,  valueList,  transitionDuration):
        self.valueList = valueList
        self.transitionDuration = transitionDuration

    def getFixtureList(self):
        return self.fixtureList
    
#    def getFixtureAddressList(self):
#        return self.fixtureAddressList
    
    def getValueList(self):
        return self.valueList
    
    def getTransitionDuration(self):
        return self.transitionDuration
    
    def activate(self,  currentTime=0.0, sampleTime=1.0):
        # Set the value of the fixture
#        for i, elt in enumerate(self.fixtureAddressList):
        for i, elt in enumerate(self.fixtureList):
            elt.setValue( self.valueList[i],  self.transitionDuration,  currentTime,  sampleTime)

        # Set the values of the fixture of the group
        for i, group in enumerate(self.groupList):
            for j, listOfFixture in enumerate(self.stageSetup.groupList[group]):
                for k, fixture in enumerate(listOfFixture):
                    fixture.setValue( self.groupValueList[i],  self.transitionDuration,  currentTime,  sampleTime)


class chase():
    def __init__(self, stageSetup,  chaseName,  sceneList,  sceneTiming):
        self.stageSetup = stageSetup
        self.chaseName = chaseName
        self.scenelist = sceneList
        self.sceneTiming = sceneTiming
