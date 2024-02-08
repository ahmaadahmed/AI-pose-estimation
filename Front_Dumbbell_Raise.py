import cv2
import time
import mediapipe as mp

# Function to count exercises
def count_exercises(right_wrist_y, right_shoulder_y, right_elbow_y, prev_wrist_shoulder_relation, counter):
    current_wrist_shoulder_relation = right_wrist_y > right_shoulder_y and right_elbow_y > right_shoulder_y
    
    if prev_wrist_shoulder_relation and not current_wrist_shoulder_relation:
        counter += 1

    # print(f"Exercise count: {counter}")
    # print(f"right wrist Y: {right_wrist_y}, right elbow Y: {right_elbow_y}, right shoulder Y: {right_shoulder_y}")
    return current_wrist_shoulder_relation, counter

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# video_path = r"E:\mediapipe-exercises-master\Alternating Front Dumbbell Raise - How to do Dumbbell Alternating Front Raises.mp4"
# Start capturing video from the specified file
# video_path = r"E:\mediapipe-exercises-master\Alternating Front Dumbbell Raise - How to do Dumbbell Alternating Front Raises.mp4"
cap = cv2.VideoCapture(0)

# Get video details
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create a VideoWriter object
output_path = 'front_dumbbell_raise.mp4'
new_width = 1280  # Replace with the desired width
new_height = 720  # Replace with the desired height
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'XVID' for AVI format
out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, new_height))


counter = 0  # Initialize exercise counter
prev_wrist_shoulder_relation = False  # Initialize previous wrist-shoulder relation

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
        # Extract right wrist, right shoulder, and right elbow landmarks
        right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        right_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]

        # Get y-coordinates of right wrist, right shoulder, and right elbow
        right_wrist_y = right_wrist.y
        right_shoulder_y = right_shoulder.y
        right_elbow_y = right_elbow.y

        # Update state and count exercises based on the condition
        prev_wrist_shoulder_relation, counter = count_exercises(right_wrist_y, right_shoulder_y, right_elbow_y, prev_wrist_shoulder_relation, counter)
        
        # Draw landmarks on the frame with increased thickness
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=3, circle_radius=3),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=5, circle_radius=4))

    # Display exercise count on the frame
    cv2.putText(frame, f'Counter: {counter}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,  (255, 0, 0), 1, cv2.LINE_AA)

    # Resize the frame to the desired width and height for display
    frame = cv2.resize(frame, (new_width, new_height))

    # Write the frame to the output video
    out.write(frame)

    # Display the frame
    cv2.imshow('Exercise Counter', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object, video writer, and close all windows
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Video saved to: {output_path}")
print(counter)