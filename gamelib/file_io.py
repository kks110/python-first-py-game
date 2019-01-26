import fileinput
import os
import pygame
from pygame.locals import *


# If the scores file doesnt exist, it creates it.
# Then appent the score to the file
def save_score(score):
    if not os.path.exists('data'):
        os.mkdir('data')
    if not os.path.isfile('data/top.scores'):
        f = open('data/top.scores', 'w')
        f.close()
    score = str(score)
    score = score + '\n'
    f = open('data/top.scores', 'a')
    f.write(score)
    f.close()

# Reads each line and saves to a list
# Turns them back to ints to sorts them correctly
# Returns the top 5 and changes back to string to be displayed
def load_scores():
    top_scores = []
    scores = [line.rstrip('\n') for line in open('data/top.scores')]
    scores = [int(x) for x in scores]
    scores.sort(reverse = True)
    top_scores = scores[:5]
    top_scores = [str(x) for x in top_scores]
    return top_scores

# Used to load the sprite sheets
class Spritesheet(object):
    # confirms file is readable, throws error is not
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error:
            print ('Unable to load spritesheet image:' + filename)
            raise SystemExit

    # Retuns a single image from the sprite sheet
    def image_at(self, rectangle, colorkey = None):
        # Loads image from x,y,x+offset,y+offset
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates"
        return [self.image_at(rect, colorkey) for rect in rects]

    # Gets the first rect size, then multiplays that accross, then uses the other functions to get the other images
    def load_strip(self, rect, image_count, colorkey = None):
        tups = [(rect[0] + rect[2] * x, rect[1], rect[2], rect[3]) for x in range(image_count)]
        return self.images_at(tups, colorkey)