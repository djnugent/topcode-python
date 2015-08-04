'''
 * @(#) Scanner.py
 * 
 * Tangible Object Placement Codes (TopCodes)
 * Copyright (c) 2007 Michael S. Horn
 * 
 *		   Michael S. Horn (michael.horn@tufts.edu)
 *		   Tufts University Computer Science
 *		   161 College Ave.
 *		   Medford, MA 02155
 * 
 * This program is free software you can redistribute it and/or modify
 * it under the terms of the GNU General def License (version 2) as
 * published by the Free Software Foundation.
 * 
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General def License for more details.
 * 
 * You should have received a copy of the GNU General def License
 * along with this program if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
'''

import math
import cv2
import numpy as np
from TopCode import TopCode

'''
 * Loads and scans images for TopCodes.  The algorithm does a single
 * sweep of an image (scanning one horizontal line at a time) looking
 * for a TopCode bullseye patterns.  If the pattern matches and the
 * black and white regions meet certain ratio constraints, then the
 * pixel is tested as the center of a candidate TopCode.
 *
 * @author Michael Horn, Port by Daniel Nugent
 * @version $Revision: 1.4 $, $Date: 2015/07/30 15:02:13 $
'''

class Scanner(object):

	
   
	'''
	* Default constructor
	'''
	def __init__(self):
		''' Total width of image '''
	  	self.w  = 0

	  	''' Total height of image '''
	  	self.h = 0

	  	''' The original image '''
	  	self.image = None

	  	''' Holds processed binary pixel data '''
	  	self.data = None

	  	''' Binary view of the image '''
	  	self.preview = None

	  	''' Candidate code count '''
	  	self.ccount = 0

	  	''' Number of candidates tested '''
	  	self.tcount = 0

	  	''' Maximum width of a TopCode unit in pixels '''
	  	self.maxu = 80
	  	self.q = 0


	'''
	Scan the given image or file(not both) and return a list of all topcodes found in it.
	'''
	def scan(self, image = None, filename = None):
		if(image is None and filename is None):
			raise TypeError("Please provide filename or image")
		if(image is not None and filename is not None):
			raise TypeError("Please provide only one argument, not both")

		if image is None:
			self.image = cv2.imread(filename,1)
			if self.image is None:
				raise IOError("Image not found")
		else:
			self.image = image


		self.preview = None
		self.w = self.image.shape[1]
		self.h = self.image.shape[0]
		self.data = self.getRGB(self.image)

		self.threshold()		  # run the adaptive threshold filter
		return self.findCodes()   # scan for topcodes

	'''
	Convert an opencv image to a linear array
	'''
	def getRGB(self, image):
		data = np.zeros([self.w*self.h], dtype=np.int32)
		for y in range(0, self.h):
			for x in range(0,self.w):
				b,g,r = image[y][x]
				pixel = (0xFF << 24) | ((r & 0xFF) << 16) | ((g & 0xFF) << 8) | (b & 0xFF)
				#pixel = ((r & 0xFF) << 16) | ((g & 0xFF) << 8) | (b & 0xFF)
				data[y * self.w + x] = pixel
		return data


	'''
	Returns the original (unaltered) image   
	'''
  	def getImage(self):
	 	return self.image

	'''
	Returns the width in pixels of the current image (or zero if no image is
	loaded).
	'''
  	def getImageWidth(self):
		return self.w


	'''
	Returns the width in pixels of the current image (or zero if no image is
	loaded).
	'''
  	def getImageHeight(self):
	 	return self.h
   

	'''
	Sets the maximum allowable diameter (in pixels) for a TopCode
	identified by the scanner.  Setting this to a reasonable value for
	your application will reduce False positives (recognizing codes that
	aren't actually there) and improve performance (because fewer
	candidate codes will be tested).  Setting this value to as low as 50
	or 60 pixels could be advisable for some applications.  However,
	setting the maximum diameter too low will prevent valid codes from
	being recognized.  The default value is 640 pixels.
	'''
  	def setMaxCodeDiameter(self, diameter):
	 	f = diameter / 8.0
	 	self.maxu = int(math.ceil(f))

   
	'''
	Returns the number of candidate topcodes found during a scan
	'''
  	def getCandidateCount(self):
		return self.ccount


	'''
	Returns the number of topcodes tested during a scan
	'''
  	def getTestedCount(self):
		return self.tcount


	'''
	Binary (thresholded black/white) value for pixel (x,y)   
	'''
  	def getBW(self, x, y):
	 	pixel = self.data[y * self.w + x]
	 	return (pixel >> 24) & 0x01

   
	'''
	Average of thresholded pixels in a 3x3 region around (x,y).
	Returned value is between 0 (black) and 255 (white).   
	'''
  	def getSample3x3(self, x, y):
	 	if (x < 1 or x > (self.w-2) or y < 1 or y >= (self.h-2)):
	 		return 0
	 	pixel, sum = 0, 0
	 	
	 	for j in range(y-1,y+2):
	 		for i in range(x-1,x+2):
				pixel = self.data[j * self.w + i]
				if ((pixel & 0x01000000) > 0):
				   sum += 0xff
	  	#return (sum >= 5) ? 1 : 0
	  	return int(sum / 9)

   
	'''
	Average of thresholded pixels in a 3x3 region around (x,y).
	Returned value is either 0 (black) or 1 (white).
	'''
  	def getBW3x3(self, x, y): 
	 	if (x < 1 or x > (self.w-2) or y < 1 or y >= (self.h-2)):
	 		return 0
	 	pixel, sum = 0, 0
	  
	 	for j in range(y-1,y+2,1):
	 		for i in range(x-1,x+2):
				pixel = self.data[j * self.w + i]
				sum += ((pixel >> 24) & 0x01)

		return 1 if (sum >= 5) else 0

   
   
	'''
	Perform Wellner adaptive thresholding to produce binary pixel
	data.  Also mark candidate spotcode locations.
 
	"Adaptive Thresholding for the DigitalDesk"   
	EuroPARC Technical Report EPC-93-110
	'''
 	def threshold(self):
 		q = 0
	 	pixel, r, g, b, a = 0, 0, 0, 0, 0
	 	threshold, sum = 128, 128
	 	s = 30
	 	k = 0
	 	b1, w1, b2, level, dk = 0, 0, 0, 0, 0

	 	self.ccount = 0
	 	for j in range(0, self.h):
			level = b1 = b2 = w1 = 0

			#----------------------------------------
			# Process rows back and forth (alternating
			# left-to-right, right-to-left)
			#----------------------------------------
			k = 0 if (j % 2 == 0) else (self.w-1)
			k += (j * self.w)
		 
			for i in range(0,self.w):
			 
				#----------------------------------------
				# Calculate pixel intensity (0-255)
				#----------------------------------------
				pixel = self.data[k]
				r = (pixel >> 16) & 0xff
				g = (pixel >> 8) & 0xff
				b = pixel & 0xff
				a = (r + g + b) / 3
				#a = r
				
				#----------------------------------------
				# Calculate sum as an approximate sum
				# of the last s pixels
				#----------------------------------------
				sum += a - (sum / s)
			 
				#----------------------------------------
				# Factor in sum from the previous row
				#----------------------------------------
				if (k >= self.w):
				   threshold = (sum + (self.data[k-self.w] & 0xffffff)) / (2*s)
				else:
				   threshold = sum / s
				
				

				#----------------------------------------
				# Compare the average sum to current pixel
				# to decide black or white
				#----------------------------------------
				f = 0.85
				f = 0.975
				a = 0 if (a < threshold * f) else 1

				

				#----------------------------------------
				# Repack pixel data with binary data in 
				# the alpha channel, and the running sum
				# for this pixel in the RGB channels
				#----------------------------------------
				self.data[k] = (a << 24) + (sum & 0xffffff)
				   
				# On a white region. No black pixels yet
				if level == 0:
				  	if (a == 0):  # First black encountered
					 	level = 1
					 	b1 = 1
					 	w1 = 0
					 	b2 = 0
	  
				# On first black region
				elif level == 1:
				  	if (a == 0):
					 	b1 += 1
				  	else:
					 	level = 2
					 	w1 = 1
				  
				   

				# On second white region (bulls-eye of a code?)
				elif level == 2:
				  	if (a == 0):
					 	level = 3
					 	b2 = 1
				  	else:
					 	w1 += 1
				  
				   
				   
				# On second black region
				elif level == 3:
				  	if (a == 0):
					 	b2 += 1
				  	# This could be a top code
				  	else:
					 	mask = 0
					 	# less than 2 pixels... not interested
					 	if (b1 >= 2 and b2 >= 2 and b1 <= self.maxu and b2 <= self.maxu and w1 <= (self.maxu + self.maxu) and math.fabs(b1 + b2 - w1) <= (b1 + b2) and math.fabs(b1 + b2 - w1) <= w1 and math.fabs(b1 - b2) <= b1 and math.fabs(b1 - b2) <= b2):
							mask = 0x2000000

							dk = 1 + b2 + w1/2
							if (j % 2 == 0):
								dk = k - dk 
							else:
								dk = k + dk
						 
							self.data[dk - 1] |= mask
							self.data[dk] |= mask
							self.data[dk + 1] |= mask
							self.ccount += 3  # count candidate codes
					  
					 	b1 = b2
					 	w1 = 1
					 	b2 = 0
					 	level = 2

				k += 1 if (j % 2 == 0) else -1
	  
   

	'''
	Scan the image line by line looking for TopCodes   
	'''
  	def findCodes(self):
	 	self.tcount = 0
	  	spots = []

	 	spot = TopCode()
	 	k = self.w * 2
	 	for j in range(2, self.h-2):
	 		for i in range(0,self.w):
				if ((self.data[k] & 0x2000000) > 0):
					if ((self.data[k-1] & 0x2000000) > 0 and (self.data[k+1] & 0x2000000) > 0 and (self.data[k-self.w] & 0x2000000) > 0 and (self.data[k+self.w] & 0x2000000) > 0):
						'''
				  		if ((self.data[k-self.w] & 0x2000000) > 0 or
					  	(self.data[k+self.w] & 0x2000000) > 0)):
						'''	

						if (not self.overlaps(spots, i, j)):
							self.tcount += 1
							spot.decode(self, i, j)
							if (spot.isValid()):
								spots.append(spot)
								spot = TopCode()

				k += 1
		return spots


	'''
	Returns True if point (x,y) is in an existing TopCode bullseye   
	'''
  	def overlaps(self, spots, x, y):
		for top in spots:
			if (top.inBullsEye(x, y)):
				return True
	 	return False
   
   
	'''
	Counts the number of vertical pixels from (x,y) until a color
	change is perceived. 
	'''
  	def ydist(self, x, y, d):
	 	sample = 0
	 	start  = self.getBW3x3(x, y)
	 	j = y + d
	 	while(j > 1 and j < self.h -1):
			sample = self.getBW3x3(x, j)
			if (start + sample == 1):
				return (j-y) if (d > 0) else (y - j)
			j+=d
		return -1
	 	

   
	'''
	Counts the number of horizontal pixels from (x,y) until a color
	change is perceived. 
	'''
  	def xdist(self, x, y, d):
	 	sample = 0
	 	start = self.getBW3x3(x, y)
	  
	 	i = x + d
	 	while(i > 1 and i < self.w -1):
			sample = self.getBW3x3(i, y)
			if (start + sample == 1): 
				return (i -x) if (d > 0) else (x - i)
			i+=d
	  	return -1

   
	#   def markTest(int x, int y): 
	#	  Graphics2D g = (Graphics2D)getImage().getGraphics()
	#	  g.setColor(Color.red)
	#	  g.fillRect(x - 1, y - 1, 3, 3)

   
	'''
	For debugging purposes, create a black and white image that
	shows the result of adaptive thresholding.
	'''
	def getPreview(self):
	 	self.preview = np.zeros((self.h,self.w,3),np.uint8)

	 	k = 0
	 	for j in range(0, self.h):
	 		for i in range(0,self.w):
	 			pixel = (self.data[k]>> 24)
	 			k+=1
				if (pixel == 0):
					pixel = 0xFF000000
				elif (pixel == 1):
					pixel = 0xFFFFFFFF
				elif (pixel == 3):
					pixel = 0xFF00FF00
				elif (pixel == 7):
					pixel = 0xFFFF0000

				a = (pixel >> 24) & 0xFF
				r = (pixel >> 16) & 0xFF
				g = pixel >> 8 & 0xFF
				b = pixel & 0xFF


				self.preview[j][i] =  (b,g,r)

	 	return self.preview

