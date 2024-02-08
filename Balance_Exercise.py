import time
import mediapipe as mp
import cv2

# Function to update timer, count exercises, and print seconds after exercise
def update_timer(right_knee_y, left_knee_y, right_heel_y, left_heel_y, timer, exercise_duration, exercise_end_time, is_exercising):
  
    if round(right_knee_y, 1) < round(left_knee_y, 1):
        if right_heel_y < left_knee_y:
            timer += 1 / fps  # Increment timer based on frame rate
            is_exercising = True
           
    elif round(left_knee_y, 1) < round(right_knee_y, 1):
        if left_heel_y < right_knee_y:
            timer += 1 / fps  # Increment timer based on frame rate
            is_exercising = True
          
    else:
        # print(f"Rest duration: {timer:.2f} seconds")
        if is_exercising and timer > exercise_duration:
            exercise_end_time = time.time()  # Record exercise end time
            print("Exercise counted!")
            is_exercising = False
        # Reset timer only when right knee y < left knee y and not exercising
        if not is_exercising:
            timer = 0
           

    return timer, exercise_end_time, is_exercising

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Specify the path to your video file
# video_path = r'E:\mediapipe-exercises-master\balance exercies\balance1.mp4'

# Start capturing video from the specified file
cap = cv2.VideoCapture(0)

# Get video details
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create a VideoWriter object
output_path = 'balance_exercise.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'XVID' for AVI format
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

timer = 0.0  # Initialize timer
exercise_duration = 2.0  # Set the minimum duration for an exercise in seconds
exercise_end_time = 0.0  # Initialize exercise end time
is_exercising = False  # Initialize exercising flag

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
        # Extract knee landmarks
        right_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
        left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
        right_heel = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HEEL]
        left_heel = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HEEL]

        # Get y-coordinates of knees
        right_knee_y = right_knee.y
        left_knee_y = left_knee.y
        right_heel_y = right_heel.y
        left_heel_y = left_heel.y

        # Update timer based on knee relation
        timer, exercise_end_time, is_exercising = update_timer(right_knee_y, left_knee_y, right_heel_y, left_heel_y, timer, exercise_duration, exercise_end_time, is_exercising)

        # Draw landmarks on the frame
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Display rest duration on the frame
    cv2.putText(frame, f'timer: {timer:.2f} s', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

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

# Release the video capture object, video writer, and close all windows
cap.release()
out.release()
cv2.destroyAllWindows()








