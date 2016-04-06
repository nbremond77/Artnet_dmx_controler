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



logging.basicConfig(format='%(levelname)s:%(message)s', filename='artNet_controller.log', level=logging.DEBUG)
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
    #log.debug(frameList)
    return render_template('layout_1.html',  buttonList=frameList,  imageList=imageList,  page=currentPage)


@app.route('/framePicture', methods = ['POST'])
def framePicture():
    log.debug("POST - Frame1")
    frameName = request.form['Frame']
    log.debug(frameName)
    for i in frameList:
        #print(i)
        #print(i['name'])
        if (i['name'] == frameName):
            currentFrame = i
            log.debug('-->FOUND: %s' % currentFrame)
            break
    #log.debug(currentFrame)
    return redirect('/')

@app.route('/nextPage', methods = ['GET'])
def nextPage():
    global currentPage
    currentPage = min(currentPage+1,  MAX_PAGES)
    log.debug("GET - next - %s" %  currentPage)
    return redirect('/')

@app.route('/previousPage', methods = ['GET'])
def previousPage():
    global currentPage
    currentPage = max(currentPage-1,  1)
    log.debug("GET - previous - %s" %  currentPage)
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

def all_white(g):
    """
    Create an all-red frame.
    """
    g.setColor('#bbbbbb22')
    g.setIntensity(255)
    return g.getFrame()    

def all_gray(g):
    """
    Create an all-red frame.
    """
    g.setColor('#80808033')
    g.setIntensity(120)
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
    myRig.load("/home/nbremond/myCloud/Projets_NBR/Electronique/ArtNet DMX Controller/Artnet_dmx_controler/rigs/my-rig_2.yaml")
    myRig.printRig()
    
    g = myRig.groups['all']
    g1 = myRig.groups['odds']
    g2 = myRig.groups['evens']
    g3 = myRig.groups['dimmers']
    

    log.info("Running script %s" % __name__)
    # global g
    # g = get_default_fixture_group(config)
#    q = controller or dmx_controller.Controller(config.get('base', 'address'), bpm=60, nodaemon=True, runout=True)
    address = "192.168.0.82"
#    address = ""

    log.debug("Configure DMX controller")

    q = dmx_controller.Controller(address, bpm=30, fps=40,  nodaemon=True, runout=False)

    log.debug("add effect")

#    q.add(dmx_effects.create_multifade([
#        all_red(g),
#        all_blue(g),
#    ] * 60, secs=3.0))
    
#    q.add(dmx_effects.create_multiframe([all_gray(g),  all_white(g)]*60, secs=3.0))
#    q.add(dmx_effects.create_multifade([all_gray(g1),  all_white(g1)]*60, secs=60.0)) # Color
#    q.add(dmx_effects.create_multiframe([all_red(g2),  all_blue(g2)]*60, secs=60.0)) # Color
    q.add(dmx_effects.create_multiframe([all_gray(g3),  all_white(g3)]*60, secs=90.0)) # Dimmer
    
    log.debug("Start DMX controller")
    q.start()

    log.debug("Continue initialization")


#    time.sleep(5)

    # Start DMX thread
#    myDMXthread = dmx_NBRLib.DMX_Thread(theStage,  Tsample,  hostIP)
#    myDMXthread.start()
    
    # Run the web server on port 5000
    print("Run the web server on port 5000")
    log.debug("Run the web server on port 5000")
    app.run('0.0.0.0')
    
    # stop the DMX thread
#    myDMXthread.stop()

    log.debug("End of processing.")
