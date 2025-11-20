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