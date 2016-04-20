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

# Run in development mode... for now
import os
import config
from flask import Flask, url_for
from flask import render_template, request,  flash,  redirect
import time
import logging

from artnet import shared
#logging.basicConfig(format='%(levelname)s:%(message)s', filename='artNet_controller.log', level=logging.DEBUG)
#log = logging.getLogger(__name__)


os.system('export APP_SETTINGS="config.ProductionConfig"')
# Create the application
app = Flask(__name__)


# Load app configuration
#app.config.from_object(os.environ['APP_SETTINGS'])
#app.config.from_object(config.DevelopmentConfig)
app.config.from_object(config.ProductionConfig)



from artnet import dmx_rig
from artnet import dmx_fixture
from artnet import dmx_frame
from artnet import dmx_chase
from artnet import dmx_show
from artnet import dmx_cue
from artnet import dmx_controller
from artnet import dmx_effects

#import dmx_NBRLib
from colour import Color
#import colorsys

DEG30 = 30/360

def adjacent_color(c, d=DEG30): # Assumption: c : color as defined in the colour library
    #r, g, b = map(lambda x: x/255., [r, g, b]) # Convert to [0, 1]
    #h, l, s = colorsys.rgb_to_hls(r, g, b)     # RGB -> HLS
    (h,  s,  l) = C.hsl
    h = [(h+d) % 1 for d in (-d, d)]           # Rotation by d
    #adjacent = [map(lambda x: int(round(x*255)), colorsys.hls_to_rgb(hi, l, s))
    #        for hi in h] # H'LS -> new RGB
    newColor = Color(hue=h, saturation=s, luminance=l)
    return newColor
    

colorList = {}
colorList['Orange']="orange"
colorList['Jaune-Orange']="gold"
colorList['Jaune']="yellow"
colorList['Vert-Clair']="yellowgreen"
colorList['Vert']="green"
colorList['Turquoise']="turquoise"
colorList['Bleu-Ciel']="lightskyblue"
colorList['Bleu']="blue"
colorList['Bleu-Fonce']="darkblue"
colorList['Outremer']="mediumblue"
colorList['Blue-Violet']="blueviolet"
colorList['Violet']="purple"
colorList['Magenta']="magenta"
colorList['Rouge']="red"
colorList['Rouge-Orange']="orangered"

mainColor = Color('black')

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



#Tsample = 2 # sampling time in seconds
TIMEOUT = 5*60 # Time in second before blackout when no action is done
hostIP = "192.168.0.82" # Target for the ArtNet frames, or empty for broadcast

# Create and load the current rig pararmeters
#    myRig =  rig_setup.get_default_rig()
myRig = dmx_rig.Rig()
myRig.load("rigs/my-rig_2.yaml")
myRig.printRig()


shared.log.info("Running script %s" % __name__)
# global g
# g = get_default_fixture_group(config)
#    q = controller or dmx_controller.Controller(config.get('base', 'address'), bpm=60, nodaemon=True, runout=True)
address = "192.168.0.82"
#    address = ""

shared.log.debug("Configure DMX controller")

#    q = dmx_controller.Controller(address, bpm=30, fps=20,  nodaemon=True, runout=False,  universe=1)
q = dmx_controller.Controller(address, bpm=30, fps=20,  timeout=TIMEOUT,  nodaemon=True, runout=False,  universe=1)
    
    

@app.route('/', methods=['GET', 'POST'])
def index():
    #shared.log.debug(frameList)
    print('main_layout')
    return render_template('main_layout.html',  buttonList=frameList,  imageList=imageList,  page=currentPage)


@app.route('/sceneButton', methods = ['POST'])
def sceneButton():
    print('scene button')
    shared.log.debug("POST - Frame1")
    frameName = request.form['Frame']
    shared.log.debug(frameName)
    for i in frameList:
        #print(i)
        #print(i['name'])
        if (i['name'] == frameName):
            currentFrame = i
            shared.log.debug('-->FOUND: %s - %s' % (frameName,  currentFrame))


            
            shared.log.debug("add effect 2")
            q.removeAll()
            q.add(dmx_effects.create_frameListRun(q.get_clock(), frames=[
                all_gray(g3),  
                all_white(g3), 
                all_red(g1),
                all_blue(g1),
                ]*20, frameDurations=[ 5,  10,  15,  20]*20, 
                frameTransitionTimes=[ 1,  2,  4,  8]*20))

    
            print("Run 1st effect")
            shared.log.info("Run 1st effect")

            break
    #shared.log.debug(currentFrame)
    return redirect('/')

@app.route('/next', methods = ['GET'])
def next():
    global currentPage
    print('next')
    currentPage = min(currentPage+1,  MAX_PAGES)
    shared.log.debug("GET - next - %s" %  currentPage)

#    q.removeAll()
#    q.add(dmx_effects.create_multiframe([all_red(g2),  all_blue(g2)]*10, totalDuration=30.0)) # Color
    return redirect('/')

@app.route('/previous', methods = ['GET'])
def previous():
    print('previous')
    global currentPage
    currentPage = max(currentPage-1,  1)
    shared.log.debug("GET - previous - %s" %  currentPage)

#    q.removeAll()
#    q.add(dmx_effects.create_multifade([all_red(g1),  all_blue(g1)]*10, totalDuration=30.0)) # Color
    return redirect('/')    

