import matplotlib.pyplot as plt
import numpy as np
import time
from collections import deque
from HIMUServer import HIMUServer
import scipy.stats
# *****************
import socket
import json
# *****************

class KalmanFilterHeading:
    def __init__(self, initial_heading=0.0):
        # Initial heading (yaw angle in degrees) from orientation sensor
        self.x = initial_heading  
        self.P = 1.0  # Initial covariance

        # Kalman filter matrices
        self.Q = 0.001  # Process noise covariance (gyroscope uncertainty)
        self.R = 0.01   # Measurement noise covariance (magnetometer noise)

    def predict(self, wy, wz, phi, theta, dt):
        """ Predict the new heading using the gyroscope. """
        self.x += (wy * np.sin(phi) / np.cos(theta) + wz * np.cos(phi) / np.cos(theta)) * dt  
        self.P += self.Q  # Update error covariance

    def update(self, mag_heading, ori_yaw, alpha):
        """ Correct heading using magnetometer & orientation sensor. """
        # Combine magnetometer & orientation sensor in the measurement update
        combined_measurement = (1-alpha)*mag_heading + alpha*ori_yaw  # Simple average fusion

        K = self.P / (self.P + self.R)  # Compute Kalman gain
        self.x = self.x + K * (combined_measurement - self.x)  # Update heading
        self.P = (1 - K) * self.P  # Update covariance

    def get_heading(self):
        """ Return the estimated heading. """
        return self.x
    
    
