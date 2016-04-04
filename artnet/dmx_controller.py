# From gitHub : philchristensen/python-artnet
# https://github.com/philchristensen/python-artnet
import time, sys, socket, logging, threading, itertools
import dmx_frame
import dmx_deamon

log = logging.getLogger(__name__)

class Controller(dmx_deamon.Poller):
	def __init__(self, address, nodaemon=False, runout=False, fps=40.0, bpm=240.0, measure=4):
		super(Controller, self).__init__(address, nodaemon=nodaemon, runout=runout)

		self.fps = fps
		self.bpm = bpm
		self.measure = measure
		self.fpb = (fps * 60) / bpm
		self.last_frame = dmx_frame.Frame()
		self.generators = []
		self.access_lock = threading.Lock()
		self.runout = runout
		self.frameindex = 0
		self.beatindex = 0
		self.beat = 0
		self.autocycle = dmx_frame.AutoCycler(self)
	
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
				last = self.last_frame
			)
		return _clock
	
	def stop(self):
		try:
			self.access_lock.acquire()
			if(self.running):
				self.running = False
		finally:
			self.access_lock.release()
	
	def add(self, generator):
		try:
			self.access_lock.acquire()
			if(self.autocycle.enabled):
				self.generators.append(itertools.cycle(generator))
			else:
				self.generators.append(generator)
		finally:
			self.access_lock.release()
	
	def iterate(self):
		f = self.last_frame
		for g in self.generators:
			try:
				n = g.next()
				f = f.merge(n) if f else n
			except StopIteration:
				self.generators.remove(g)
		
		self.frameindex = self.frameindex + 1 if self.frameindex < self.fps - 1 else 0
		self.beatindex = self.beatindex + 1 if self.beatindex < self.fpb - 1 else 0
		if self.beatindex < self.fpb - 1:
			self.beatindex += 1
		else:
			self.beatindex = 0
			self.beat = self.beat + 1 if self.beat < self.measure - 1 else 0
		
		self.last_frame = f
	
	def run(self):
		now = time.time()
		while(self.running):
			drift = now - time.time()
			
			# do anything potentially framerate-affecting here
			self.iterate()
			self.handle_artnet()
			
			self.send_dmx(self.last_frame)
			if(self.runout and len(self.generators) == 0):
				self.running = False
			# end framerate-affecting code
			
			elapsed = time.time() - now
			excess = (1 / self.fps) - elapsed
			if(excess > 0):
				time.sleep(excess - drift if self.running else 0)
			else:
				log.warning("Frame rate loss; generators took %sms too long" % round(abs(excess * 1000)))
			now = time.time()
