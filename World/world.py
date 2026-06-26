""" 
This script manages the simulation world of the autonomous vehicle platform. It is responsible for creating and maintaining the environment where all subsystems operate. The world initializes the simulator window, controls the main game loop, handles eventsupdates world states, and renders all objects such as roads, vehicles, obstacles, and future environment elements.

Handled by - Adway
"""

import pygame
from Utils.config import *
import random
from Sensors.sensors import Sensor
from Perception.perception import Perception
from Planning.planning import Planner
from Control.control import VehicleController
from Dashboard.dashboard import Dashboard


class World:

    def __init__(self):

        self.running = True
        self.crashed = False
        pygame.init()
        pygame.font.init()
        self.sensor = Sensor(self)
        self.perception = Perception(self)
        self.planner = Planner(self)
        self.controller = VehicleController(self)
        self.dashboard = Dashboard(self)
        
        self.autonomous = False
        self.edges_surface = None
        self.target_x = 0
        self.planner_state = "FOLLOW_LANE"
        self.font = pygame.font.SysFont("Arial", 20)


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
        self.obstacles.append(self.create_obstacle("vehicle", self.left_lane_center - (NPC_WIDTH // 2),-100, 3))
        self.obstacles.append(self.create_obstacle("pedestrian", (WINDOW_WIDTH - ROAD_WIDTH)//2, 250, 1))
        self.obstacles.append(self.create_obstacle("object", self.right_lane_center - (OBSTACLE_WIDTH // 2), -400, 0))

        

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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.autonomous = not self.autonomous
                    print(f"Switched control mode. Autonomous: {self.autonomous}")


    def draw(self):

        if self.crashed:
            self.screen.fill((255, 0, 0))
            crashed_text = self.font.render("COLLISION DETECTED! GAME OVER", True, (255, 255, 255))
            text_rect = crashed_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(crashed_text, text_rect)
            pygame.display.flip()
            return
        self.screen.fill(GRASS_COLOR)
        road_x = (WINDOW_WIDTH - ROAD_WIDTH)//2
        pygame.draw.rect(self.screen, ROAD_COLOR, (road_x, 0, ROAD_WIDTH, WINDOW_HEIGHT))
        for y in range(-60, WINDOW_HEIGHT + 60, 60):
            draw_y = y + self.road_offset
            pygame.draw.line(self.screen, LANE_COLOR, (WINDOW_WIDTH // 2, draw_y), (WINDOW_WIDTH // 2, draw_y + 30), 5)
        pygame.draw.rect(self.screen, CAR_COLOR, (self.car_x, self.car_y, self.car_width, self.car_height))
        pygame.draw.circle(self.screen, (0, 255, 255), (self.car_x + (self.car_width // 2), self.car_y + (self.car_height // 2)), SENSOR_RANGE, 1)
        detected_objects = self.sensor.get_detected_objects()
        for detection in detected_objects:
            pygame.draw.line(self.screen, (255, 255, 0), (self.car_x + (self.car_width // 2), self.car_y + (self.car_height // 2)), (detection["x"], detection["y"]), 2)
        for obstacle in self.obstacles:
            if obstacle["type"] == "pedestrian":
                color = PEDESTRIAN_COLOR
            elif obstacle["type"] == "vehicle":
                color = VEHICLE_COLOR
            else:
                color = OBJECT_COLOR
            pygame.draw.rect(self.screen, color, (obstacle["x"], obstacle["y"], obstacle["width"], obstacle["height"]))

        self.dashboard.draw()    
        pygame.display.flip()


    def update(self):

        if self.crashed:
            return
            
        if not self.autonomous:
            # Manual keyboard control
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.speed += self.acceleration
            if keys[pygame.K_s]:
                self.speed -= self.brake_force
            if keys[pygame.K_a]:
                self.car_x -= CAR_SPEED
            if keys[pygame.K_d]:
                self.car_x += CAR_SPEED
        else:
            # Autonomous control pipeline
            crop_surface = self.sensor.get_camera_crop()
            self.edges_surface, self.target_x, obstacle_info = self.perception.process(crop_surface, self.planner.target_lane)
            self.planner_state, target_lane, target_speed = self.planner.update(obstacle_info)
            self.controller.control(self.target_x, target_speed)

        # Apply physics and constraints
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < 0:
            self.speed = 0
        self.speed *= FRICTION
        if self.speed < 0.05:
            self.speed = 0

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
        self.sensor.detect_objects()
        self.check_collisions()

    

    def update_obstacles(self):

        current_time = pygame.time.get_ticks()
        for obstacle in self.obstacles:
            if (current_time - obstacle["decision_timer"]) > (BEHAVIOUR_CHANGE_TIME * 1000):
                obstacle["decision_timer"] = current_time
                if obstacle["type"] == "pedestrian":
                    obstacle["behavior"] = random.choice(["stand", "cross"])
                elif obstacle["type"] == "vehicle":
                    obstacle["behavior"] = random.choice(["stop", "forward", "turn_left", "turn_right"])
            world_scroll = self.speed
            if obstacle["type"] == "pedestrian":
                obstacle["y"] += world_scroll
                if obstacle["behavior"] == "cross":
                    obstacle["x"] += PEDESTRIAN_SPEED
                    if obstacle["x"] > ((WINDOW_WIDTH + ROAD_WIDTH) // 2):
                        obstacle["behavior"] = "respawn"
                if obstacle["behavior"] == "respawn":
                    obstacle["x"] = (WINDOW_WIDTH - ROAD_WIDTH) // 2
                    obstacle["y"] = random.randint(50, WINDOW_HEIGHT - 100)
                    obstacle["behavior"] = random.choice(["stand", "cross"])
                    obstacle["decision_timer"] = current_time
            elif obstacle["type"] == "vehicle":
                if obstacle["behavior"] == "forward":
                    obstacle["y"] += max(1, self.speed * 0.7)
                elif obstacle["behavior"] == "turn_left":
                    obstacle["y"] += max(1, self.speed * 0.7)
                    obstacle["x"] -= LANE_DRIFT_SPEED
                    if obstacle["x"] < (self.left_lane_center - (NPC_WIDTH // 2)):
                        obstacle["behavior"] = "forward"
                        obstacle["decision_timer"] = current_time
                elif obstacle["behavior"] == "turn_right":
                    obstacle["y"] += max(1, self.speed * 0.7)
                    obstacle["x"] += LANE_DRIFT_SPEED
                    if obstacle["x"] > (self.right_lane_center - (NPC_WIDTH // 2)):
                        obstacle["behavior"] = "forward"
                        obstacle["decision_timer"] = current_time
                elif obstacle["behavior"] == "stop":
                    pass
            elif obstacle["type"] == "object":
                obstacle["y"] += self.speed
            if obstacle["type"] == "vehicle":
                road_left = ((WINDOW_WIDTH - ROAD_WIDTH) // 2)
                road_right = (road_left + ROAD_WIDTH - obstacle["width"])
                if obstacle["x"] < road_left:
                    obstacle["x"] = road_left
                if obstacle["x"] > road_right:
                    obstacle["x"] = road_right
            if obstacle["y"] > WINDOW_HEIGHT:
                if obstacle["type"] == "vehicle":
                    obstacle["y"] = random.randint(-500, -50)
                    obstacle["x"] = random.choice([self.left_lane_center - (NPC_WIDTH // 2), self.right_lane_center - (NPC_WIDTH // 2)])
                    obstacle["speed"] = random.randint(NPC_MIN_SPEED, NPC_MAX_SPEED)
                    obstacle["behavior"] = "forward"
                    obstacle["decision_timer"] = current_time
                elif obstacle["type"] == "object":
                    obstacle["y"] = random.randint(-500, -50)
                    obstacle["x"] = random.choice([ self.left_lane_center - (OBSTACLE_WIDTH // 2), self.right_lane_center - (OBSTACLE_WIDTH // 2)])

                elif obstacle["type"] == "pedestrian":
                    obstacle["x"] = (WINDOW_WIDTH - ROAD_WIDTH) // 2
                    obstacle["y"] = random.randint(50, WINDOW_HEIGHT - 100)

    def check_collisions(self):

        car_rect = pygame.Rect(self.car_x, self.car_y, self.car_width, self.car_height)
        for obstacle in self.obstacles:

            obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], obstacle["width"], obstacle["height"])

            if car_rect.colliderect(obstacle_rect):
                self.crashed = True

    def create_obstacle(self, obstacle_type, x, y, speed):
       
        if obstacle_type == "pedestrian":
                width = PEDESTRIAN_WIDTH
                height = PEDESTRIAN_HEIGHT
                behavior = random.choice(["stand", "cross"])

        elif obstacle_type == "vehicle":
                width = NPC_WIDTH
                height = NPC_HEIGHT
                behavior = random.choice(["forward"])

        else:
                width = OBSTACLE_WIDTH
                height = OBSTACLE_HEIGHT
                behavior = "static"

        return {
                "type": obstacle_type,
                "behavior": behavior,
                "decision_timer": pygame.time.get_ticks(),
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "speed": speed
               }
        