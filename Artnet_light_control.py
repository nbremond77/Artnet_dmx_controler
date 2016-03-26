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
from flask import render_template

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])


@app.route('/')
def mainLayout():
    """short description of the function square

    longish explanation: returns the square of a: :math:`a^2`

    :param a: an input argument

    :returns: a*a
    """
    with app.test_request_context():
        print url_for('setup')
        print url_for('about')
        print url_for('page', page='Page1')    

    return "ArtNet Light Control - main layout"


@app.route('/page/<page>')
def pageLayout(page=None):
    """short description of the function square

    longish explanation: returns the square of a: :math:`a^2`

    :param a: an input argument

    :returns: a*a
    """
#    return "ArtNet Light Control - layout %s" % page
    return render_template('layout_1.html', page=page)
   

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
    app.run('192.168.0.0')