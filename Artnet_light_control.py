#!/usr/bin/env python
## @package artnet_light_control
#  Documentation for this module.
#
#  More details.

"""
To activate a specific settings for the application, run:
    source env/bin/activate
    export APP_SETTINGS="config.DevelopmentConfig"
    OR export APP_SETTINGS="config.ProductionConfig"
    OR export APP_SETTINGS="config.StagingConfig"
    OR export APP_SETTINGS="config.TestingConfig"
"""

from flask import Flask, url_for
from flask import render_template, request,  flash,  redirect
import os
import time
import logging

import dmx_rig
import dmx_fixture
import dmx_frame
import dmx_chase
import dmx_show
import dmx_controller
import dmx_effects

#import dmx_NBRLib



log = logging.getLogger(__name__)


frameList=[]
aFrame = dict(name='Douche_simple',  image='static/douche1.jpg',  page=1)
frameList.append(aFrame)
aFrame = dict(name='Douche_froide',  image='static/douche2.jpg',  page=1)
frameList.append(aFrame)
aFrame = dict(name='Douche_chaude',  image='static/douche3.jpg',  page=1)
frameList.append(aFrame)

aFrame = dict(name='Bain_simple',  image='static/douche1.jpg',  page=2)
frameList.append(aFrame)
aFrame = dict(name='Bain_froid',  image='static/douche2.jpg',  page=2)
frameList.append(aFrame)
aFrame = dict(name='Bain_chaude',  image='static/douche3.jpg',  page=2)
frameList.append(aFrame)

MAX_PAGES = 4
imageList = ['static/douche1.jpg',  'static/douche2.jpg',  'static/douche3.jpg',  'static/douche4.jpg']
currentPage = 1


# Create the application
app = Flask(__name__)

# Run in development mode... for now
os.system('export APP_SETTINGS="config.DevelopmentConfig"')
import config

# Load app configuration
#app.config.from_object(os.environ['APP_SETTINGS'])
app.config.from_object(config.DevelopmentConfig)


@app.route('/', methods=['GET', 'POST'])
def index():
    #print(frameList)
    return render_template('layout_1.html',  buttonList=frameList,  imageList=imageList,  page=currentPage)


@app.route('/framePicture', methods = ['POST'])
def framePicture():
    print("POST - Frame1")
    frameName = request.form['Frame']
    print(frameName)
    for i in frameList:
        #print(i)
        #print(i['name'])
        if (i['name'] == frameName):
            currentFrame = i
            print('-->FOUND: %s' % currentFrame)
            break
    #print(currentFrame)
    return redirect('/')

@app.route('/nextPage', methods = ['GET'])
def nextPage():
    global currentPage
    currentPage = min(currentPage+1,  MAX_PAGES)
    print("GET - next - %s" %  currentPage)
    return redirect('/')

@app.route('/previousPage', methods = ['GET'])
def previousPage():
    global currentPage
    currentPage = max(currentPage-1,  1)
    print("GET - previous - %s" %  currentPage)
    return redirect('/')    

@app.route('/setupPage')
def setupPage():
    return 'The configuration page'

    
@app.route('/aboutPage')
def aboutPage():
    return 'The about page'



def all_red(g):
    """
    Create an all-red frame.
    """
    g.setColor('#ff0000')
    g.setIntensity(255)
    return g.getFrame()

def all_blue(g):
    """
    Create an all-blue frame.
    """
    g.setColor('#0000ff')
    g.setIntensity(255)
    return g.getFrame()

    
    
#######################################################

if __name__ == '__main__':
    """Main Code

    Display HTML pages to control lights using ArtNet messages

    :param: none

    :returns: none
    """
    Tsample = 2 # sampling time in seconds
    hostIP = "192.168.0.82" # Target for the ArtNet frames, or empty for broadcast

    # Create and load the current rig pararmeters
#    myRig =  rig_setup.get_default_rig()
    myRig = dmx_rig.Rig()
    myRig.load("/home/nbremond/myCloud/Projets_NBR/Electronique/ArtNet DMX Controller/Artnet_dmx_controler/rigs/my-rig.yaml")
    myRig.printRig()
    
    g = myRig.groups['all']
    

    """
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


    # Create new frames
    myFrame1 = dmx_NBRLib.frame(theStage,  "Frame1",  theStage.getFixtureList(),  [[10, 120, 30, "RGB"], [10, 120, 30, "Color"], [10, 120, 30, "Auto"], [10, 120, 30, "Music"]], [],  [], 5)
    frameList.append(myFrame1)

    myFrame2 = dmx_NBRLib.frame(theStage,  "Frame2",  theStage.getFixtureList(),  [[10, 120, 30, "RGB"], [10, 120, 30, "Color"], [10, 120, 30, "Auto"], [10, 120, 30, "Music"]], [],  [], 5)
    frameList.append(myFrame2)

    myFrame3 = dmx_NBRLib.frame(theStage,  "Frame3",  theStage.getFixtureList(),  [[10, 120, 30, "RGB"], [10, 120, 30, "Color"], [10, 120, 30, "Auto"], [10, 120, 30, "Music"]], [],  [], 5)
    frameList.append(myFrame3)

    myFrame4 = dmx_NBRLib.frame(theStage,  "Frame4",  theStage.getFixtureList(),  [[10, 120, 30, "RGB"], [10, 120, 30, "Color"], [10, 120, 30, "Auto"], [10, 120, 30, "Music"]], [],  [], 5)
    frameList.append(myFrame4)

    # Create a chase
    myChase1 = dmx_NBRLib.chase(theStage,  "Chase1",  frameList,  [10,  5,  12,  11])
    chaseList.append(myChase1)

    # Activate a frame
    myFrame3.activate(time.time(), Tsample)

    # Activate a chase

    """
    ################################################################

    log.info("Running script %s" % __name__)
    # global g
    # g = get_default_fixture_group(config)
#    q = controller or dmx_controller.Controller(config.get('base', 'address'), bpm=60, nodaemon=True, runout=True)
    address = "192.168.0.82"

    print("Configure DMX controller")

    q = dmx_controller.Controller(address, bpm=60, nodaemon=True, runout=True)

    q.add(dmx_effects.create_multifade([
        all_red(g),
        all_blue(g),
    ] * 3, secs=5.0))
    
    print("Start DMX controller")
    q.start()




    # Start DMX thread
#    myDMXthread = dmx_NBRLib.DMX_Thread(theStage,  Tsample,  hostIP)
#    myDMXthread.start()
    
    # Run the web server on port 5000
    print("Run the web server on port 5000")
#    app.run('0.0.0.0')
    
    # stop the DMX thread
#    myDMXthread.stop()

