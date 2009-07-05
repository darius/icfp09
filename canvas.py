import pygame
import sys

# Window dimensions
wscale   = 500
wwidth   = 2*wscale
wheight  = 2*wscale

screen   = None
dotcount = 0

class Canvas:

    red      = (255, 0, 0)
    green    = (0, 255, 0)
    blue     = (0, 0, 255)
    white    = (255, 255, 255)

    def __init__(self, scale):
        self.rescale = float(wscale) / scale
        global screen
        assert screen is None
        screen = pygame.display.set_mode((wwidth, wheight))

    def draw_dot(self, (x, y), color):
        x = int(self.rescale * x) + wscale
        y = int(self.rescale * y) + wscale
        assert 0 <= x < wwidth
        assert 0 <= y < wheight
        screen.set_at((x, y), color)
        global dotcount
        dotcount += 1
        if 100 <= dotcount:
            dotcount = 0
            pygame.display.flip()

    def draw_circle(self, (x, y), radius, color, width=1):
        x = int(self.rescale * x) + wscale
        y = int(self.rescale * y) + wscale
        radius = int(self.rescale * radius)
        assert 0 <= x < wwidth
        assert 0 <= y < wheight
        #assert 0 <= radius < 1.414213563 * wscale
        pygame.draw.circle(screen, color, (x, y), radius, width)

    def react(self):
        for event in pygame.event.get():
            self.react_to(event)

    def hold(self):
        while True:
            self.react_to(pygame.event.wait())

    def react_to(self, event):
        if event.type == pygame.QUIT:
            sys.exit(0)
        
