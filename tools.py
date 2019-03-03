# standards
import numpy as np
import matplotlib.pyplot as plt
import datetime

#### to communicate with spectrometer #####
import seabreeze
seabreeze.use("pyseabreeze")
import seabreeze.spectrometers as sb

devices = sb.list_devices()
print('Spectrometer connected:', devices)
spec = sb.Spectrometer(devices[0])
###########################################




#get wavelengths. Note: first intensity is zero -> alway ignore
def wavelengths():
    return spec.wavelengths()[1:]
    #or... return np.loadtxt('spectro/wavelengths.txt')

# demo data, all at single frame 0.5 sec int time
def spectrum_demo():
    return np.loadtxt('spectro/flour.txt')
def dark_demo():
    return np.loadtxt('spectro/dark_5_1.txt')
def standard_demo():
    return np.loadtxt('spectro/standard_5_1.txt')




### functions #############################



### Smoothing

# Define function that returns the gaussian smoothed data
# IN:  y     array of intensities
#      tau   parameter for gauss
# OUT: smoothed ys

def gaussian(y,tau):
    
    x = wavelengths()

    # define gaussian memory function
    def gauss_point(x,tau): 
        return np.exp(-(1/2)*(x/tau)**2)

    #subfunction that finds weighted avg at each point
    def weighted_avg(x0,y,tau):
        
        weight = gauss_point(x0-x,tau)
        # multiply each point by its weight and sum and divide to get avg at that point
        weighted_avg_point = np.sum(y*weight)/np.sum(weight)
        return weighted_avg_point

    return [weighted_avg(xi,y,tau) for xi in x]

# Define function that returns boxcar smoothed (i.e. nearby pixel averaged) data
# IN:  y     array of intensities
#      p     number of pixels to each side
# OUT: smoothed ys

def boxcar(y,p):
    n = len(y)
    y_new = []
    for i in range(0,n):
        lo = i - p
        hi = i + p
        # edges
        if lo < 0:
            lo = 0
        if hi > n:
            hi = n
        # pick out window and its length
        window = y[lo:hi+1]
        w_len = len(window)
        y_new.append(sum(window)/w_len)
    return y_new



### capture function

# IN: n         number of frames to average, default 1 frame
#    int_secs   integration time per frame
#    smoother   either 'boxcar', 'gaussian', or None. Default = None
#    p          parameter for smoother, i.e. number of boxcar frames to each side, or tau if gaussian. Default = 1
#    dark     frame as array length same as y to be taken off captured frame
# !! (Note that this frame must have been captured at same integration time and number of frame averages) !!

def capture(n = 1, int_secs = 0.5, smoother = None, p = 1, sub = [], div = []):
    
    # set integration time
    spec.integration_time_micros(int_secs*10**6)
    
    #check smoother input is correct
    smoother_types = ['gaussian','boxcar',None]
    if smoother not in smoother_types:
        raise ValueError("Invalid smoother type. Expected one of: %s" % smoother_types)
    
    # capture multiple and average frames if needed
    if n > 1:
        frames = []
        for i in range(n):
            frame_i = spec.intensities()[1:]
            frames.append(frame_i)

        intensities = np.transpose(frames)
        result = np.array([sum(y)/n for y in intensities])
    else:
        result = np.array(spec.intensities()[1:])
    
    # "interpolation" due to bad pixel.
    result[1268] = (result[1267] + result[1267])/2
    
    # subtract dark frame if supplied, before smoothing
    if len(sub) > 0:
        result = result - sub

    if len(div) > 0:
        temp = div - sub # when passing in non-dark subtracted standards
        result = np.divide(result, temp, out=np.zeros_like(result), where=temp!=0) # if dividing by zero, keeps numerator as answer
    
    # apply smoother if needed
    if smoother == None:
        return result
    
    elif smoother == 'gaussian':
        return gaussian(result, p)
    
    elif smoother == 'boxcar':
        return boxcar(result,p)



### Define function to save data

def saveit(data = [], name = False):
    if name == False:
        name = currentDT = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    np.savetxt('spec_data/'+name+'.txt',data)



### Define plotter function that shows data captured
# plots raw data against standard given, then standard divided, then smoothed
# !!! assumes data inputted is already dark-subbed.

def plot_demo(y, standard, smoother = 'boxcar', p = 10):

    x = wavelengths()

    fig = plt.figure(figsize=(20,5))
    ax1, ax2, ax3 = fig.subplots(1,3)

    y0 = y
    ax1.plot(x, y0)
    ax1.plot(x, standard)
    ax1.set_title('Originals')
    ax1.set_xlabel('Wavelength (nm)')
    ax1.set_ylabel('Counts')
    
    y1 = np.divide(y0, standard, out=np.zeros_like(y0), where=standard!=0)
    ax2.plot(x, y1)
    ax2.set_title('Standard divided')
    ax2.set_xlabel('Wavelength (nm)')
    ax2.set_ylabel('Counts')

    if smoother == 'gaussian':
        y2 = gaussian(y1, p)
    elif smoother == 'boxcar':
        y2 = boxcar(y1,p)
    ax3.plot(x, y2)
    ax3.set_title('Smoothed')
    ax3.set_xlabel('Wavelength (nm)')
    ax3.set_ylabel('Counts')

    #plt.savefig('capture_smoothing.png')
    plt.show()
