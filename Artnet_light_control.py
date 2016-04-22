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

from colour import Color

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
#import colorsys

DEG30 = 30/360
DEG180 = 180/360
DEG120 = 120/360

# Calculate colors on the color wheel: shifting colors based on the current color given in parameter
def adjacent_color(c, d=DEG30): # Assumption: c : color as defined in the colour library
    #r, g, b = map(lambda x: x/255., [r, g, b]) # Convert to [0, 1]
    #h, l, s = colorsys.rgb_to_hls(r, g, b)     # RGB -> HLS
    (h,  s,  l) = c.hsl
#    h = [(h+d) % 1 for d in (-d, d)]           # Rotation by d
    h = (h+d) % 1           # Rotation by d
    #adjacent = [map(lambda x: int(round(x*255)), colorsys.hls_to_rgb(hi, l, s))
    #        for hi in h] # H'LS -> new RGB
    newColor = Color(hue=h, saturation=s, luminance=l)
    return newColor


# Default colors, based on the main color
mainColor = Color('black')
sideColor1 = adjacent_color(mainColor, DEG30)
sideColor2 = adjacent_color(mainColor, -DEG30)
triadColor1 = adjacent_color(mainColor, DEG120)
triadColor2 = adjacent_color(mainColor, -DEG120)
complementColor = adjacent_color(mainColor, DEG180)
sideComplementColor1 = adjacent_color(complementColor, DEG30)
sideComplementColor2 = adjacent_color(complementColor, -DEG30)
colorList = [mainColor.hex,  sideColor1.hex,  sideColor2.hex, complementColor, triadColor1, triadColor2, sideComplementColor1, sideComplementColor2]
 
# Default program name 
currentProgramName = ""

# Number of HTML pages           
MAX_PAGES = 2
currentPage = 1

# Description of the HTML pages
title = "Salle de bain"
introduction="<h1>Quelle couleur pour obtenir quels effets ?</h1><p>S'il existe une symbolique arbitraire construite par les différentes cultures et civilisations, une signification réelle est intrinsèque aux couleurs, par les effets et mouvements de la nature, les phénomènes universels de la vie et le profond inconscient commun à toute l'espèce humaine. On distingue plusieurs catégories de couleurs selon leurs vertus.</p>"
imageList = ['../static/douche1.jpg',  '../static/douche6.jpg',  '../static/douche3.jpg',  '../static/douche4.jpg']
pageTitle = ['Les programmes',  'Les couleurs',  '',  '']


# Descriptions of the choices in the HTML page - Colors
choiceList=[]
aFrame = dict(name='Vert',  image='',  color='green', description="Anti-allergiques et antibiotiques", page=1)
choiceList.append(aFrame)
aFrame = dict(name='Turquoise',  image='',  color='turquoise', description="Mobilise les cycles chronobiologiques", page=1)
choiceList.append(aFrame)
aFrame = dict(name='Magenta',  image='',  color='magenta', description="Représente la fusion, l'amour, le rêve mais également la vulnérabilité", page=1)
choiceList.append(aFrame)
aFrame = dict(name='Violet',  image='',  color='purple', description="Est un immunostimulant, pour la circulation veineuse et contre les migraines", page=1)
choiceList.append(aFrame)
aFrame = dict(name='Bleu Foncé',  image='',  color='darkblue', description="On le préconise comme somnifère et antibactérien, détuméfiant. Il participe de la synchronisation entre les deux hémisphères cérébraux", page=1)
choiceList.append(aFrame)
aFrame = dict(name='BleuCiel',  image='',  color='lightskyblue', description="Symbolise le souffle, la communication, l'échange, le partage. Il est anti-inflammatoire et rafraîchissant", page=1)
choiceList.append(aFrame)
aFrame = dict(name='Outremer',  image='mediumblue',  color='green', description="Inhibiteur et antistress. Il porte la tempérance, le calme et l'introspection", page=1)
choiceList.append(aFrame)
aFrame = dict(name='Rouge',  image='',  color='red', description="Il permet de tonifier et dynamiser par ses vertus anti-anémiques", page=1)
choiceList.append(aFrame)
aFrame = dict(name='Orange',  image='',  color='orange', description="On l'utilise en anti-dépresseur ou stimulant neurosensoriel", page=1)
choiceList.append(aFrame)
aFrame = dict(name='Jaune',  image='',  color='yellow', description="On s'en sert comme stimulant digestif et lymphatique, pour l'estomac et les glandes exocrines", page=1)
choiceList.append(aFrame)

