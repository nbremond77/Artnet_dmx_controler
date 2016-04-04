class cure():
    def __init__(self, stageSetup,  frameName,  fixtureList,  valueList, groupList,  groupValueList,  transitionDuration = 0):
        # Parameters
        #   stageSetup = MyStageSetup
        #   frameName = "Cue blue ambiance"
        #   fixtureList  = ["Chauvet_RGB56#1", "Chauvet_RGB56#2", "Chauvet_RGB56#3", "Chauvet_RGB56#4"]
        #   valueList =  [[10, 120, 30, "RGB"], [10, 120, 30, "Color"], [10, 120, 30, "Auto"], [10, 120, 30, "Music"]]
        #   groupList = ["group1", "group2"]
        #   groupValueList = [[10, 120, 30, "RGB"], [10, 120, 30, "RGB"]]
        #   transitionDuration = 3

        self.stageSetup = stageSetup
        self.name = cueName
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
