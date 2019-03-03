# pyspectro
Easy to use capture and data preparation functions for OceanOptics spectrometers as accessed with @python-seabreeze.

## Requirements
`numpy`, `matplotlib` and `datetime`, which should all be installed if you used anaconda.

Functioning installation of @python-seabreeze. Ensure that the following throws no errors:
```
import seabreeze
seabreeze.use("pyseabreeze")
import seabreeze.spectrometers as sb
```

## Usage
Clone this repository, and copy all contents into a folder called "pyspectro" in your working folder where your python code lives. At the top of your script, add 
```
from pyspectro import tools
```

You can then use the following, with tools.<function name>:

load sample data provided
```
spectrum_demo()
dark_demo()
standard_demo()
```

### spectrum smoothing
```
gaussian(y,p)
boxcar(y,p)
```
inputs

- y     array of intensities
- p     parameter, standard deviation for gauss and number of pixels to each side for boxcar

returns

- smoothed ys

### capture spectrum
```
capture(n = 1, int_secs = 0.5, smoother = None, p = 1, sub = [], div = [])
```

Parameters

- n          number of frames to average, default 1 frame
- int_secs   integration time (in seconds) per frame
- smoother   either 'boxcar', 'gaussian', or None. Default = None
- p          parameter for smoother, i.e. number of boxcar frames to each side, or tau if gaussian. Default = 1
- sub        frame as array length same as y to be taken off captured frame (as dark)
- div        frame to divide by (as calibration)
!! Note that this frame must have been captured at same integration time and number of frame averages !!

Returns

- result    array of spectrum values


### easy save to file
```
saveit(y, 'name_no_extention')
```

### easy demo plot 

takes in dark-subbed y and standard and shows three graphs: raw y, y/standard, smoothed y/standard
```
plot_demo(y, standard, smoother = 'boxcar', p = 10)
```
## Uninstall
Delete the pyspectro folder