aFrame = dict(name='Vert',  image='',  color='green', description="Anti-allergiques et antibiotiques", page=2)
choiceList.append(aFrame)
aFrame = dict(name='Turquoise',  image='',  color='turquoise', description="Mobilise les cycles chronobiologiques", page=2)
choiceList.append(aFrame)
aFrame = dict(name='Magenta',  image='',  color='magenta', description="Représente la fusion, l'amour, le rêve mais également la vulnérabilité", page=2)
choiceList.append(aFrame)
aFrame = dict(name='Violet',  image='',  color='purple', description="Est un immunostimulant, pour la circulation veineuse et contre les migraines", page=2)
choiceList.append(aFrame)
aFrame = dict(name='Bleu Foncé',  image='',  color='darkblue', description="On le préconise comme somnifère et antibactérien, détuméfiant. Il participe de la synchronisation entre les deux hémisphères cérébraux", page=2)
choiceList.append(aFrame)
aFrame = dict(name='BleuCiel',  image='',  color='lightskyblue', description="Symbolise le souffle, la communication, l'échange, le partage. Il est anti-inflammatoire et rafraîchissant", page=2)
choiceList.append(aFrame)
aFrame = dict(name='Outremer',  image='mediumblue',  color='green', description="Inhibiteur et antistress. Il porte la tempérance, le calme et l'introspection", page=2)
choiceList.append(aFrame)
aFrame = dict(name='Rouge',  image='',  color='red', description="Il permet de tonifier et dynamiser par ses vertus anti-anémiques", page=2)
choiceList.append(aFrame)
aFrame = dict(name='Orange',  image='',  color='orange', description="On l'utilise en anti-dépresseur ou stimulant neurosensoriel", page=2)
choiceList.append(aFrame)
aFrame = dict(name='Jaune',  image='',  color='yellow', description="On s'en sert comme stimulant digestif et lymphatique, pour l'estomac et les glandes exocrines", page=2)
choiceList.append(aFrame)


# Descriptions of the choices in the HTML page - Programs
programList=[]
aFrame = dict(name='Tonic 5mn',  image='',  color='', description="Programme tonic rapide (5mn)", page=1)
programList.append(aFrame)
aFrame = dict(name='Tonic 10mn',  image='',  color='', description="Programme tonic", page=1)
programList.append(aFrame)
aFrame = dict(name='Paisible 5mn',  image='',  color='', description="Programme relaxant rapide (5mn)", page=1)
programList.append(aFrame)
aFrame = dict(name='Paisible 10mn',  image='',  color='', description="Programme relaxant de 10mn", page=1)
programList.append(aFrame)
aFrame = dict(name='Paisible 20mn',  image='',  color='', description="Programme relaxant de 20 mn", page=1)
programList.append(aFrame)
aFrame = dict(name='Paisible 30mn',  image='',  color='', description="Programme relaxant de 30 mn", page=1)
programList.append(aFrame)
aFrame = dict(name='Fin',  image='',  color='', description="Fin de programme", page=1)
programList.append(aFrame)
aFrame = dict(name='Nuit',  image='',  color='', description="Eclairage tamisé", page=1)
programList.append(aFrame)

