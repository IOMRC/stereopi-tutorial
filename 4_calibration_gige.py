# Copyright (C) 2019 Eugene Pomazov, <stereopi.com>, virt2real team
#
# This file is part of StereoPi tutorial scripts.
#
# StereoPi tutorial is free software: you can redistribute it 
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
#
# StereoPi tutorial is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with StereoPi tutorial.  
# If not, see <http://www.gnu.org/licenses/>.
#
# Most of this code is updated version of 3dberry.org project by virt2real
# 
# Thanks to Adrian and http://pyimagesearch.com, as there are lot of
# code in this tutorial was taken from his lessons.
# 
#%%
import os
import cv2
import numpy as np
import json
from stereovision.calibration import StereoCalibrator
from stereovision.calibration import StereoCalibration
from stereovision.exceptions import ChessboardNotFoundError

#%%

# Global variables preset
total_photos = 1
photo_width = 1626 #only used for splitting stereopi images
photo_height = 1236 #only used for splitting stereopi images
img_width = 1626
img_height = 1236
image_size = (img_width,img_height)

# Chessboard parameters
rows = 19 # this is the number of dots in a row
columns = 15 # the number of dots in a column
square_size = 2.5 # this is the physical distance between dot centres (easiest to measure from edge to edge)
target_type = 'circle'

# Paramters to be adjusted for the blob detector - see https://www.learnopencv.com/blob-detection-using-opencv-python-c/ 
if target_type == 'circle':
  # Setup SimpleBlobDetector parameters.
  params = cv2.SimpleBlobDetector_Params()

  # Change thresholds
  params.minThreshold = 10
  params.maxThreshold = 200

  # Filter by Area.
  params.filterByArea = True
  params.minArea = 500
  params.maxArea = 1000

  # Filter by Circularity
  params.filterByCircularity = True
  params.minCircularity = 0.8

  # Filter by Convexity
  params.filterByConvexity = True
  params.minConvexity = 0.87

  # Filter by Inertia
  params.filterByInertia = True
  params.minInertiaRatio = 0.7

  #Blob detector parameters 
  detector = cv2.SimpleBlobDetector_create(params)

#%%
calibrator = StereoCalibrator(rows, columns, square_size, image_size)
photo_counter = 0
print ('Start cycle')

while photo_counter != total_photos:
  photo_counter = photo_counter + 1
  print ('Import pair No ' + str(photo_counter))
  leftName = './gige_pairs/left_'+str(photo_counter).zfill(2)+'.bmp'
  rightName = './gige_pairs/right_'+str(photo_counter).zfill(2)+'.bmp'
  if os.path.isfile(leftName) and os.path.isfile(rightName):
      imgLeft = cv2.imread(leftName,1)
      imgRight = cv2.imread(rightName,1)
      try:
        if target_type == 'circle':
          calibrator.add_corners((imgLeft, imgRight), show_results=False, target='circle',blobDetector=detector)
        elif target_type == 'chess':
          calibrator.add_corners((imgLeft, imgRight), show_results=False)
      except ChessboardNotFoundError as error:
        print (error)
        print ("Pair No "+ str(photo_counter) + " ignored")
        
        
print ('End cycle')
#%%

import pprint

print ('Starting calibration... It can take several minutes!')
calibration = calibrator.calibrate_cameras()
for key, item in calibration.__dict__.items():
  print('calibration.' + key + ":")
  pprint.pprint(item)
calibration.export('calib_result')
print ('Calibration complete!')

error=calibrator.check_calibration(calibration)
print('Reprojection error was %e pixels' % error)


#%%
# Lets rectify and show last pair after  calibration
calibration = StereoCalibration(input_folder='calib_result')
rectified_pair = calibration.rectify((imgLeft, imgRight))

cv2.imshow('Left CALIBRATED', rectified_pair[0])
cv2.imshow('Right CALIBRATED', rectified_pair[1])
cv2.imwrite("rectifyed_left.jpg",rectified_pair[0])
cv2.imwrite("rectifyed_right.jpg",rectified_pair[1])
cv2.waitKey(0)
