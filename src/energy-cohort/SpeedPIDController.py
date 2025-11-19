import math


# ==============================================================================
# -------------------------- PID Controller ---------------------------
# ==============================================================================

class SpeedPIDController:
    def __init__(self, Kp, Ki, Kd, max_integral, deadband, min_throttle, min_brake, filter_alpha, throttle_smoothing):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.max_integral = max_integral
        self.deadband = deadband
        self.min_throttle = min_throttle
        self.min_brake = min_brake
        self.last_steer = 0.0

        # Internal state
        self.integral = 0.0
        self.last_error = 0.0
        self.last_throttle = 0.0
        self.filtered_speed = None

        # Filters
        self.filter_alpha = filter_alpha  # Low-pass filter factor
        self.throttle_smoothing = throttle_smoothing

        # Moving average buffer
        self.moving_avg_window = []
        self.moving_avg_maxlen = 5
        self.use_moving_avg_threshold = 8.0  # [m/s] ~28.8 km/h

    def reset(self):
        self.integral = 0.0
        self.last_error = 0.0
        self.last_throttle = 0.0
        self.filtered_speed = None
        self.moving_avg_window = []

    def apply_lowpass_filter(self, new_speed):
        if self.filtered_speed is None:
            self.filtered_speed = new_speed
        else:
            self.filtered_speed = (self.filter_alpha * new_speed +
                                   (1 - self.filter_alpha) * self.filtered_speed)
        return self.filtered_speed

    def apply_moving_average(self, new_speed):
        self.moving_avg_window.append(new_speed)
        if len(self.moving_avg_window) > self.moving_avg_maxlen:
            self.moving_avg_window.pop(0)
        return sum(self.moving_avg_window) / len(self.moving_avg_window)

    def smooth_throttle(self, raw_throttle):
        smoothed = max(min(raw_throttle, self.last_throttle + self.throttle_smoothing),
                       self.last_throttle - self.throttle_smoothing)
        self.last_throttle = smoothed
        return smoothed

    def smooth_brake(self, raw_brake):
        smoothed = max(min(raw_brake, self.last_throttle + self.throttle_smoothing),
                    self.last_throttle - self.throttle_smoothing)
        return smoothed

    def compute_control(self, current_speed, desired_speed, dt):
        # Apply appropriate filter
        if current_speed >= self.use_moving_avg_threshold:
            current_speed = self.apply_moving_average(current_speed)
        else:
            current_speed = self.apply_lowpass_filter(current_speed)

        # Calculate error
        error = desired_speed - current_speed

        # Deadband: skip small errors
        if abs(error) < self.deadband:
            self.last_throttle = 0.0
            return 0.0, 0.0, 0.0

        # 🔧 Kickstart from stop if desired speed is non-zero
        if current_speed < 0.1 and desired_speed > 0.5:
            control = max(self.min_throttle, 0.6)  # Force enough throttle to start
        
        else: 
            # PID calculations
            self.integral += error * dt
            self.integral = max(-self.max_integral, min(self.max_integral, self.integral))  # Anti-windup

            derivative = (error - self.last_error) / dt if dt > 0 else 0.0
            self.last_error = error

            control = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # Output control
        throttle = 0.0
        brake = 0.0

        if control > 0:
            # throttle = max(self.min_throttle, min(control, 1.0))
            # throttle = self.smooth_throttle(throttle)
            # brake = 0.0
            if current_speed < self.use_moving_avg_threshold:
                throttle = max(self.min_throttle, min(control, 1.0))  # 🚀 No smoothing at low speed
            else:
                throttle = self.smooth_throttle(max(self.min_throttle, min(control, 1.0)))  # 🧽 Smooth at high speed
            brake = 0.0
            
        elif control < 0:
            # brake = max(self.min_brake, min(abs(control), 1.0))
            # self.last_throttle = 0.0  # Reset throttle to avoid jump on next cycle
            
            brake = max(self.min_brake, min(abs(control), 1.0))
            if current_speed >= self.use_moving_avg_threshold:
                brake = self.smooth_brake(brake)  # 💡 Smoother brake at high speeds
            self.last_throttle = 0.0  # Reset throttle to avoid jump on next cycle


        return throttle, brake, control
    
    def compute_steering_angle(self, current_heading, desired_heading, current_speed_mps):
        """
        Compute a normalized steering value based on current GPS position and desired GPS waypoint.

        Args:
            current_lat (float): Current latitude
            current_lon (float): Current longitude
            desired_lat (float): Target latitude
            desired_lon (float): Target longitude
            current_heading (float): Compass heading in degrees

        Returns:
            float: Steering value in range [-1.0, 1.0]
        """
        # Compute heading error
        heading_error = desired_heading - current_heading
        heading_error = (heading_error + 180) % 360 - 180  # Normalize to [-180, 180]

        # # Apply proportional control
        # Kp_steer = 0.015  # Steering gain (adjustable)
        # steer = Kp_steer * heading_error

        # # Clamp to [-1.0, 1.0]
        # steer = max(-1.0, min(1.0, steer))

        # # Optional smoothing (low-pass filter)
        # alpha = 1.0
        # steer = alpha * steer + (1 - alpha) * self.last_steer
        # self.last_steer = steer
        
        # return steer
        
        # Speed-based steering gain (smaller gain at higher speeds)
        if current_speed_mps < 5.0:
            Kp_steer = 0.02  # More responsive at low speed
        elif current_speed_mps < 15.0:
            Kp_steer = 0.015
        else:
            Kp_steer = 0.01  # Less twitchy at high speed

        raw_steer = Kp_steer * heading_error

        # Clamp to [-1.0, 1.0]
        raw_steer = max(-1.0, min(1.0, raw_steer))

        # Apply exponential smoothing
        alpha = 0.3  # 0.1-0.4 works well, lower = smoother
        smoothed_steer = alpha * raw_steer + (1 - alpha) * self.last_steer
        self.last_steer = smoothed_steer
        
        return smoothed_steer

        
    
    def compute_steering_from_xy(self, current_x, current_y, current_yaw, desired_x, desired_y):
        Kp=0.015
        # Compute vector from current to desired point
        dx = desired_x - current_x
        dy = desired_y - current_y

        # Compute desired yaw (in degrees)
        desired_yaw = math.degrees(math.atan2(dy, dx))

        # Normalize angles
        current_yaw = current_yaw % 360
        desired_yaw = desired_yaw % 360

        # Calculate yaw error [-180, 180]
        yaw_error = (desired_yaw - current_yaw + 180) % 360 - 180

        # Apply proportional control
        steer = Kp * yaw_error

        # Clamp to [-1.0, 1.0]
        steer = max(-1.0, min(1.0, steer))

        return steer