aFrame = dict(name='Neutralisantes, nettoyantes et équilibrantes',  image='',  color='', description="<p><b>Vert:</b> A des vertus anti-allergiques et antibiotiques. Il représente l'indépendance, la nature, la liberté mais aussi la solitude et l'apprentissage.</p><p><b>Turquoise:</b> Mobilise les cycles chronobiologiques. Il symbolise la transformation, l'évolution, l'élimination et la purification.</p>", page=2)
programList.append(aFrame)
aFrame = dict(name='Cicatrisantes, protectrices et régénératrices',  image='',  color='', description="<p><b>Écarlate</b> Porte la fertilité, la féminité et l'enracinement, la terre. Ses vertus sont régénératrices et régulatrices.</p><p><b>Magenta:</b> Représente la fusion, l'amour, le rêve mais également la vulnérabilité. On l'utilise comme rajeunissant et équilibrant cardiovasculaire, ou aphrodisiaque.</p><p><b>Violet:</b> Est un immunostimulant, pour la circulation veineuse et contre les migraines. Il image l'esprit, la connaissance et la spiritualité.</p>", page=2)
programList.append(aFrame)
aFrame = dict(name='Calmantes, dispersantes et sédatives',  image='',  color='', description="<p><b>Bleu foncé:</b> Représente la nuit, l'inconscient, la méditation et la profondeur. On le préconise comme somnifère et antibactérien, détuméfiant. Il participe de la synchronisation entre les deux hémisphères cérébraux.</p><p><b>Bleu ciel:</b> Symbolise le souffle, la communication, l'échange, le partage. Il est anti-inflammatoire et rafraîchissant.</p><p><b>Outremer:</b> Est un inhibiteur et antistress. Il porte la tempérance, le calme et l'introspection.</p>", page=2)
programList.append(aFrame)
aFrame = dict(name='Énergisantes et tonifiantes',  image='',  color='', description="<p><b>Rouge:</b> Symbolise la chaleur, la vitalité, l'engagement et le courage. Il permet de tonifier et dynamiser par ses vertus anti-anémiques.</p><p><b>Orange:</b> Est un excitant qui stimule l'adrénaline. Il caractérise les mouvements, les rythmes et symbolise l'émotion, le contact. On l'utilise en anti-dépresseur ou stimulant neurosensoriel.</p><p><b>Jaune:</b> Représente le soleil, la conscience, la lucidité, le rayonnement personnel. On s'en sert comme stimulant digestif et lymphatique, pour l'estomac et les glandes exocrines.</p>", page=2)
programList.append(aFrame)


TIMEOUT = 5*60 # Time in second before blackout when no action is done
hostIP = "192.168.0.82" # Target address for the ArtNet frames, or empty for broadcast

# Create and load the current rig parameters
myRig = dmx_rig.Rig()
myRig.load("rigs/my-rig_3.yaml")
myRig.printRig()


shared.log.debug("Configure DMX controller")
#    q = dmx_controller.Controller(hostIP, bpm=30, fps=20,  nodaemon=True, runout=False,  universe=1)
q = dmx_controller.Controller(hostIP, bpm=30, fps=20,  timeout=TIMEOUT,  nodaemon=True, runout=False,  universe=1)
    
    
# Definition of the HTML routes for Flask framework
@app.route('/', methods=['GET', 'POST'])
def index():
    #shared.log.debug(choiceList)
    print('main_layout')
    return render_template('main_layout.html',  title = title, pageTitle = pageTitle,  buttonList=choiceList,  imageList=imageList,  page=currentPage, maxPage=MAX_PAGES,  introduction=introduction,  programList=programList,  colorList=colorList)


