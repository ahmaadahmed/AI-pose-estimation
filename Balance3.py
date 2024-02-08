import time
import mediapipe as mp
import cv2

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Start capturing video from the specified file
cap = cv2.VideoCapture(0)

# Get video details
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create a VideoWriter object
output_path = 'balance_exercise.mp4'
new_width = 1280  # Replace with the desired width
new_height = 720  # Replace with the desired height
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'XVID' for AVI format
out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, new_height))

timer = 0.0  # Initialize timer
exercise_duration = 2.0  # Set the minimum duration for an exercise in seconds
exercise_end_time = 0.0  # Initialize exercise end time
is_exercising = False  # Initialize exercising flag
round_count = 1  # Initialize round count
round_durations = []  # List to store the duration of each round
round1=False
round2=False
left_leg_temp=0.0
right_leg_temp=0.0
round_time_temp=0.0
right_leg_timer=0.0
left_leg_timer=0.0
round_count_temp=0

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
        right_knee_x = right_knee.x
        right_heel_x = right_heel.x
        left_knee_x = left_knee.x
        left_heel_x = left_heel.x


        # Update timer based on knee relation
        if round(right_knee_y, 1) < round(left_knee_y, 1) and round(right_knee_x, 2) < round(right_heel_x, 2):
            if right_heel_y < left_knee_y:
                timer += 0.1
                right_leg_timer += 0.1  # Increment timer based on frame rate
                is_exercising = True
                round1=True
        elif round(left_knee_y, 1) < round(right_knee_y, 1) and round(left_knee_x, 2) > round(left_heel_x, 2):
            if left_heel_y < right_knee_y:
                timer += 0.1
                left_leg_timer += 0.1   # Increment timer based on frame rate
                is_exercising = True
                round2=True
        else :
            is_exercising=False

        rounds_lst = []
        if round1==True and round2==True  and is_exercising == False:
            print("Round 2 Begins") 
            exercise_end_time = time.time()  # Record exercise end time
            print(f"Round {round_count} - Exercise counted!")
            round_count_temp=round_count
            round_count += 1
            left_leg_temp=left_leg_timer
            right_leg_temp=right_leg_timer
            round_time_temp=timer

            is_exercising = False
            right_leg_timer = 0.0
            left_leg_timer=0.0
            timer=0.0
            round1=False
            round2=False

        # Draw landmarks on the frame with increased thickness
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=3, circle_radius=3),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=5, circle_radius=4))

        # Display round, timer, and all round durations on the frame
        cv2.putText(frame, f'Round {round_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,  (255, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, f'Timer: {timer:.2f} s', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5,  (255, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, f'Right Leg Timer: {right_leg_timer:.2f} s', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, f'Left Leg Timer: {left_leg_timer:.2f} s', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5,  (255, 0, 0), 1, cv2.LINE_AA)
        
    # Resize the frame to the desired width and height for display
    frame = cv2.resize(frame, (new_width, new_height))

    # Write the resized frame to the output video
    out.write(frame)

    # Display the resized frame
    cv2.imshow('Exercise Timer', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Calculate and print seconds after the last exercise
if exercise_end_time > 0.0:
    total_exercise_time = time.time() - exercise_end_time
    print(f"Total exercise time: {total_exercise_time:.2f} seconds")

# Release the video capture object, video writer, and close all windows
cap.release()
out.release()
cv2.destroyAllWindows()
