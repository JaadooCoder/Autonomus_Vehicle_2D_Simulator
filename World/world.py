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

        pygame.quit()

    def process_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False