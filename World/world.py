""" 
This script manages the simulation world of the autonomous vehicle platform. It is responsible for creating and maintaining the environment where all subsystems operate. The world initializes the simulator window, controls the main game loop, handles eventsupdates world states, and renders all objects such as roads, vehicles, obstacles, and future environment elements.

Handled by - Adway
"""

import pygame
from Utils.config import *
import random

class World:

    def __init__(self):

        self.running = True
        self.crashed = False
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
        self.car_width = CAR_WIDTH
        self.car_height = CAR_HEIGHT
        road_x = (WINDOW_WIDTH - ROAD_WIDTH) // 2
        self.left_lane_center = road_x + (ROAD_WIDTH // 4)
        self.right_lane_center = road_x + (3 * ROAD_WIDTH // 4)
        self.car_x = self.left_lane_center - (self.car_width // 2)
        self.car_y = WINDOW_HEIGHT - 120
        self.obstacles = []
        self.obstacles.append(self.create_obstacle(self.left_lane_center - 20, 250, 2))
        self.obstacles.append(self.create_obstacle(self.right_lane_center - 20, -200, 3))
        self.obstacles.append( self.create_obstacle( self.left_lane_center - 20, -500, 4))

    def run(self):

        while self.running:

            self.process_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

    def process_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False

    def draw(self):

        self.screen.fill(GRASS_COLOR)
        if self.crashed:
            self.screen.fill((255, 0, 0))
            pygame.display.flip()
            return
        road_x = (WINDOW_WIDTH - ROAD_WIDTH)//2
        pygame.draw.rect(self.screen, ROAD_COLOR, (road_x, 0, ROAD_WIDTH, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, 60):

            pygame.draw.line(self.screen, LANE_COLOR, (WINDOW_WIDTH//2, y), (WINDOW_WIDTH//2, y+30), 5)
        pygame.draw.rect(self.screen, CAR_COLOR, (self.car_x, self.car_y, self.car_width, self.car_height))
        for obstacle in self.obstacles:

            pygame.draw.rect(self.screen, (0, 0, 255), (obstacle["x"], obstacle["y"], obstacle["width"], obstacle["height"]))

        pygame.display.flip()

    def update(self):

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.car_y -= CAR_SPEED
        if keys[pygame.K_DOWN]:
            self.car_y += CAR_SPEED
        if keys[pygame.K_LEFT]:
            self.car_x -= CAR_SPEED
        if keys[pygame.K_RIGHT]:
            self.car_x += CAR_SPEED

        road_left = (WINDOW_WIDTH - ROAD_WIDTH) // 2
        road_right = (road_left + ROAD_WIDTH) - self.car_width

        if self.car_x < road_left:
            self.car_x = road_left
        if self.car_x > road_right:
            self.car_x = road_right
        if self.car_y < 0:
            self.car_y = 0
        if self.car_y > WINDOW_HEIGHT - self.car_height:
            self.car_y = (WINDOW_HEIGHT - self.car_height)

        self.update_obstacles()
        self.check_collisions()

    def update_obstacles(self):

        for obstacle in self.obstacles:

            obstacle["y"] += obstacle["speed"]
            if obstacle["y"] > WINDOW_HEIGHT:
                obstacle["y"] = -50
                obstacle["x"] = random.choice([self.left_lane_center - 20, self.right_lane_center - 20])

    def check_collisions(self):

        car_rect = pygame.Rect(self.car_x, self.car_y, self.car_width, self.car_height)
        for obstacle in self.obstacles:

            obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], obstacle["width"], obstacle["height"])

            if car_rect.colliderect(obstacle_rect):
                self.crashed = True

    def create_obstacle(self, x, y, speed):
        return {"x": x, "y": y, "width": 40, "height": 40, "speed": speed}