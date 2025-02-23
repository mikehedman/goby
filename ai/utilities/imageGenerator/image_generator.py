import os
import math
import random

from PIL import Image, ImageDraw
from os.path import abspath, dirname, join

import sys
ai_dir = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(ai_dir)
import shared

background_color = "LightCyan"
line_color = "DarkBlue"
line_width = 25

def line(output_path, bottom, top):
    image = Image.new("RGB", (shared.WIDTH, shared.HEIGHT), background_color)
    draw = ImageDraw.Draw(image)
    draw.line([(top, 0), (bottom, shared.HEIGHT)], width=line_width, fill=line_color)
    image.save(output_path)
    #add a merged version
    merged = make_merged(image)
    merged.save(output_path.replace(".png", "_merged.png"))

#draws a set of lines according to a pattern, moving the line each time by the "shift" argument
def lineSet(x_start, x_finish, top_offset, shift, classification):
    x = x_start
    while x <= x_finish:
        filename = "{}/{}/lane{}_{}_{}_{}_{}.png".format(shared.GENERATED_DIR, classification, x, x + top_offset, background_color, line_color, line_width)
        line(filename, x, x + top_offset)
        x += shift

#defines the different line set definitions
def draw_lines():
    lineSet(round(shared.WIDTH*.4), round(shared.WIDTH*.6),0, 10, "good") #straight
    lineSet(0, shared.WIDTH,10, 10, "good")
    lineSet(0, shared.WIDTH,5, 10, "good")

    lineSet(round(shared.WIDTH/2), shared.WIDTH-30,50, 10, "left")
    lineSet(30, round(shared.WIDTH/2), -50, 10, "right")

    lineSet(round(shared.WIDTH/2), shared.WIDTH-30,60, 10, "left")
    lineSet(30, round(shared.WIDTH/2), -60, 10, "right")

def cross(output_path, bottom, angle, gap):
    cross_width = line_width * 5
    image = Image.new("RGB", (shared.WIDTH, shared.HEIGHT), background_color)
    draw = ImageDraw.Draw(image)
    draw.line([(bottom, gap), (bottom, shared.HEIGHT)], width=line_width, fill=line_color)
    cross = ImageDraw.Draw(image)
    cross.line([(bottom - round(cross_width/2), gap+math.floor(line_width/2)), (bottom + (cross_width/2), gap+math.floor(line_width/2))], width=line_width, fill=line_color)

    #pick the center of rotation so that the bottom doesn't get chopped off
    rotation_center = bottom + round(line_width/2) if angle > 0 else bottom - round(line_width/2)

    rotated_image = image.rotate(angle, center=(rotation_center, shared.HEIGHT), fillcolor=background_color)
    rotated_image.save(output_path)
    #add a merged version
    merged = make_merged(rotated_image)
    merged.save(output_path.replace(".png", "_merged.png"))

#draws a set of crosses according to a pattern, moving the cross each time by the "shift" argument
def crossSet(x_start, x_finish, shift, angle, gap):
    x = x_start
    while x <= x_finish:
        random_gap = random.randrange(gap)
        filename = "{}/wall/lane{}_{}_{}_{}_{}_{}.png".format(shared.GENERATED_DIR, x, angle, random_gap, background_color, line_color, line_width)
        cross(filename, x, angle, random_gap)
        x += shift

    #flip the angle and do another set
    if angle == 0:
        return
    angle = -angle
    x = x_start
    while x <= x_finish:
        random_gap = random.randrange(gap)
        filename = "{}/wall/lane{}_{}_{}_{}_{}_{}.png".format(shared.GENERATED_DIR, x, angle, random_gap, background_color, line_color, line_width)
        cross(filename, x, angle, random_gap)
        x += shift

def draw_crosses():
    max_gap = shared.HEIGHT - 2*line_width
    crossSet(round(shared.WIDTH*.3), round(shared.WIDTH*.7),10, 0, max_gap) #straight
    crossSet(round(shared.WIDTH*.3), round(shared.WIDTH*.7),10, 2, max_gap)
    crossSet(round(shared.WIDTH*.3), round(shared.WIDTH*.7),10, 4, max_gap)
    crossSet(round(shared.WIDTH*.3), round(shared.WIDTH*.7),10, 6, max_gap)

def make_merged(image):
  water_file = Image.open(random.choice(files))
  return Image.blend(water_file, image, 0.5)


if __name__ == "__main__":

    shared.setup_dirs(shared.GENERATED_DIR)

    pool_masks_dir = "pool_masks"
    files = os.listdir(pool_masks_dir)
    # append pool_masks_dir to each file name
    files = [join(pool_masks_dir, file) for file in files]

    #draw the default set
    draw_lines()
    draw_crosses()
    #
    #draw another set with different color and size
    line_color = "RoyalBlue"
    line_width = 35
    draw_lines()
    draw_crosses()




