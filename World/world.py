""" 
This script manages the simulation world of the autonomous vehicle platform. It is responsible for creating and maintaining the environment where all subsystems operate. The world initializes the simulator window, controls the main game loop, handles eventsupdates world states, and renders all objects such as roads, vehicles, obstacles, and future environment elements.

Handled by - Adway
"""

import pygame
from Utils.config import *


class World:

    def __init__(self):

        self.running = True

        pygame.init()

        self.screen = pygame.display.set_mode(
            (
                WINDOW_WIDTH,
                WINDOW_HEIGHT
            )
        )

        pygame.display.set_caption(
            "AutoStack AV Simulator"
        )

        self.clock = pygame.time.Clock()

    def run(self):

        while self.running:

            self.process_events()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

    def process_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False

    def draw(self):

        self.screen.fill(GRASS_COLOR)
        road_x = (WINDOW_WIDTH - ROAD_WIDTH)//2
        pygame.draw.rect(self.screen, ROAD_COLOR, (road_x, 0, ROAD_WIDTH, WINDOW_HEIGHT))
        pygame.display.flip()