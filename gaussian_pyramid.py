from PIL import Image
import numpy as np
import math
import scipy

def MakeGaussianPyramid(image, scale, minsize):
  # initialize the empty pyramid to return
  result_pyramid = []

  # save the pointer to the currrent image 
  curr_image = image

  # get the dimensions of the current image 
  x, y = curr_image.size

  # until the dimensions of the current, scaled version of image
  # are not smaller than the minsize in either x or y, 
  # continue building the pyramid
  while(x > minsize and y > minsize):

    # if the image is RGB, then proceed with splitting the color channels
    if (image.mode == "RGB"):
      # split the current image into the color channels for RGB support
      red_channel, green_channel, blue_channel = curr_image.split()

      # convert every color channel into a numpy array
      red_array = np.asarray(red_channel)
      green_array = np.asarray(green_channel)
      blue_array = np.asarray(blue_channel)

      # before we scale the image down, we want to apply the gaussian filter to it,
      # to avoid aliasing issues

      # apply the gaussian blur with a sigma of 1/(2*scale) to every color channel separately
      red_array = scipy.ndimage.gaussian_filter(red_array, 1 / (2 * scale))
      green_array = scipy.ndimage.gaussian_filter(green_array, 1 / (2 * scale))
      blue_array = scipy.ndimage.gaussian_filter(blue_array, 1 / (2 * scale))

      # convert every color channel back into unsigned intgers 
      red_array = red_array.astype("uint8")
      green_array = green_array.astype("uint8")
      blue_array = blue_array.astype("uint8")

      # convert the numpy color arrays back into the PIL images
      red_image = Image.fromarray(red_array)
      green_image = Image.fromarray(green_array)
      blue_image = Image.fromarray(blue_array)

      # finally, combine the three color channels together back into the same image
      curr_image = Image.merge("RGB", (red_image, green_image, blue_image))
    
    # if the image is greyscale, proceed with a single channel version
    elif (image.mode == "L"):
      
      # represent the current image as a numpy array
      curr_image_array = np.asarray(curr_image)

      # apply the gaussian blur with a sigma of 1/(2*scale)
      curr_image_array = scipy.ndimage.gaussian_filter(curr_image_array, 1 / (2 * scale))

      # convert the image array back into unsigned intgers 
      curr_image_array = curr_image_array.astype("uint8")

      # convert the image array back into the PIL image
      curr_image = Image.fromarray(curr_image_array)

    # add the current scaled version of the image to the pyramid
    result_pyramid.append(curr_image)

    # scale the image down, and save the dimensions of the new image 
    next_image_x = math.floor(x * scale)
    next_image_y = math.floor(y * scale)

    # finally, create a new image by using bicubic interpolation,
    # using the saved dimensions from above 
    curr_image = curr_image.resize((next_image_x, next_image_y), Image.BICUBIC)

    # NOTE: this step is important as here we will be updating the x, y values for the currrent image,
    # these values will be checked on the next while loop iteration, checking if either is above minsize
    x, y = curr_image.size

  return result_pyramid