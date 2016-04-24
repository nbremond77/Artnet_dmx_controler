# From gitHub : philchristensen/python-artnet
# https://github.com/philchristensen/python-artnet
import time, sys, socket, logging, threading, itertools

from artnet import dmx_frame
from artnet import dmx_deamon

from artnet import shared
#logging.basicConfig(format='%(levelname)s:%(message)s', filename='artNet_controller.log', level=logging.DEBUG)
#log = logging.getLogger(__name__)

class Controller(dmx_deamon.Poller):
    def __init__(self, address, nodaemon=False, runout=False, fps=10.0, bpm=60.0, measure=4,  timeout=0,  universe=0):
        super(Controller, self).__init__(address, nodaemon=nodaemon, runout=runout)

        self.universe = universe
        self.fps = fps
        self.bpm = bpm
        self.measure = measure
        self.fpb = (fps * 60) / bpm
        self.timeout = timeout
        self.currentTimeForBlackout = time.time() + timeout
        self.last_frame = dmx_frame.Frame()
        self.generators = []
#        self.generatorsActivationTime = []
        self.access_lock = threading.Lock()
        self.runout = runout
        self.frameindex = 0
        self.beatindex = 0
        self.beat = 0
        self.autocycle = dmx_frame.AutoCycler(self)
        self.startTime = time.time()
    
    def get_clock(self):
        def _clock():
            return dict(
                beat = self.beat,
                measure = self.measure,
                frameindex = self.frameindex,
                fps = self.fps,
                beatindex = self.beatindex,
                fpb = self.fpb,
                running = self.running,
                last = self.last_frame,
                startTime = self.startTime
            )
        return _clock
    
    def stop(self):
        try:
            self.access_lock.acquire()
            if(self.running):
                self.running = False
                shared.log.debug("Stop...")
        finally:
            self.access_lock.release()
    
    def add(self, generator):
        self.currentTimeForBlackout = time.time() + self.timeout
        try:
            self.access_lock.acquire()
            if(self.autocycle.enabled):
                self.generators.append(itertools.cycle(generator))
                shared.log.debug("*** Add autocyclic generator: %s" % generator)
            else:
                self.generators.append(generator)
                shared.log.debug("*** Add generator: %s" % generator)
        finally:
            self.access_lock.release()
    

    def removeAll(self):
        self.access_lock.acquire()
        self.generators = []
        self.access_lock.release()

    def blackOut(self):
        self.access_lock.acquire()
        self.generators = []
        self.last_frame = dmx_frame.Frame([0] * 512)
        self.access_lock.release()
        self.currentTimeForBlackout = time.time() + self.timeout


    def iterate(self):
        f = self.last_frame
        for g in self.generators:
            #print(g)
            try:
                n = g.__next__()
                f = f.merge(n) if f else n
                
            except StopIteration:
                self.generators.remove(g)
                shared.log.debug("***Controller remove generator: %s" % g)

            shared.log.debug("Controller iterate generators with frame: %s" % f[0:30])
        
        self.frameindex = self.frameindex + 1 if self.frameindex < self.fps - 1 else 0
        self.beatindex = self.beatindex + 1 if self.beatindex < self.fpb - 1 else 0
        if self.beatindex < self.fpb - 1:
            self.beatindex += 1
        else:
            self.beatindex = 0
            self.beat = self.beat + 1 if self.beat < self.measure - 1 else 0
        
        self.last_frame = f
    
    def run(self):
        self.running = True
        now = time.time()
        self.startTime = now
        shared.log.debug("Start run...")
        while(self.running):
            drift = now - time.time()
            
            # do anything potentially framerate-affecting here
            if (time.time() > self.currentTimeForBlackout) and (self.timeout > 0.1):
                self.blackOut()
                
            self.iterate()
#            self.handle_artnet()

            shared.log.debug("Controller run - send_dmx with frame: %s" % self.last_frame[0:30])

            self.send_dmx(self.last_frame,  universe=self.universe)
            
            if(self.runout and len(self.generators) == 0):
                self.running = False
            # end framerate-affecting code
            
            elapsed = time.time() - now
            excess = (1 / self.fps) - elapsed
            if(excess > 0):
                time.sleep(excess - drift if self.running else 0)
            else:
                shared.log.warning("Frame rate loss; generators took %sms too long" % round(abs(excess * 1000)))
            now = time.time()
            shared.log.debug("Run...")

