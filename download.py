#!/usr/bin/python

# Prior art:
# https://gist.github.com/eskriett/6038468
# https://gist.github.com/sebastianleonte/617628973f88792cd097941220110233

import urllib.request
from PIL import Image
import os
import math

class GoogleMapsLayers:
  ROADMAP = "v"
  TERRAIN = "p"
  ALTERED_ROADMAP = "r"
  SATELLITE = "s"
  TERRAIN_ONLY = "t"
  HYBRID = "y"


def getTile(_lat,_lng,_zoom):
    """
        Generates an X,Y tile coordinate based on the latitude, longitude
        and zoom level
        Returns:    An X,Y tile coordinate
    """

    tile_size = 256

    # Use a left shift to get the power of 2
    # i.e. a zoom level of 2 will have 2^2 = 4 tiles
    numTiles = 1 << _zoom

    # Find the x_point given the longitude
    point_x = (tile_size / 2 + _lng * tile_size / 360.0) * numTiles // tile_size

    # Convert the latitude to radians and take the sine
    sin_y = math.sin(_lat * (math.pi / 180.0))

    # Calulate the y coorindate
    point_y = ((tile_size / 2) + 0.5 * math.log((1 + sin_y) / (1 - sin_y)) * -(
    tile_size / (2 * math.pi))) * numTiles // tile_size

    return int(point_x), int(point_y)


def generateImage(start_x, start_y, tile_width, tile_height, _zoom, _layer):
    """
        Generates an image by stitching a number of google map tiles together.
        Args:
            start_x:        The top-left x-tile coordinate
            start_y:        The top-left y-tile coordinate
            tile_width:     The number of tiles wide the image should be -
                            defaults to 5
            tile_height:    The number of tiles high the image should be -
                            defaults to 5
        Returns:
            A high-resolution Goole Map image.
    """


    # Determine the size of the image
    width, height = 256 * tile_width, 256 * tile_height

    # Create a new image of the size require
    map_img = Image.new('RGB', (width, height))

    for x in range(0, tile_width):
        for y in range(0, tile_height):
            url = f'https://mt0.google.com/vt?lyrs={_layer}&x=' + str(start_x + x) + '&y=' + str(start_y + y) + '&z=' + str(_zoom)

            current_tile = str(x) + '-' + str(y)
            urllib.request.urlretrieve(url, current_tile)

            im = Image.open(current_tile)
            map_img.paste(im, (x * 256, y * 256))

            os.remove(current_tile)

    return map_img

"""
    GoogleMapDownloader Constructor
    Args:
        lat:    The latitude of the location required
        lng:    The longitude of the location required
        zoom:   The zoom level of the location required, ranges from 0 - 23
                defaults to 12
"""



def download(lat,lng,name):
    gmd = GoogleMapDownloader(lat, lng, 20, GoogleMapsLayers.SATELLITE)

    print("The tile coorindates are {}".format(gmd.getXY()))

    try:
        # Get the high resolution image
        img = gmd.generateImage()
    except IOError as e:
        print(e)
        print("Could not generate the image - try adjusting the zoom level and checking your coordinates")
    else:
        # Save the image to disk
        img.save(name + ".png")
        print("The map has successfully been created")



def main():

    # lat lng corners NW and SE corners
    # NOTE: you'll want to use a VPN to hop around and aviod 403 errors from Google
    x0 = 38.540285
    x1 = 38.521378
    y0 = -120.615499
    y1 = -120.603025

    zoom = 20
    step = 10

    layer = GoogleMapsLayers.SATELLITE

    tx0, ty0 = getTile(x0, y0, zoom)
    tx1, ty1 = getTile(x1, y1, zoom)

    total = 0
    for start_y in range(ty0, ty1, step):
        for start_x in range(tx0, tx1, step):
            total += 1
    i = 0
    for start_y in range(ty0, ty1, step):
        for start_x in range(tx0, tx1, step):
            i += 1
            print("Downloading", start_x, start_y)
            print("Progress", i, "/", total)
            if i > 20:
                tile_width = step
                tile_height = step
                img = generateImage(start_x, start_y, tile_width, tile_height, zoom, layer)
                img.save(str(start_x) + "-" + str(start_y) + ".png")



if __name__ == '__main__':  main()