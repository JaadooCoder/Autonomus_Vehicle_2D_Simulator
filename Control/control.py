"""
This script manages the control subsystem of the autonomous vehicle. It implements a PID controller
for lateral steering control and a longitudinal controller to match target speeds requested by the planner.

Handled by - Vedant (Week 5 Implementation)
"""

from Utils.config import *

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0.0
        self.integral = 0.0

    def update(self, error, dt=1.0):
        self.integral += error * dt
        # Simple derivative calculation
        derivative = (error - self.prev_error) / dt
        self.prev_error = error
        return (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)

class VehicleController:
    def __init__(self, world):
        self.world = world
        # Initialize lateral PID controller with tuned gains
        self.steer_pid = PIDController(kp=0.03, ki=0.0, kd=0.01)

    def control(self, target_x, target_speed):
        """
        Applies lateral and longitudinal control commands to steer and adjust speed.
        """
        # 1. Lateral Control (Steering)
        car_center_x = self.world.car_x + self.world.car_width // 2
        lateral_error = target_x - car_center_x
        
        # Calculate steer output using PID
        steer_cmd = self.steer_pid.update(lateral_error)
        
        # Clamp steering output between -1.0 (Full Left) and 1.0 (Full Right)
        steer_cmd = max(-1.0, min(1.0, steer_cmd))
        
        # Apply steering to change vehicle x position
        self.world.car_x += steer_cmd * CAR_SPEED
        
        # Ensure we stay within road boundaries
        road_left = (WINDOW_WIDTH - ROAD_WIDTH) // 2
        road_right = (road_left + ROAD_WIDTH) - self.world.car_width
        self.world.car_x = max(road_left, min(self.world.car_x, road_right))

        # 2. Longitudinal Control (Speed)
        if self.world.speed < target_speed:
            # Accelerate
            self.world.speed += self.world.acceleration
            if self.world.speed > target_speed:
                self.world.speed = target_speed
        elif self.world.speed > target_speed:
            # Brake
            self.world.speed -= self.world.brake_force
            if self.world.speed < 0:
                self.world.speed = 0.0

        return steer_cmd