@app.route('/Vert', methods = ['GET'])
def vert():
    print('vert')
    global mainColor
    mainColor = Color(colorList['Vert'])
    shared.log.debug("Color: %s" %  mainColor)
    return redirect('/')    

@app.route('/Turquoise', methods = ['GET'])
def turquoise():
    print('turquoise')
    global mainColor
    mainColor = Color(colorList['Turquoise'])
    shared.log.debug("Color: %s" %  mainColor)
    return redirect('/')    

@app.route('/Magenta', methods = ['GET'])
def magenta():
    print('magenta')
    global mainColor
    mainColor = Color(colorList['Magenta'])
    shared.log.debug("Color: %s" %  mainColor)
    return redirect('/')    

@app.route('/Violet', methods = ['GET'])
def violet():
    print('violet')
    global mainColor
    mainColor = Color(colorList['Violet'])
    shared.log.debug("Color: %s" %  mainColor)
    return redirect('/')    

@app.route('/BleuFonce', methods = ['GET'])
def bleuFonce():
    print('bleuFonce')
    global mainColor
    mainColor = Color(colorList['Bleu-Fonce'])
    shared.log.debug("Color: %s" %  mainColor)
    return redirect('/')    

@app.route('/BleuCiel', methods = ['GET'])
def bleuCiel():
    print('bleuCiel')
    global mainColor
    mainColor = Color(colorList['Bleu-Ciel'])
    shared.log.debug("Color: %s" %  mainColor)
    return redirect('/')  

@app.route('/Outremer', methods = ['GET'])
def outremer():
    print('outremer')
    global mainColor
    mainColor = Color(colorList['Outremer'])
    shared.log.debug("Color: %s" %  mainColor)
    return redirect('/')  


@app.route('/Rouge', methods = ['GET'])
def rouge():
    print('rouge')
    global mainColor
    mainColor = Color(colorList['Rouge'])
    shared.log.debug("Color: %s" %  mainColor)
    return redirect('/')  

@app.route('/Orange', methods = ['GET'])
def orange():
    print('orange')
    global mainColor
    mainColor = Color(colorList['Orange'])
    shared.log.debug("Color: %s" %  mainColor)
    return redirect('/')  

@app.route('/Jaune', methods = ['GET'])
def jaune():
    print('jaune')
    global mainColor
    mainColor = Color(colorList['Jaune'])
    shared.log.debug("Color: %s" %  mainColor)
    return redirect('/')  
    
@app.route('/Toilette')
def toilette():
    print('Toilette')
    shared.log.debug("Toilette")
    q.removeAll()
    q.add(iter([[255] * 512]))   
    return redirect('/')  

    
@app.route('/Douche')
def douche():
    print('Douche')
    q.removeAll()
    q.add(iter([[0] * 512]))
    return redirect('/')  

@app.route('/Bain')
def bain():
    print('Bain')
    q.removeAll()
    q.add(iter([[0] * 512]))
    return redirect('/')  


def all_red(g):
    """
    Create an all-red frame.
    """
    g.setColor('#fe0000')
    g.setIntensity(55)
    return g.getFrame()

def all_blue(g):
    """
    Create an all-blue frame.
    """
    g.setColor('#0000ef')
    g.setIntensity(160)
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

#    cueName = 'myCue1'
#    fixtureList = {
#        'slimpar_1': {'setColor': '#FE1233BB', 'setStrobe':12, 'setIntensity':200}, 
#        'slimpar_2': {'setColor': '#FE1233', 'setIntensity':200}, 
#        'slimpar_4': {'setIntensity':200}
#        }
#    groupList = {
#        'odds': {'setColor': '#FE1233BB', 'setStrobe':12, 'setIntensity':200}
#        }
#    myCue1 = Cue(cueName, fixtureList={},  groupList={},  effectList = {}, initialTransitionDuration = 0)
#    myCue1 = dmx_cue.Cue(cueName, fixtureList,  groupList,  {}, initialTransitionDuration = 2)
#    print(myCue1)
    
#    myFrame = myCue1.getFrame()
#    print(myFrame)


#    q.run()

#    q.add(dmx_effects.create_multiframe([all_gray(g),  all_white(g)]*60, totalDuration=3.0))
#    q.add(dmx_effects.create_multifade([all_gray(g1),  all_white(g1)]*60, totalDuration=60.0)) # Color

#    q.add(dmx_effects.create_multiframe([all_gray(g3),  all_white(g3)]*3, totalDuration=10.0)) # Dimmer
#    print("Run 2nd effect")
#    shared.log.info("Run 2nd effect")
#    q.run()
    


#    q.run()
    

    
#    q2 = dmx_controller.Controller(address, bpm=30, fps=20,  nodaemon=True, runout=False,  universe=1)
#    q.add(dmx_effects.create_multiframe([all_red(g2),  all_blue(g2)]*60, totalDuration=60.0)) # Color
#    print("Start DMX controller with other effect")
    shared.log.info("Start DMX controller with other effect")
    q.start()

    shared.log.debug("Continue initialization")


#    time.sleep(5)

    # Start DMX thread
#    myDMXthread = dmx_NBRLib.DMX_Thread(theStage,  Tsample,  hostIP)
#    myDMXthread.start()
    
    # Run the web server on port 5000
    print("Run the web server on port 5000")
    shared.log.debug("Run the web server on port 5000")
    app.run('0.0.0.0')
    
    # stop the DMX thread
#    myDMXthread.stop()

    shared.log.debug("End of processing.")
