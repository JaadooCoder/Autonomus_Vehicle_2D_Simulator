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
        road_x = (WINDOW_WIDTH - ROAD_WIDTH) // 2
        self.left_lane_center = road_x + (ROAD_WIDTH // 4)
        self.right_lane_center = road_x + (3 * ROAD_WIDTH // 4)
        self.road_offset = 0
        self.car_width = CAR_WIDTH
        self.car_height = CAR_HEIGHT
        self.car_x = self.left_lane_center - (self.car_width // 2)
        self.car_y = WINDOW_HEIGHT - 120
        self.speed = 0
        self.max_speed = MAX_SPEED
        self.acceleration = ACCELERATION
        self.brake_force = BRAKE_FORCE
        self.obstacles = []
        self.obstacles.append(self.create_obstacle(OBSTACLE_WIDTH // 2, 250, 2))
        self.obstacles.append(self.create_obstacle(OBSTACLE_WIDTH // 2, -200, 3))
        self.obstacles.append( self.create_obstacle(OBSTACLE_WIDTH // 2, -500, 4))
        

    def run(self):

        while self.running:

            self.process_events()
            self.update()
            pygame.display.set_caption(f"AutoStack AV Simulator | Speed: {self.speed:.1f}")
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

    def process_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False

    def draw(self):

        if self.crashed:
            self.screen.fill((255, 0, 0))
            pygame.display.flip()
            return
        self.screen.fill(GRASS_COLOR)
        road_x = (WINDOW_WIDTH - ROAD_WIDTH)//2
        pygame.draw.rect(self.screen, ROAD_COLOR, (road_x, 0, ROAD_WIDTH, WINDOW_HEIGHT))
        for y in range(-60, WINDOW_HEIGHT + 60, 60):
            draw_y = y + self.road_offset
            pygame.draw.line(self.screen, LANE_COLOR, (WINDOW_WIDTH // 2, draw_y), (WINDOW_WIDTH // 2, draw_y + 30), 5)
        pygame.draw.rect(self.screen, CAR_COLOR, (self.car_x, self.car_y, self.car_width, self.car_height))
        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, VEHICLE_COLOR, (obstacle["x"], obstacle["y"], obstacle["width"], obstacle["height"]))

        pygame.display.flip()

    def update(self):

        if self.crashed:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.speed += self.acceleration
        if keys[pygame.K_s]:
            self.speed -= self.brake_force
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < 0:
            self.speed = 0
        self.speed *= FRICTION
        if self.speed < 0.05:
            self.speed = 0
        if keys[pygame.K_a]:
            self.car_x -= CAR_SPEED
        if keys[pygame.K_d]:
            self.car_x += CAR_SPEED

        road_left = (WINDOW_WIDTH - ROAD_WIDTH) // 2
        road_right = (road_left + ROAD_WIDTH) - self.car_width

        if self.car_x < road_left:
            self.car_x = road_left
        if self.car_x > road_right:
            self.car_x = road_right
        self.road_offset += self.speed
        if self.road_offset >= 60:
            self.road_offset -= 60
        
        self.update_obstacles()
        self.check_collisions()
    

    def update_obstacles(self):

        for obstacle in self.obstacles:

            obstacle["y"] += (obstacle["speed"] + self.speed)
            if obstacle["y"] > WINDOW_HEIGHT:
                obstacle["y"] = random.randint(-500, -50)
                obstacle["x"] = random.choice([self.left_lane_center - 20, self.right_lane_center - 20])
                obstacle["speed"] = random.randint(NPC_MIN_SPEED, NPC_MAX_SPEED)

    def check_collisions(self):

        car_rect = pygame.Rect(self.car_x, self.car_y, self.car_width, self.car_height)
        for obstacle in self.obstacles:

            obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], obstacle["width"], obstacle["height"])

            if car_rect.colliderect(obstacle_rect):
                self.crashed = True

    def create_obstacle(self, x, y, speed):
        return {"x": x, "y": y, "width": OBSTACLE_WIDTH, "height": OBSTACLE_HEIGHT, "speed": speed}