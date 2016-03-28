## @package pyexample
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



sceneList=[]
aScene = dict(name='Douche_simple',  image='static/douche1.jpg',  page=1)
sceneList.append(aScene)
aScene = dict(name='Douche_froide',  image='static/douche2.jpg',  page=1)
sceneList.append(aScene)
aScene = dict(name='Douche_chaude',  image='static/douche3.jpg',  page=1)
sceneList.append(aScene)

aScene = dict(name='Bain_simple',  image='static/douche1.jpg',  page=2)
sceneList.append(aScene)
aScene = dict(name='Bain_froid',  image='static/douche2.jpg',  page=2)
sceneList.append(aScene)
aScene = dict(name='Bain_chaude',  image='static/douche3.jpg',  page=2)
sceneList.append(aScene)

MAX_PAGES = 4
imageList = ['static/douche1.jpg',  'static/douche2.jpg',  'static/douche3.jpg',  'static/douche4.jpg']
currentPage = 1


# Create the application
app = Flask(__name__)

# Run in development mode... for now
os.system('export APP_SETTINGS="config.DevelopmentConfig"')

# Load app configuration
app.config.from_object(os.environ['APP_SETTINGS'])


@app.route('/', methods=['GET', 'POST'])
def index():
    #print(sceneList)
    return render_template('layout_1.html',  buttonList=sceneList,  imageList=imageList,  page=currentPage)


@app.route('/scene', methods = ['POST'])
def scene():
    print("POST - Scene1")
    sceneName = request.form['Scene']
    print(sceneName)
    for i in sceneList:
        #print(i)
        #print(i['name'])
        if (i['name'] == sceneName):
            currentScene = i
            print('-->FOUND: %s' % currentScene)
            break
    #print(currentScene)
    return redirect('/')

@app.route('/next', methods = ['GET'])
def next():
    global currentPage
    currentPage = min(currentPage+1,  MAX_PAGES)
    print("GET - next - %s" %  currentPage)
    return redirect('/')

@app.route('/previous', methods = ['GET'])
def previous():
    global currentPage
    currentPage = max(currentPage-1,  1)
    print("GET - previous - %s" %  currentPage)
    return redirect('/')    

@app.route('/setup')
def setup():
    return 'The configuration page'

    
@app.route('/about')
def about():
    return 'The about page'

    
#######################################################

if __name__ == '__main__':
    """Main Code

    Display HTML pages to control lights using ArtNet messages

    :param: none

    :returns: none
    """
    app.run('0.0.0.0')
