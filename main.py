# Credits : ketanv3

# Imports
import numpy as np
import cv2


# Get the image statistics
# returns the mean and standard deviations of each channel
# The input image is in the Lab color space
def image_stats(image):
    (l, a, b) = cv2.split(image)
    (l_m, l_s) = (l.mean(), l.std())
    (a_m, a_s) = (a.mean(), a.std())
    (b_m, b_s) = (b.mean(), b.std())
    return l_m, l_s, a_m, a_s, b_m, b_s


# Color transfer function from source onto destination
def color_transfer(source, destination):
    # Convert the images form the RGB to the L*a*b* color space
    # also converts the pixel values to float 32
    source = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype("float32")
    destination = cv2.cvtColor(destination, cv2.COLOR_BGR2LAB).astype("float32")

    # compute the image statistics
    (s_l_m, s_l_s, s_a_m, s_a_s, s_b_m, s_b_s) = image_stats(source)
    (d_l_m, d_l_s, d_a_m, d_a_s, d_b_m, d_b_s) = image_stats(destination)

    # Subtract the mean from the destination image
    (l, a, b) = cv2.split(destination)
    l -= d_l_m
    a -= d_a_m
    b -= d_b_m

    # Scale by the standard deviations
    l = (d_l_s / s_l_s) * l
    a = (d_a_s / s_a_s) * a
    b = (d_b_s / s_b_s) * b

    # Add in the source mean
    l += s_l_m
    a += s_a_m
    b += s_b_m

    # Clip the pixel intensities to [0,255]
    l = np.clip(l, 0, 255)
    a = np.clip(a, 0, 255)
    b = np.clip(b, 0, 255)

    # Merge the channels together and convert them back to the RGB color space
    # Also use 8-bit uint for the pixel values
    transfer = cv2.merge([l, a, b])
    transfer = cv2.cvtColor(transfer.astype("uint8"), cv2.COLOR_LAB2BGR)

    # Return the color transferred image
    return transfer


# Display an image and resize it to a constant width
def show_image(title, image, width=300):
    r = width / float(image.shape[1])
    dim = (width, int(image.shape[0] * r))
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    cv2.imshow(title, resized)


# Image file names
source = "source.jpg"
destination = "destination.jpg"
output = "output.jpg"

# Read the images
source = cv2.imread(source)
destination = cv2.imread(destination)

# Transfer the colors from source onto destination
transferred = color_transfer(source, destination)

# Write the image to the output file if not None
if output is not None:
    cv2.imwrite(output, transferred)

# Show the images
show_image("Source", source)
show_image("Destination", destination)
show_image("Transferred", transferred)
cv2.waitKey(0)