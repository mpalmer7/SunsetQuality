# Sunset Detector
import urllib.request
from PIL import Image
import numpy as np
import scipy.cluster
import os
from datetime import datetime
import time

print("****************************************")
print("****************************************")
print("Sunset quality evaluator by Mitch.")
print("Currently hardcoded for Washington D.C.")
print("****************************************")
print("****************************************")
print("Starting Script...")
print("Retrieving SunsetWX Model.")
filename = "ET_sunset.png"  # Todo hardcoded
url = "https://sunsetwx.com/sunset/sunset_et.png"  # Todo hardcoded
urllib.request.urlretrieve(url, filename)
print("Cropping image.")
img = Image.open(filename)
# Left/Top/Right/Bottom
# ToDo hardcoded for Washington D.C.
img2 = img.crop([950, 500, 1125, 580])  # Virginia
img2.save("sunset_va.png")
img3 = img.crop([1055, 500, 1100, 530])  # Washington D.C.
img3.save("sunset_dc.png")

# ToDo can be multi-threaded?
print("Image processing.")
rgb_list = []
for n in range(10):

	# print('Reading image.')
	im = Image.open('sunset_dc.png')
	im = im.resize((150, 150))      # optional, to reduce time
	ar = np.asarray(im)
	shape = ar.shape
	ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)

	# print('Finding clusters.')
	NUM_CLUSTERS = 5
	codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
	# print('cluster centres:\n', codes)
	vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
	counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences
	index_max = scipy.argmax(counts)                    # find most frequent
	peak = codes[index_max]
	colour = '#'+str(hex(int(peak[0])))[2:].upper()+str(hex(int(peak[1])))[2:].upper()+str(hex(int(peak[2])))[2:].upper()
	# print('most frequent color is %s (%s)' % (peak, colour))
	r, g, b = [str(i).split('.')[0] for i in peak]
	rgb_list.append([r, g, b])

# RBG values are a number.
# They do not linearily correspond to colors.
# I used an online table to attempt to associate the value with
# the closest reconizable color.
rgb_txt_color_name = {}
css_color_list_name = {}
print('Retrieving color names.')
for rgb in rgb_list:
	r, g, b = rgb
	url = "http://shallowsky.com/colormatch/index.php?r={}&g={}&b={}".format(r, g, b)
	urllib.request.urlretrieve(url, "color.html")
	f = open("color.html", "r")
	lns = f.readlines()
	f.close()
	temp = []
	for l in lns:
		if l.startswith("<td><span style"):
			temp.append(l)
	rtcn = temp[0].split("<td>")[2]
	ccln = temp[1].split("<td>")[2]
	if rtcn in rgb_txt_color_name:
		rgb_txt_color_name[rtcn] += 1
	else:
		rgb_txt_color_name[rtcn] = 1
	if ccln in css_color_list_name:
		css_color_list_name[ccln] += 1
	else:
		css_color_list_name[ccln] = 1

	time.sleep(.25) # don't want to spam...

print("Found colors: ", rgb_txt_color_name)
print("Found colors: ", css_color_list_name)
sorted_rtcn = sorted(rgb_txt_color_name, key=rgb_txt_color_name.get, reverse=True)[0]  # Get most common output
sorted_ccln = sorted(css_color_list_name, key=css_color_list_name.get, reverse=True)[0]  # Get most common output
# print(sorted_rtcn)
# print(sorted_ccln)


print("Cleaning.")
os.remove("color.html")
os.remove("sunset_dc.png")
try:
	os.rename("ET_sunset.png", "Archive/ET_sunset_{}.png".format(str(datetime.now()).split(" ")[0]))
except FileExistsError:
	pass
try:
	os.rename("sunset_va.png", "Archive/sunset_va_{}.png".format(str(datetime.now()).split(" ")[0]))
except FileExistsError:
	pass
os.remove("ET_sunset.png")
os.remove("sunset_va.png")


print("****************************************")
print("****************************************")
if "blue" in sorted_rtcn.lower() or "blue" in sorted_ccln.lower():
	print("You will experience a poor sunset.")
elif "green" in sorted_rtcn.lower() or "green" in sorted_ccln.lower():
	print("The sunset will be... okay.")
elif "yellow" in sorted_rtcn.lower() or "yellow" in sorted_ccln.lower():
	print("The sunset should decent.")
elif "orange" in sorted_rtcn.lower() or "orange" in sorted_ccln.lower():
	print("Watch the skies. Good sunset incoming.")
elif "red" in sorted_rtcn.lower() or "red" in sorted_ccln.lower():
	print("Fantastic sunset incoming!!!")
else:
	print("unable to classify sunset.")
	print("See values below to debug...")
	print("rgb.txt list:", str(rgb_txt_color_name))
	print("css color list:", str(css_color_list_name))
	print("RGB values: ", str(r+g+b))

# Connect this to Raspberry PI or Alexa, schedule to get sunset quality evaluation every morning.
