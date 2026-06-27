"""
Dashboard.py

This module is responsible for displaying all simulation
information on the right side of the screen.

Handled by - Dipansh
"""

import pygame
from Utils.config import *


class Dashboard:

    def __init__(self, world):

        self.world = world

        pygame.font.init()

        self.title_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.heading_font = pygame.font.SysFont("Arial", 17, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 15)
        self.small_font = pygame.font.SysFont("Arial", 13)

        self.background = (35, 35, 35)
        self.panel = (50, 50, 50)
        self.border = (110, 110, 110)

        self.white = (255, 255, 255)
        self.green = (0, 220, 0)
        self.red = (255, 70, 70)
        self.yellow = (255, 220, 0)
        self.blue = (0, 200, 255)

    ##########################################################

    def draw(self):

        self.draw_background()

        self.draw_header()

        self.draw_vehicle_panel()

        self.draw_sensor_panel()

        self.draw_ai_panel()

        self.draw_environment_panel()

        self.draw_footer()

    ##########################################################

    def draw_background(self):

        pygame.draw.rect(

            self.world.screen,

            self.background,

            (

                WORLD_WIDTH,

                0,

                DASHBOARD_WIDTH,

                WINDOW_HEIGHT

            )

        )

    ##########################################################

    def draw_panel(self, title, x, y, w, h):

        pygame.draw.rect(

            self.world.screen,

            self.panel,

            (x, y, w, h)

        )

        pygame.draw.rect(

            self.world.screen,

            self.border,

            (x, y, w, h),

            2

        )

        heading = self.heading_font.render(

            title,

            True,

            self.white

        )

        self.world.screen.blit(

            heading,

            (

                x + 10,

                y + 8

            )

        )

    ##########################################################

    def draw_header(self):

        title = self.title_font.render(

            "AUTOSTACK",

            True,

            self.white

        )

        subtitle = self.small_font.render(

            "Autonomous Vehicle Dashboard",

            True,

            self.blue

        )

        self.world.screen.blit(

            title,

            (

                WORLD_WIDTH + 20,

                15

            )

        )

        self.world.screen.blit(

            subtitle,

            (

                WORLD_WIDTH + 20,

                42

            )

        )

        pygame.draw.line(

            self.world.screen,

            self.border,

            (WORLD_WIDTH, 65),

            (WINDOW_WIDTH, 65),

            2

        )

    ##########################################################

    def draw_vehicle_panel(self):

        x = WORLD_WIDTH + 10

        y = 80

        w = DASHBOARD_WIDTH - 20

        h = 170

        self.draw_panel(

            "Vehicle Status",

            x,

            y,

            w,

            h

        )

        mode = "AUTONOMOUS" if self.world.autonomous else "MANUAL"

        info = [

            ("Mode", mode),

            ("Speed", f"{self.world.speed:.2f}"),

            ("Maximum", f"{self.world.max_speed:.2f}"),

            ("Acceleration", f"{self.world.acceleration:.2f}"),

            ("Brake", f"{self.world.brake_force:.2f}"),

            ("Position",

             f"({int(self.world.car_x)}, {int(self.world.car_y)})")

        ]

        row = y + 35

        for label, value in info:

            left = self.text_font.render(

                label,

                True,

                self.white

            )

            right = self.text_font.render(

                str(value),

                True,

                self.green

            )

            self.world.screen.blit(left, (x + 10, row))

            self.world.screen.blit(right, (x + 150, row))

            row += 22

        ##########################################################

    def draw_sensor_panel(self):

        x = WORLD_WIDTH + 10
        y = 265
        w = DASHBOARD_WIDTH - 20
        h = 165

        self.draw_panel(
            "Sensor Status",
            x,
            y,
            w,
            h
        )

        detected = len(self.world.sensor.get_detected_objects())

        sensors = [

            ("Camera", "ONLINE"),

            ("LiDAR", "ONLINE"),

            ("Radar", "ONLINE"),

            ("GPS", "ONLINE"),

            ("Ultrasonic", "ONLINE"),

            ("Objects", detected)

        ]

        row = y + 35

        for label, value in sensors:

            left = self.text_font.render(
                label,
                True,
                self.white
            )

            right = self.text_font.render(
                str(value),
                True,
                self.green
            )

            self.world.screen.blit(left, (x + 10, row))
            self.world.screen.blit(right, (x + 160, row))

            row += 22

    ##########################################################

    def draw_ai_panel(self):

        x = WORLD_WIDTH + 10
        y = 445
        w = DASHBOARD_WIDTH - 20
        h = 165

        self.draw_panel(
            "AI / Planning",
            x,
            y,
            w,
            h
        )

        state = self.world.planner_state

        lane = self.world.planner.target_lane

        autonomous = "ON" if self.world.autonomous else "OFF"

        planner_info = [

            ("Autonomous", autonomous),

            ("FSM State", state),

            ("Target Lane", lane),

            ("Target X", int(self.world.target_x))

        ]

        row = y + 35

        for label, value in planner_info:

            left = self.text_font.render(
                label,
                True,
                self.white
            )

            right = self.text_font.render(
                str(value),
                True,
                self.yellow
            )

            self.world.screen.blit(left, (x + 10, row))
            self.world.screen.blit(right, (x + 160, row))

            row += 24

    ##########################################################

    def draw_environment_panel(self):

        x = WORLD_WIDTH + 10
        y = 625
        w = DASHBOARD_WIDTH - 20
        h = 165

        self.draw_panel(
            "Environment",
            x,
            y,
            w,
            h
        )

        vehicles = 0
        pedestrians = 0
        objects = 0

        for obstacle in self.world.obstacles:

            if obstacle["type"] == "vehicle":
                vehicles += 1

            elif obstacle["type"] == "pedestrian":
                pedestrians += 1

            elif obstacle["type"] == "object":
                objects += 1

        collision = "YES" if self.world.crashed else "NO"

        data = [

            ("Vehicles", vehicles),

            ("Pedestrians", pedestrians),

            ("Objects", objects),

            ("Collision", collision)

        ]

        row = y + 35

        for label, value in data:

            colour = self.green

            if label == "Collision" and collision == "YES":
                colour = self.red

            left = self.text_font.render(
                label,
                True,
                self.white
            )

            right = self.text_font.render(
                str(value),
                True,
                colour
            )

            self.world.screen.blit(left, (x + 10, row))
            self.world.screen.blit(right, (x + 160, row))

            row += 24

    ##########################################################

    def draw_footer(self):

        pygame.draw.line(

            self.world.screen,

            self.border,

            (WORLD_WIDTH, WINDOW_HEIGHT - 40),

            (WINDOW_WIDTH, WINDOW_HEIGHT - 40),

            2

        )

        fps = int(self.world.clock.get_fps())

        fps_surface = self.small_font.render(

            f"FPS : {fps}",

            True,

            self.green

        )

        self.world.screen.blit(

            fps_surface,

            (

                WORLD_WIDTH + 15,

                WINDOW_HEIGHT - 30

            )

        )

        version = self.small_font.render(

            "AutoStack AV Simulator",

            True,

            self.white

        )

        self.world.screen.blit(

            version,

            (

                WORLD_WIDTH + 100,

                WINDOW_HEIGHT - 30

            )

        )

        mode = "AUTONOMOUS" if self.world.autonomous else "MANUAL"

        mode_colour = self.green if self.world.autonomous else self.yellow

        mode_surface = self.small_font.render(

            mode,

            True,

            mode_colour

        )

        self.world.screen.blit(

            mode_surface,

            (

                WINDOW_WIDTH - 120,

                WINDOW_HEIGHT - 30

            )

        )