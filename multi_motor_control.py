import serial
import time
import numpy as np
from robot import Robot, TrajectoryGenerator

# Set your serial port 
# Please check the port you connec the arduino board before running the code
SERIAL_PORT = "COM3"  # For Windows: "COMx", for Linux/Mac: "/dev/ttyUSB0"
BAUD_RATE = 9600  # Must match the Arduino baud rate

# Open serial connection
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Allow time for Arduino to reset
    print("Connected to Arduino!")
except Exception as e:
    print(f"Error: {e}")
    exit()

# This is the function to move the motor.
# motor_num: 1-5
# angle: positive = clockwise negative = counterclockwise
# speed: scale 0-1
def send_motor_command(motor_num, angle, speed):
    """ Sends a formatted command to the Arduino """
    command = f"{motor_num} {angle} {speed}\n"
    arduino.write(command.encode())  # Send command
    print(f"Sent: {command.strip()}")
    
    # Wait for response from Arduino
    response = arduino.readline().decode().strip()
    if response:
        print(f"Arduino: {response}")

# Example commands

#send_motor_command(1, 180, 1.0)
#send_motor_command(1, 90, 0.5)  # Move Motor 1, 90 degrees at 50% speed
#time.sleep(1)
#send_motor_command(2, 180, 1.0)  # Move Motor 2, 180 degrees at full speed
#time.sleep(1)
#send_motor_command(3, 360, 0.7)  # Move Motor 3, 45 degrees at 20% speed
#time.sleep(1)
#send_motor_command(4, 360, 0.5)  # Move Motor 4, full rotation at 80% speed
#time.sleep(1)
#send_motor_command(5, 360, 0.5)
#send_motor_command(2, 3600, 1.0)
#send_motor_command(3, 3600, 1.0)
#time.sleep(2)
#send_motor_command(1, 90, 1.0)
#send_motor_command(4, -90, 1.0)
#time.sleep(4)
#send_motor_command(1, 3510, 1.0)
#send_motor_command(4, 36090, 1.0)
#time.sleep(4)
#send_motor_command(5, -90, 1.0)
#time.sleep(2)
#send_motor_command(5, 36090, 1.0)

# Close serial connection
#arduino.close()
#print("Connection closed.")

# ========== MAIN FUNCTION ==========
def main():
    # Initialize robot & trajectory objects
    robot = Robot()
    traj_gen = TrajectoryGenerator()

    # Define target pose (4x4 transformation matrix)
    target_pose = np.eye(4)
    target_pose[:3, 3] = [0.2, 0.1, 0.2]  # Desired XYZ position of end-effector (example)

    # Initial joint seed (e.g., all zeros)
    seed = np.zeros(robot.dof)

    # Inverse Kinematics
    solution = robot._inverse_kinematics(target_pose, seed)

    if solution is None:
        print("IK failed. Could not reach the desired pose.")
        return

    print("IK solution (radians):", solution)

    # Trajectory generation
    trajectory = traj_gen.generate_trapezoidal_trajectory(seed, solution, traj_gen.max_vel, traj_gen.max_acc, duration=4.0)

    # Send joint angles to Arduino
    print("Sending trajectory to Arduino...")
    traj_gen.follow_joint_trajectory(trajectory, send_motor_command)
    print("Motion complete.")

# ========== RUN MAIN ==========
if __name__ == "__main__":
    main()
    arduino.close()
    print("Connection closed.")