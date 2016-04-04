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

from artnet import dmx_rig
from artnet import dmx_fixture
from artnet import dmx_frame
from artnet import dmx_chase
from artnet import dmx_show
from artnet import dmx_controller
from artnet import dmx_effects

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
#app.config.from_object(config.DevelopmentConfig)
app.config.from_object(config.ProductionConfig)


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
    

    log.info("Running script %s" % __name__)
    # global g
    # g = get_default_fixture_group(config)
#    q = controller or dmx_controller.Controller(config.get('base', 'address'), bpm=60, nodaemon=True, runout=True)
    address = "192.168.0.82"

    print("Configure DMX controller")

    q = dmx_controller.Controller(address, bpm=30, fps=40,  nodaemon=True, runout=False)

    print("add multifade effect")

    q.add(dmx_effects.create_multifade([
        all_red(g),
        all_blue(g),
    ] * 30, secs=65.0))
    
    print("Start DMX controller")
    q.start()


#    time.sleep(5)

    # Start DMX thread
#    myDMXthread = dmx_NBRLib.DMX_Thread(theStage,  Tsample,  hostIP)
#    myDMXthread.start()
    
    # Run the web server on port 5000
    print("Run the web server on port 5000")
    app.run('0.0.0.0')
    
    # stop the DMX thread
#    myDMXthread.stop()

