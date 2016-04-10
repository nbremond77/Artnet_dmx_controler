# From gitHub : philchristensen/python-artnet
# https://github.com/philchristensen/python-artnet
import time, logging

#from artnet import dmx
from artnet import dmx_frame

logging.basicConfig(format='%(levelname)s:%(message)s', filename='artNet_controller.log', level=logging.DEBUG)
log = logging.getLogger(__name__)

def create_cueListRun(clock, cues, cuesDurations = [], fps=20):
    result = []
    while len(frameDurations) < len(cues) :
        frameDurations.append(10.0) # 10 seconds is the default duration
    while len(frameTransitionTimes) < len(cues) :
        frameTransitionTimes.append(2.0) # 2 seconds is the default transition duration
        
    c = clock()
    
    for frameIndex in range(len(cues)):
        frame_startTime = time.time()
        frame_endTransitionTime = frame_startTime + frameTransitionTimes[frameIndex]
        frame_endTime = frame_startTime + frameDurations[frameIndex]

        while(c['running'] and (time.time() < frame_endTime)):
            if(time.time() < frame_endTransitionTime) and (frameIndex > 0):
                fade = generate_fade(frames[frameIndex-1], frames[frameIndex], frameTransitionTimes[frameIndex], fps)
                #result.extend(list(fade))
                #return iter(result)
#                yield fade
                result.extend(list(fade))
            else:
#                yield frames[frameIndex]
                result.extend(list(frames[frameIndex]))
            c = clock()
    return iter(result)



def create_frameListRun(clock, frames, frameDurations = [], frameTransitionTimes = [], fps=20):
    result = []
    while len(frameDurations) < len(frames) :
        frameDurations.append(10.0) # 10 seconds is the default duration
    while len(frameTransitionTimes) < len(frames) :
        frameTransitionTimes.append(2.0) # 2 seconds is the default transition duration
        
    c = clock()
    
    for frameIndex in range(len(frames)):
        frame_startTime = time.time()
        frame_endTransitionTime = frame_startTime + frameTransitionTimes[frameIndex]
        frame_endTime = frame_startTime + frameDurations[frameIndex]

        while(c['running'] and (time.time() < frame_endTime)):
            if(time.time() < frame_endTransitionTime) and (frameIndex > 0):
                fade = generate_fade(frames[frameIndex-1], frames[frameIndex], frameTransitionTimes[frameIndex], fps)
                #result.extend(list(fade))
                #return iter(result)
#                yield fade
                result.extend(list(fade))
            else:
#                yield frames[frameIndex]
                result.extend(list(frames[frameIndex]))
            c = clock()
    return iter(result)


def create_multiframe(frames, totalDuration=5.0, fps=20):
    result = []
    total_frames = len(frames)
    for index in range(total_frames):
        if(index < len(frames) - 1):
            fade = generate_cut(frames[index], frames[index+1], totalDuration/(total_frames-1), fps)
            result.extend(list(fade))
    return iter(result)

def generate_cut(start,  end, duration=5.0, fps=20):
    for index in range(int(duration * fps)):
#        f = dmx_frame.Frame()
#        f = end
        if index < int(duration * fps)/2:
            yield start
        else:
            yield end
        
def create_multifade(frames, totalDuration=5.0, fps=20):
    result = []
    total_frames = len(frames)
    for index in range(total_frames):
        if(index < len(frames) - 1):
            fade = generate_fade(frames[index], frames[index+1], totalDuration/(total_frames-1), fps)
            result.extend(list(fade))
    return iter(result)

def generate_fade(start, end, duration=5.0, fps=20):
    for index in range(int(duration * fps)):
        f = dmx_frame.Frame()
        if duration > 1/fps:
            for channel in range(len(start)):
                a = start[channel] or 0
                b = end[channel] or 0
                f[channel] = int(a + (((b - a) / (duration * fps)) * index))
        else:
            f = end
        yield f

def pulse_beat(clock, start, end, duration=5.0):
    t = time.time()
    c = clock()
    while(c['running']):
        if(c['beat'] % 2):
            yield start
        else:
            yield end
        if(time.time() - t >= duration):
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