@app.route('/scene', methods = ['POST'])
def scene():
    global colorList
    print('scene')
    shared.log.debug("POST - scene")
    sceneName = request.form['Scene']
    shared.log.debug(sceneName)
    for i in choiceList:
        #print(i)
        #print(i['name'])
        if (i['name'] == sceneName):
            currentScene = i
            shared.log.debug('-->FOUND: %s - %s' % (sceneName,  currentScene))
            print('-->FOUND: %s - %s' % (sceneName,  currentScene))
        
            mainColor = Color(currentScene['color'])
            sideColor1 = adjacent_color(mainColor, DEG30)
            sideColor2 = adjacent_color(mainColor, -DEG30)
            triadColor1 = adjacent_color(mainColor, DEG120)
            triadColor2 = adjacent_color(mainColor, -DEG120)
            complementColor = adjacent_color(mainColor, DEG180)
            sideComplementColor1 = adjacent_color(complementColor, DEG30)
            sideComplementColor2 = adjacent_color(complementColor, -DEG30)
            
            colorList = [mainColor.hex,  sideColor1.hex,  sideColor2.hex, complementColor, triadColor1, triadColor2, sideComplementColor1, sideComplementColor2]
            shared.log.debug('   MainColor: %s | %s | %s - %s ** %s' % (currentScene['color'],  mainColor.hex,  sideColor1.hex,  sideColor2.hex, complementColor.hex))
            print('   MainColor: %s | %s | %s - %s ** %s' % (currentScene['color'],  mainColor.hex,  sideColor1.hex,  sideColor2.hex, complementColor.hex))
            
            # Udpate the colors in the Cues
            
            # Start the light program
            if (currentProgramName <> ""):
                if currentProgramName in chaseList:
                    q.removeAll()
                    q.add(dmx_effects.create_chaseRun(q.get_clock(), chaseList[currentProgramName]))
                    shared.log.debug('Start light program [%s] with color %s' % (currentProgramName, mainColor))
                    print('Start light program [%s] with color %s' % (currentProgramName, mainColor))
            break

            break

    #shared.log.debug(currentFrame)
    return redirect('/')

@app.route('/program', methods = ['POST'])
def program():
    print('program')
    shared.log.debug("POST - program")
    programName = request.form['Program']
    shared.log.debug(programName)
    for i in programList:
        if (i['name'] == programName):
            currentProgram = i
            currentProgramName = programName
            shared.log.debug('-->FOUND: %s - %s' % (programName,  currentProgram))
            print('-->FOUND: %s - %s' % (programName,  currentProgram))
            
            # Start the light program
            if (currentProgramName <> ""):
                if currentProgramName in chaseList:
                    q.removeAll()
                    q.add(dmx_effects.create_chaseRun(q.get_clock(), chaseList[currentProgramName]))
                    shared.log.debug('Start light program [%s] with color %s' % (currentProgramName, mainColor))
                    print('Start light program [%s] with color %s' % (currentProgramName, mainColor))
            break
    return redirect('/')
    
@app.route('/next', methods = ['GET'])
def next():
    global currentPage
    print('next')
    currentPage = min(currentPage+1,  MAX_PAGES)
    shared.log.debug("GET - next - %s" %  currentPage)
    return redirect('/')

@app.route('/previous', methods = ['GET'])
def previous():
    print('previous')
    global currentPage
    currentPage = max(currentPage-1,  1)
    shared.log.debug("GET - previous - %s" %  currentPage)
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
    q.add(iter([[180] * 512]))
    return redirect('/')  

@app.route('/Bain')
def bain():
    print('Bain')
    q.removeAll()
    q.add(iter([[128] * 512]))
    return redirect('/')  


@app.route('/OFF')
def OFF():
    print('Bain')
    q.removeAll()
    q.add(iter([[0] * 512]))
    return redirect('/')  
    

    
#######################################################

if __name__ == '__main__':

    # Display HTML pages to control lights using ArtNet messages

    shared.log.info("Start DMX controller with other effect")
    q.start()
    
    # Run the web server on port 5000
    print("Run the web server on port 5000")
    shared.log.debug("Run the web server on port 5000")
    app.run('0.0.0.0')

    shared.log.debug("End of processing.")
