"""
This script simulates the sensor suite of the autonomous vehicle. It collects information from the environment and converts it into readable data that can be used by perception and decision-making systems.

Handled by - Adway
"""

from Utils.config import *

class Sensor:

    def __init__(self, world):

        self.world = world

    def calculate_distance(self, x1, y1, x2, y2):

        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    
    def detect_objects(self):

        detections = []

        car_x = self.world.car_x + (self.world.car_width // 2)
        car_y = self.world.car_y + (self.world.car_height // 2)

        for obstacle in self.world.obstacles:

            obstacle_x = (obstacle["x"] + (obstacle["width"] // 2))
            obstacle_y = (obstacle["y"] + (obstacle["height"] // 2))

            distance = self.calculate_distance(car_x, car_y, obstacle_x, obstacle_y)

            if distance <= SENSOR_RANGE:

                detections.append({"type": obstacle["type"], "distance": round(distance, 2), "x": obstacle["x"], "y": obstacle["y"]})

        return detections

    def get_nearest_object(self):
        detections = self.detect_objects()
        if len(detections) == 0:
            return None

        nearest_object = detections[0]
        for detection in detections:
            if (detection["distance"] < nearest_object["distance"]):
                nearest_object = detection

        return nearest_object
    
    def get_nearest_vehicle(self):
        detections = self.detect_objects()
        vehicles = []
        for detection in detections:
            if detection["type"] == "vehicle":
                vehicles.append(detection)

        if len(vehicles) == 0:
            return None

        nearest_vehicle = vehicles[0]
        for vehicle in vehicles:
            if vehicle["distance"] < nearest_vehicle["distance"]:
                nearest_vehicle = vehicle

        return nearest_vehicle
    
    def get_nearest_pedestrian(self):
        detections = self.detect_objects()
        pedestrians = []
        for detection in detections:
            if detection["type"] == "pedestrian":
                pedestrians.append(detection)

        if len(pedestrians) == 0:
            return None

        nearest_pedestrian = pedestrians[0]
        for pedestrian in pedestrians:
            if pedestrian["distance"] < nearest_pedestrian["distance"]:
                nearest_pedestrian = pedestrian

        return nearest_pedestrian
    
    def get_nearest_obstacle(self):
        detections = self.detect_objects()
        obstacles = []
        for detection in detections:
            if detection["type"] == "object":
                obstacles.append(detection)

        if len(obstacles) == 0:
            return None

        nearest_obstacle = obstacles[0]
        for obstacle in obstacles:
            if obstacle["distance"] < nearest_obstacle["distance"]:
                nearest_obstacle = obstacle

        return nearest_obstacle
    
    def get_detected_objects(self):

        return self.detect_objects()