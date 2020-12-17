# Proj002-ColorTransfert

Raphaël TOURNAFOND & Ambroise DECOUTTERE - CMI info

## Description

Color transfer is an image processing application where you want 
to retarget the color histogram of an input image according to the 
color histogram of a target one.


## Work done

This program is able to transfer the colors of the source image onto 
the destination image.

The *opt_transport_v1* function simply takes the color of the closest projected 
pixel on the directionnal vector.

The *opt_transport_v2* function is more complex.
This function uses the directional vector to get the new color of each pixel by 
applying a part of this vector to the pixel to make it 
This function use the directionnal vector to get a new color more similar to the 
closest projected pixel but without using this pixel.