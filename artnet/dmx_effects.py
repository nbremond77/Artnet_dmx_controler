# From gitHub : philchristensen/python-artnet
# https://github.com/philchristensen/python-artnet
import time, logging

#from artnet import dmx
from artnet import dmx_frame

logging.basicConfig(format='%(levelname)s:%(message)s', filename='artNet_controller.log', level=logging.DEBUG)
log = logging.getLogger(__name__)

def create_cuelist(frames, frameDurations, frameTransitionTime, fps=40):
    result = []
    total_frames = len(frames)
    for index in range(total_frames):
        if(index < len(frames) - 1):
            fade = generate_fade(frames[index], frames[index+1], secs/(total_frames-1), fps)
            result.extend(list(fade))
    return iter(result)


def create_multiframe(frames, secs=5.0, fps=40):
    result = []
    total_frames = len(frames)
    for index in range(total_frames):
        if(index < len(frames) - 1):
            fade = generate_cut(frames[index], frames[index+1], secs/(total_frames-1), fps)
            result.extend(list(fade))
    return iter(result)

def generate_cut(start,  end, secs=5.0, fps=40):
    for index in range(int(secs * fps)):
#        f = dmx_frame.Frame()
#        f = end
        if index < int(secs * fps)/2:
            yield start
        else:
            yield end
        
def create_multifade(frames, secs=5.0, fps=40):
    result = []
    total_frames = len(frames)
    for index in range(total_frames):
        if(index < len(frames) - 1):
            fade = generate_fade(frames[index], frames[index+1], secs/(total_frames-1), fps)
            result.extend(list(fade))
    return iter(result)

def generate_fade(start, end, secs=5.0, fps=40):
    for index in range(int(secs * fps)):
        f = dmx_frame.Frame()
        if secs > 1/fps:
            for channel in range(len(start)):
                a = start[channel] or 0
                b = end[channel] or 0
                f[channel] = int(a + (((b - a) / (secs * fps)) * index))
        else:
            f = end
        yield f

def pulse_beat(clock, start, end, secs=5.0):
    t = time.time()
    c = clock()
    while(c['running']):
        if(c['beat'] % 2):
            yield start
        else:
            yield end
        if(time.time() - t >= secs):
            return
        c = clock()

def rotate(clock, group):
    t = time.time()
    c = clock()
    while(c['running']):
        if(c['beatindex'] == 0):
            colors = group.getColor()
            colors.append(colors.pop(0))
            for i in range(len(colors)):
                group[i].setColor(colors[i])
            
            intensities = group.getIntensity()
            intensities.append(intensities.pop(0))
            for i in range(len(intensities)):
                group[i].setIntensity(intensities[i])
            
            strobes = group.getStrobe()
            strobes.append(strobes.pop(0))
            for i in range(len(strobes)):
                group[i].setStrobe(strobes[i])
        
        yield group.getFrame()
        c = clock()


