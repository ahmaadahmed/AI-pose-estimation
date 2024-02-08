import cv2
import time
import mediapipe as mp

# Function to update timer, count exercises, and print seconds after exercise
def update_timer(right_wrist_y, left_wrist_y, right_elbow_y, left_elbow_y, right_knee_y, left_knee_y, timer, exercise_duration, exercise_end_time, is_exercising):
    if right_knee_y < right_elbow_y:
        if round(right_elbow_y, 1) == round(right_wrist_y, 1):
            timer += 1 / fps  # Increment timer based on frame rate
            is_exercising = True

    elif left_knee_y < left_elbow_y:
         if round(left_elbow_y, 1) == round(left_wrist_y, 1):
            timer += 1 / fps  # Increment timer based on frame rate
            is_exercising = True
    else:
        # print(f"Rest duration: {timer:.2f} seconds")
        if is_exercising and timer > exercise_duration:
            exercise_end_time = time.time()  # Record exercise end time
            print("Exercise counted!")
            is_exercising = False
        # Reset timer only when fingers y < wrist y and not exercising
        if not is_exercising:
            timer = 0

    return timer, exercise_end_time, is_exercising

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Specify the path to your video file
# video_path = r'E:\mediapipe-exercises-master\blank\1 minute plank timer with music..mp4'

# Start capturing video from the specified file
cap = cv2.VideoCapture(0)

# Get video details
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create a VideoWriter object
output_path = 'blank_exercise.mp4'
new_width = 1280  # Replace with the desired width
new_height = 720  # Replace with the desired height
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'XVID' for AVI format
out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, new_height))


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
    # Extract specific landmarks
        right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
        right_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
        left_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
        right_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
        left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE] 

        # Get y-coordinates of specific landmarks
        right_wrist_y = right_wrist.y
        left_wrist_y = left_wrist.y
        right_elbow_y = right_elbow.y
        left_elbow_y = left_elbow.y
        right_knee_y = right_knee.y
        left_knee_y = left_knee.y

        # Update timer based on fingers and wrist relation
        timer, exercise_end_time, is_exercising = update_timer(right_wrist_y, left_wrist_y, right_elbow_y, left_elbow_y, right_knee_y, left_knee_y, timer, exercise_duration, exercise_end_time, is_exercising)

        # Draw landmarks on the frame with increased thickness
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=3, circle_radius=3),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=5, circle_radius=4))

    # Display rest duration on the frame
    cv2.putText(frame, f'time: {timer:.2f} s', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,  (255, 0, 0), 1, cv2.LINE_AA)

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

# Release the video capture object, video writer, and close all windows
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Video saved to: {output_path}")

print(timer)