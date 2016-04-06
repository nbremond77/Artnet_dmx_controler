# From gitHub : philchristensen/python-artnet
# https://github.com/philchristensen/python-artnet



import os.path
import yaml
import logging
import pkg_resources as pkg

#from artnet import fixtures
#from artnet import dmx
#import dmx_NBRLib

from artnet import dmx_fixture
from artnet import dmx_cue
from artnet import dmx_chase
from artnet import dmx_show

logging.basicConfig(format='%(levelname)s:%(message)s', filename='artNet_controller.log', level=logging.DEBUG)
log = logging.getLogger(__name__)


class Rig():
    def __init__(self, name="Not loaded"):
        self.name = name
        self.groups = {}
        self.fixtures = {}
        self.cues = {}
        self.chases = {}
        self.shows = {}
        self.rig_data = {}
        

    def get_default_rig(self):
        self.load(self,  os.path.expanduser("~/.artnet-rig.yaml"))

    def load(self,  config_path):
        # Load rig configuration file
        with open(config_path, 'r') as f:
            self.rig_data = yaml.safe_load(f)
            
        log.debug(self.rig_data)
        
        # Rig global parameters
        self.name = self.rig_data['name']
        
        # decode Fixtures
        for name, theFixture in self.rig_data['fixtures'].items():
            log.debug("Fixture: %s" % name)
            log.debug(theFixture)
            self.fixtures[name] = dmx_fixture.Fixture.create(theFixture['address'], theFixture['config'])

        # Decode groups
        for name, group in self.rig_data['groups'].items():
            log.debug("Group: %s" % name)
            log.debug(group)
            self.groups[name] = dmx_fixture.FixtureGroup([
                self.fixtures[g] for g in group
            ])
    
        # decode Cues
        for name, cue in self.rig_data['cues'].items():
            log.debug("Cue: %s" % name)
            log.debug(cue)
        
        # decode Chases
        for name, chase in self.rig_data['chases'].items():
            log.debug("Chase: %s" % name)
            log.debug(chase)
        
        # decode Shows
        for name, show in self.rig_data['shows'].items():
            log.debug("Show: %s" % name)
            log.debug(show)

    def printRig(self):
        print("*** RIG %s ***" % self.name)

        print("Fixtures:")
        for fixture in self.fixtures:
            print("  - %s" % fixture )

        print("Groups:")
        for group in self.groups:
            print("  - %s" % group)

        print("Cues:")
        for cue in self.cues:
            print("  %s" % cue)

        print("Chases:")
        for chase in self.chases:
            print("  %s" % chase)

        print("Shows:")
        for show in self.shows:
            print("  - %s" % show)
        
        print("*** end RIG %s ***" % self.name)
