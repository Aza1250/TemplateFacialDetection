from PIL import Image, ImageDraw
import numpy as np
import ncc

def FaceDetect(pyramid, template, threshold, scale):

  # the array of where filtered and cleaned coordinates are stored
  # used to draw the squares
  matches = []

  # define a maximum width for the template.
  # this is necessary since a large template,
  # will be very computationally expensive
  template_width = 15

  # convert the 0th element or the original image from the pyramid into RGB,
  # if needed
  imageRGB = pyramid[0].convert('RGB')

  # dimensions of the template
  x_t, y_t = template.size

  # ratio between the width and the height of the template
  # necessary to keep the template's aspect ratio after the scale down
  # to template_width
  ratio = x_t // template_width
  # it's important to make sure everything stays as an int,
  # so I floor within this function
  template = template.resize((template_width, y_t // ratio), Image.BICUBIC)
  
  for image in pyramid:
    # calculate the coordinates (x, y) in the original image,
    #  of where the dot product/correlation values are above the set threshold
    filtered_coordinates = np.where(ncc.normxcorr2D(image, template) > threshold)

    # save the x and y coordinates of the filtered points separately
    filtered_coordinates_x = filtered_coordinates[0]
    filtered_coordinates_y = filtered_coordinates[1]

    # the zip function allows for the removal of duplicate values,
    # it also combines the separate x and y coordinates into the
    # cleaned and filtered tuple of x and y coordinates;
    # ready to be used for drawing the squares

    # Every match with the template at each level of the Gaussian pyramid is saved to the 
    # matches array, where they turn into x, y coordinates
    matches.append(zip(filtered_coordinates_y, filtered_coordinates_x))
	

	# get the number of total matches (squares to be drawn)
  number_of_matches = len(matches)
  
  for i in range(number_of_matches):
    # we need to keep track of which image we are on in the pyramid,
    # the smaller (further in the matches array) we get,
    # the larger the multiplier needs to be to have the same scale as the original image
    multiplier = scale ** i
    multiplier_x2 = 2 * multiplier
  
    for match_position in matches[i]:
      # building the rectangle around the appropriate point.
      x1 = (match_position[0] // multiplier) - (x_t // multiplier_x2)
      y1 = (match_position[1] // multiplier) - (y_t // multiplier_x2)
      x2 = (match_position[0] // multiplier) + (x_t // multiplier_x2)
      y2 = (match_position[1] // multiplier) + (y_t // multiplier_x2)

      # shortcut for the PIL Image Draw function
      draw = ImageDraw.Draw(imageRGB)
      draw.rectangle((x1, y1, x2, y2), outline=(0, 0, 255))
      del draw
    
  return imageRGB

  # In short, here are steps to my template matching function:
  # 1. Calculate dot product similarity for every pyramid image
  # 2. Find every position for which the threshold has been exceeded
  # 3. For each pyramid level, combine all those matching positions into a zip object,
  #    to store in the list of zip objects
  # 4. Iterate over the zip objects and add squares at appropriate scales 
          