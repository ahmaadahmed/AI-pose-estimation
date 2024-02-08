#  and round(left_ankle_x, 1) != round(left_knee_x) and round(right_ankle_x) != round(right_knee_x):
import cv2
import time
import mediapipe as mp

import cv2
import time
import mediapipe as mp

# Function to update timer, count exercises, and print seconds after exercise
def update_timer(right_fingers_y, right_wrist_y, left_fingers_y, left_wrist_y, left_ankle_x, right_ankle_x, left_knee_x, right_knee_x, timer, exercise_duration, exercise_end_time, is_exercising, fps, reset_threshold=2):
    global false_condition_counter  # Global variable to keep track of false condition duration

    if right_fingers_y < right_wrist_y and left_fingers_y < left_wrist_y:
        if round(right_fingers_y, 1) == round(left_fingers_y, 1) and round(right_wrist_y, 1) == round(left_wrist_y, 1):
            timer += 1 / fps  # Increment timer based on frame rate
            is_exercising = True
            false_condition_counter = 0  # Reset false condition counter when the condition is true
    else:
        false_condition_counter += 1 / fps  # Increment false condition counter

        # If the false condition has been continuous for at least 2 seconds, reset the timer
        if false_condition_counter >= reset_threshold:
            timer = 0
            false_condition_counter = 0

        if is_exercising and timer > exercise_duration:
            exercise_end_time = time.time()  # Record exercise end time
            print("Exercise counted!")
            is_exercising = False

    return timer, exercise_end_time, is_exercising

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Start capturing video from the default camera (camera index 0)
cap = cv2.VideoCapture(0)

# Get video details
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create a VideoWriter object
output_path = 'Yoga.mp4'
new_width = 1280  # Replace with the desired width
new_height = 720  # Replace with the desired height
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'XVID' for AVI format
out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, new_height))

timer = 0.0  # Initialize timer
exercise_duration = 2.0  # Set the minimum duration for an exercise in seconds
exercise_end_time = 0.0  # Initialize exercise end time
is_exercising = False  # Initialize exercising flag

current_round = 1
round_timer = 0.0
round_duration = 10.0  # Adjust the duration for each round as needed

exercise_counter = 0  # Initialize exercise counter
false_condition_counter = 0  # Initialize false condition counter

while cap.isOpened():
    # Read frame from the video
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the image and get the pose landmarks
    results = pose.process(rgb_frame)

    # Check if pose landmarks are detected
    if results.pose_landmarks:
        # Extract hand fingers and wrists landmarks
        right_hand_fingers = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_THUMB]
        right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        left_hand_fingers = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_THUMB]
        left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
        left_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]
        right_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]
        left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
        right_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]

        # Get y-coordinates of hand fingers and wrist
        right_fingers_y = right_hand_fingers.y
        right_wrist_y = right_wrist.y
        left_fingers_y = left_hand_fingers.y
        left_wrist_y = left_wrist.y
        left_ankle_x = left_ankle.x
        right_ankle_x = right_ankle.x
        left_knee_x = left_knee.x
        right_knee_x = right_knee.x

        # Update timer based on fingers and wrist relation
        timer, exercise_end_time, is_exercising = update_timer(right_fingers_y, right_wrist_y, left_fingers_y, left_wrist_y, left_ankle_x, right_ankle_x, left_knee_x, right_knee_x, timer, exercise_duration, exercise_end_time, is_exercising, fps)

        # Display rest duration on the frame
        cv2.putText(frame, f'Time: {timer:.2f} s', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,  (255, 0, 0), 1, cv2.LINE_AA)

        # Display round information below the timer
        cv2.putText(frame, f'Round {current_round}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

        # Check if exercise is reset (timer is reset)
        if timer == 0 and exercise_end_time > 0.0:
            if is_exercising:
                current_round += 1  # Increment the round
            round_timer = 0.0   # Reset the round timer

            if is_exercising:
                exercise_counter += 1  # Increment the exercise counter

        # Increment round_timer
        round_timer += 1 / fps

        # Check if the round duration has been exceeded
        if round_timer > round_duration:
            print(f"End of Round {current_round}")
            # Perform any additional actions needed at the end of a round
            round_timer = 0.0  # Reset the round timer

    # Draw landmarks on the frame with increased thickness
    mp_drawing.draw_landmarks(
        frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=3, circle_radius=3),
        connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=5, circle_radius=4))

    # Resize the frame to the desired width and height for display
    frame = cv2.resize(frame, (new_width, new_height))

    # Write the frame to the output video
    out.write(frame)

    # Display the frame
    cv2.imshow('Exercise Timer', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Calculate and print seconds after exercise
if exercise_end_time > 0.0:
    total_exercise_time = time.time() - exercise_end_time
    print(f"Total exercise time: {total_exercise_time:.2f} seconds")

# Print the total number of exercises
print(f"Total exercises: {exercise_counter}")

# Release the video capture object, video writer, and close all windows
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Video saved to: {output_path}")

