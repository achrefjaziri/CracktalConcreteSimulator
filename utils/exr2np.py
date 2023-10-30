import OpenEXR
import numpy as np
import Imath

import sys
def exr2numpy(filepath):
	# Get FLOAT type
	pt = Imath.PixelType(Imath.PixelType.FLOAT)
	exrImg = OpenEXR.InputFile(filepath)
	dw = exrImg.header()['dataWindow']
	size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
	# Convert image
	redstr = exrImg.channel('R', pt)
	# Read image to numpy
	img_np = np.fromstring(redstr, dtype = np.float32)
	return img_np

if(__name__ == "__main__"):
	res = exr2numpy(sys.argv[1])
	print(np.unique(res))