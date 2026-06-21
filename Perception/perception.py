"""
This script manages the perception subsystem of the autonomous vehicle. It takes raw camera frames
and sensor detections, processes them using OpenCV for lane line detection (Canny + HoughLinesP),
computes dynamic lane centers, and tracks obstacle proximity relative to the lanes.

Handled by - Vedant (Week 4 Implementation)
"""

import cv2
import numpy as np
import pygame
from Utils.config import *

class Perception:
    def __init__(self, world):
        self.world = world
        self.road_left_boundary = (WINDOW_WIDTH - ROAD_WIDTH) // 2
        self.road_right_boundary = self.road_left_boundary + ROAD_WIDTH
        self.road_center = WINDOW_WIDTH // 2

    def process(self, camera_surface, target_lane="left"):
        """
        Processes the pygame camera surface to detect lane lines.
        Returns:
            edges_surface (pygame.Surface): Pygame surface with Canny edges and Hough lines drawn.
            target_x (int): Target x coordinate for lane center.
            obstacle_info (dict): Info about the nearest obstacle in the target lane.
        """
        # 1. Convert pygame surface to OpenCV image (BGR)
        surf_array = pygame.surfarray.array3d(camera_surface)
        rgb_array = np.transpose(surf_array, (1, 0, 2))
        img_bgr = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
        h, w, _ = img_bgr.shape

        # 2. Image Processing
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)

        # 3. Line Detection (HoughLinesP)
        # We search for lines in the cropped camera region
        lines = cv2.HoughLinesP(
            edges, 
            rho=1, 
            theta=np.pi/180, 
            threshold=30, 
            minLineLength=25, 
            maxLineGap=15
        )

        # Output canvas: convert edges to BGR so we can draw colored lines on it
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        detected_left = []
        detected_center = []
        detected_right = []

        # Get absolute x-offset of the camera crop on the screen
        car_center_x = self.world.car_x + self.world.car_width // 2
        crop_x = int(car_center_x - w // 2)
        crop_x = max(0, min(crop_x, WINDOW_WIDTH - w))

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Calculate angle to filter out non-vertical lines (slopes)
                dx = x2 - x1
                dy = y2 - y1
                if dy == 0:
                    continue
                angle = abs(np.arctan2(dy, dx) * 180 / np.pi)
                # Keep lines that are mostly vertical (70 to 110 degrees)
                if 70 <= angle <= 110:
                    # Draw detected line on the output image (in Green)
                    cv2.line(edges_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Convert crop x coordinates to absolute screen x coordinates
                    x_mid_abs = crop_x + (x1 + x2) / 2
                    
                    # Classify line by absolute screen position
                    if abs(x_mid_abs - self.road_left_boundary) < 30:
                        detected_left.append(x_mid_abs)
                    elif abs(x_mid_abs - self.road_center) < 30:
                        detected_center.append(x_mid_abs)
                    elif abs(x_mid_abs - self.road_right_boundary) < 30:
                        detected_right.append(x_mid_abs)

        # 4. Compute target lane center based on detected lines or ideal configuration
        ideal_left_lane_center = self.road_left_boundary + ROAD_WIDTH // 4
        ideal_right_lane_center = self.road_left_boundary + (3 * ROAD_WIDTH // 4)
        
        target_x = ideal_left_lane_center if target_lane == "left" else ideal_right_lane_center

        # Refine target_x dynamically based on detected lines
        if target_lane == "left":
            left_x = np.mean(detected_left) if detected_left else self.road_left_boundary
            center_x = np.mean(detected_center) if detected_center else self.road_center
            target_x = int((left_x + center_x) / 2)
        else:
            center_x = np.mean(detected_center) if detected_center else self.road_center
            right_x = np.mean(detected_right) if detected_right else self.road_right_boundary
            target_x = int((center_x + right_x) / 2)

        # 5. Convert processed OpenCV edge image back to Pygame Surface
        rgb_edges = cv2.cvtColor(edges_bgr, cv2.COLOR_BGR2RGB)
        rgb_edges_transposed = np.transpose(rgb_edges, (1, 0, 2))
        edges_surface = pygame.surfarray.make_surface(rgb_edges_transposed)

        # 6. Extract nearest obstacle info in the target lane
        obstacle_info = self.get_obstacle_in_lane(target_lane)

        return edges_surface, target_x, obstacle_info

    def get_obstacle_in_lane(self, lane):
        """
        Identifies the closest obstacle (car, pedestrian, static object) in the target lane.
        """
        detections = self.world.sensor.detect_objects()
        nearest_obstacle = None
        min_dist = float('inf')

        # Left lane is x in [road_left, road_center]
        # Right lane is x in [road_center, road_right]
        for det in detections:
            obstacle_x_center = det["x"]
            # Classify obstacle lane
            obs_lane = "left" if obstacle_x_center < self.road_center else "right"

            if obs_lane == lane:
                # Find the distance along the vertical axis (y) for precise control
                # Obstacle y-position relative to car
                dy = self.world.car_y - det["y"]
                # Only consider obstacles that are in front of us
                if dy > 0:
                    if dy < min_dist:
                        min_dist = dy
                        nearest_obstacle = {
                            "type": det["type"],
                            "distance": dy,
                            "x": det["x"],
                            "y": det["y"]
                        }

        return nearest_obstacle
