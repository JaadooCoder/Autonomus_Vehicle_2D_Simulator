"""
This script manages the planning subsystem of the autonomous vehicle. It implements a Finite State Machine
(FSM) that controls the high-level behavior of the car. The states are:
- FOLLOW_LANE: Standard lane following at maximum speed.
- AVOID_OBSTACLE: Maneuver to change lanes to bypass an obstacle.
- STOPPED: Stop the vehicle when the path is blocked or a pedestrian is detected.

Handled by - Vedant (Week 5 Implementation)
"""

from Utils.config import *

class Planner:
    def __init__(self, world):
        self.world = world
        self.state = "FOLLOW_LANE"
        self.target_lane = "left"  # Start in the left lane
        self.safe_distance = 180  # Distance in pixels to trigger avoidance or stopping

    def update(self, obstacle_info):
        """
        Updates the FSM state based on perception inputs.
        Returns:
            state (str): Current FSM state.
            target_lane (str): The lane the vehicle should target ("left" or "right").
            target_speed (float): The target speed for the controller.
        """
        car_center_x = self.world.car_x + self.world.car_width // 2
        
        # 1. State Transitions
        if self.state == "FOLLOW_LANE":
            target_speed = MAX_SPEED
            
            if obstacle_info is not None:
                distance = obstacle_info["distance"]
                obs_type = obstacle_info["type"]
                
                if distance < self.safe_distance:
                    # Pedestrians always trigger a stop
                    if obs_type == "pedestrian":
                        self.state = "STOPPED"
                    else:
                        # For vehicles and other static obstacles, try to change lanes
                        other_lane = "right" if self.target_lane == "left" else "left"
                        if self.is_lane_clear(other_lane):
                            self.state = "AVOID_OBSTACLE"
                            self.target_lane = other_lane
                        else:
                            # If other lane is blocked, we must stop
                            self.state = "STOPPED"

        elif self.state == "AVOID_OBSTACLE":
            # Slow down slightly during lane change for stability
            target_speed = MAX_SPEED * 0.7
            
            # Determine target center x coordinate
            if self.target_lane == "left":
                target_center_x = self.world.left_lane_center
            else:
                target_center_x = self.world.right_lane_center
                
            # If we are close to the target lane center, switch back to FOLLOW_LANE
            if abs(car_center_x - target_center_x) < 15:
                self.state = "FOLLOW_LANE"
                
            # Emergency stop check during lane change
            if obstacle_info is not None and obstacle_info["distance"] < 80:
                self.state = "STOPPED"

        elif self.state == "STOPPED":
            target_speed = 0.0
            
            # Check if the obstacle in the current lane has cleared
            if obstacle_info is None or obstacle_info["distance"] >= self.safe_distance:
                self.state = "FOLLOW_LANE"
            else:
                # If still blocked, check if we can bypass it now
                obs_type = obstacle_info["type"]
                if obs_type != "pedestrian":
                    other_lane = "right" if self.target_lane == "left" else "left"
                    if self.is_lane_clear(other_lane):
                        self.state = "AVOID_OBSTACLE"
                        self.target_lane = other_lane

        return self.state, self.target_lane, target_speed

    def is_lane_clear(self, lane):
        """
        Checks if the specified lane is clear of obstacles near the ego car.
        """
        detections = self.world.sensor.detect_objects()
        road_center = WINDOW_WIDTH // 2
        
        for det in detections:
            # Classify obstacle lane
            obs_lane = "left" if det["x"] < road_center else "right"
            
            if obs_lane == lane:
                # Calculate longitudinal distance (dy)
                dy = self.world.car_y - det["y"]
                # Block if any obstacle is in front (< safe_distance) 
                # or slightly behind/beside (to avoid side-swipes, e.g., dy > -100)
                if -100 < dy < self.safe_distance + 50:
                    return False
                    
        return True
