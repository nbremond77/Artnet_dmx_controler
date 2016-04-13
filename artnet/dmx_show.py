
import time,  logging
#from artnet import dmx_frame, dmx_fixture, dmx_effects, dmx_rig,  dmx_cue

from artnet import shared
#logging.basicConfig(format='%(levelname)s:%(message)s', filename='artNet_controller.log', level=logging.DEBUG)
#log = logging.getLogger(__name__)


class Show():
    def __init__(self, showName, show):
        self.showName = showName
        self.show = show
