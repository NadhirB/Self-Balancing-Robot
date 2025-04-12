# A PID class object controller designed for the balancing robot project
# Coded by Nadhir Busheri Apr 2025

class PID:
    def __init__(self, p_value = 1.0, i_value = 0.0, d_value = 0.0):
        self.p_value = p_value
        self.i_value = i_value
        self.d_value = d_value

        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = None

    def compute_pid(self, desired_value, measured_value, dt):
        """
        Computes the PID gain
        :param desired_value: should be a constant
        :param measured_value: passed from the main loop
        :param dt: passed from the main loop
        :return: the
        """
        # computing the error
        error = desired_value - measured_value

        # Proportional: is computed directly in the output

        # Integral:
        self.integral += error * dt

        # Derivative:
        derivative = (error - self.last_error) / dt if dt > 0 else 0.0

        # Combine all components and compute proportional part
        output = self.p_value * error + self.d_value * derivative + self.i_value * self.integral

        self.last_error = error
        self.last_time = dt

        return output