class MyCustomListener:
    def __init__(self, max_points=100, threshold=20):
        self.max_points = max_points
        self.kf = None
        self.heading_list = []
        self.pos = [(0,0)]
        self.pitch_data = deque(maxlen=max_points)  # Stores latest pitch values
        self.heading_data = deque(maxlen=max_points)  # Store last 100 readings
        self.time_data = deque(maxlen=max_points)   # Stores time in seconds
        self.start_time = time.time()  # Get initial timestamp
        self.initialized = False  # Flag to check if initial heading is set

        # Step detection variables
        self.opt_list = [(-80, 0)]  # Store (value, timestamp) pairs
        self.step_count = 0
        self.total_pitch_diff = 0
        self.threshold = threshold  # Threshold for step detection
        self.step_times = []  # Store times when steps are detected
        self.opts = []  # Stores all peaks and troughs
        self.last_step_time = 0  # Global variable to prevent multiple detections
        self.min_step_interval = 0.3  # Minimum time interval between steps (300ms)

        # Live plot setup for position tracking
        plt.ion()
        self.fig, self.ax1 = plt.subplots(1, 1, figsize=(8, 6))

        # Position plot
        self.line_position, = self.ax1.plot([], [], 'g-', label="Indoor Position (X, Y)")
        self.arrow = self.ax1.quiver(0, 0, 0, 0, angles='xy', scale_units='xy', scale=5, color='r', label="User Heading")  # Arrow for heading
        self.ax1.set_xlabel("X Position (m)")
        self.ax1.set_ylabel("Y Position (m)")
        self.ax1.set_title("Indoor Position Tracking")
        self.ax1.legend()
        self.ax1.grid(True)

        # ***************** 
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.target_address = ('localhost', 65432)  # target address and port
        # *****************

    def send_position(self, x, y, heading):
        """ Send position and heading to UDP server """
        data = {
            'x': x,
            'y': y,
            'heading': heading
        }
        try:
            self.udp_socket.sendto(json.dumps(data).encode(), self.target_address)
        except Exception as e:
            print(f"Failure: {str(e)}")
    def update_plot(self):
        """ Update the live plot for position tracking with heading arrow. """
        if len(self.pos) > 1:
            x_vals, y_vals = zip(*self.pos)
            self.line_position.set_data(x_vals, y_vals)
            self.ax1.set_xlim(min(x_vals)-0.5, max(x_vals)+0.5)
            self.ax1.set_ylim(min(y_vals)-0.5, max(y_vals)+0.5)

            # Get latest position and heading
            x, y = self.pos[-1]
            heading = np.radians(self.heading_list[-1]) if len(self.heading_list) > 0 else 0

            # Update arrow direction
            self.arrow.set_offsets([x, y])  # Set position
            self.arrow.set_UVC(np.sin(heading), np.cos(heading))  # Set direction

        self.fig.canvas.flush_events()
        plt.pause(0.01)  # Smooth updates


    def notify(self, sensorData):
        for sensors in sensorData:
            if len(sensors) < 4:
                continue  
            
            ori = HIMUServer.strings2Floats(sensors[3]) if len(sensors) > 3 else [None, None, None, None]
            gyr = HIMUServer.strings2Floats(sensors[2]) if len(sensors) > 2 else [None, None, None]
            mag = HIMUServer.strings2Floats(sensors[0]) if len(sensors) > 0 else [None, None, None]

            if ori is None or len(ori) < 3 or gyr is None or len(gyr) < 3 or mag is None or len(mag) < 3:
                continue  # Skip if data is incomplete

            pitch = -ori[1]  
            
            # Extract gyroscope readings
            wx, wy, wz = gyr

            # Extract orientation sensor values
            theta = -ori[1]  # Pitch
            phi = -ori[2]  # Roll
            ori_yaw = ori[0]  # Yaw (raw orientation sensor)

            # Extract magnetometer readings
            mag_x, mag_y = mag[0], mag[1]
            # Compute magnetometer-based heading
            mag_heading = np.arctan2(mag_y, mag_x) * (180 / np.pi)   # Convert to degrees            

            # Get time elapsed in seconds
            current_time = time.time() - self.start_time
            dt = 0.1

            # Set the initial heading from the orientation sensor
            if not self.initialized:
                self.kf = KalmanFilterHeading(initial_heading = ori_yaw)
                self.initialized = True
                print(f"Initial Heading Set: {ori_yaw:.2f}°")
                continue  # Skip first update to avoid errors

            # Store pitch and time
            self.pitch_data.append(pitch)
            self.time_data.append(current_time)
            
            # Check for step detection
            self.detect_step(pitch, current_time)

            # Kalman filter prediction (using gyro)
            self.kf.predict(wy, wz, phi, theta, dt)

            # Kalman filter update (using magnetometer & orientation sensor)
            self.kf.update(mag_heading, ori_yaw, 0.9)
            
            # Get estimated heading
            self.heading = self.kf.get_heading()
            self.heading_list.append(self.heading)
                        
            # Update the live plot
            self.update_plot()

    def detect_step(self, pitch, current_time):
        """ Detects steps based on pitch maxima and minima with threshold """
        if len(self.pitch_data) < 3:
            return

        is_peak = (
            self.pitch_data[-2] > self.pitch_data[-3] and
            self.pitch_data[-2] > self.pitch_data[-1] and
            self.pitch_data[-2] > self.opt_list[-1][0] + self.threshold
        )

        is_trough = (
            self.pitch_data[-2] < self.pitch_data[-3] and
            self.pitch_data[-2] < self.pitch_data[-1] and
            self.pitch_data[-2] < self.opt_list[-1][0] - self.threshold
        )

        if is_peak:
            self.opt_list.append((self.pitch_data[-2], current_time))
            self.opts.append(("peak", self.pitch_data[-2], current_time))



            print(f"Stored Peak: {self.pitch_data[-2]} at {current_time:.2f}s")

        elif is_trough:
            self.opt_list.append((self.pitch_data[-2], current_time))
            self.opts.append(("trough", self.pitch_data[-2], current_time))
            
            # Store heading at the start of the step 
            self.step_heading_start = self.heading_list[-1]

            print(f"Stored Trough: {self.pitch_data[-2]} at {current_time:.2f}s")

        # Step detection: Check if a peak and trough happen in sequence in opts
        if len(self.opts) >= 2 and self.opts[-2][0] == "peak" and self.opts[-1][0] == "trough":
            peak_value, peak_time = self.opts[-2][1], self.opts[-2][2]
            trough_value, trough_time = self.opts[-1][1], self.opts[-1][2]
            time_diff = abs(trough_time - peak_time)
            pitch_diff = abs(trough_value - peak_value)

            # Ensure a minimum time interval before detecting the next step
            if (0.5 <= time_diff <= 2) and (current_time - self.last_step_time > self.min_step_interval):
                self.step_count += 1
                self.total_pitch_diff += pitch_diff
                self.step_times.append(current_time)
                self.last_step_time = current_time  # Update global last step time

                # Step length calculation
                step_length = 0.01 * pitch_diff + 0.1

                # Compute mean heading from the start of the step (peak) to the end (trough)
                heading_window = self.heading_list[-int(time_diff / 0.1):]  # Select headings during step
                mean_heading = scipy.stats.circmean(heading_window, high=180, low=-180) if len(heading_window) > 0 else self.step_heading_start

                # Compute new x, y position
                offset = 0.5
                x_new = self.pos[-1][0] + step_length * np.sin(np.radians(mean_heading) + offset)
                y_new = self.pos[-1][1] + step_length * np.cos(np.radians(mean_heading) + offset)

                # Append new position
                self.pos.append((x_new, y_new))
                print(f"Step Detected! New Position: ({x_new:.2f}, {y_new:.2f}) | Heading: {mean_heading:.2f}°")
                
                # ***************
                self.send_position(x_new, y_new, mean_heading)
                # ***************

                # Reset opts to prevent duplicate detections
                self.opts = []


                print(f"Step Detected! Total Steps: {self.step_count}, Pitch Difference: {pitch_diff:.2f}")

server = HIMUServer()
listener = MyCustomListener()

server.addListener(listener)
server.start("TCP", 2055)
