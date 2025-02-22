import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Calculate Angle
def calculate_angle(a,b,c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])

    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360-angle
        
    return angle

def calculate_statistics(landmarks, world_landmarks):
    left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
    left_shoulder = (world_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                 world_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y)
    world_left_ankle = [world_landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
              world_landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y,
              world_landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].z]
    world_left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    left_foot_index = [landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x, landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y]
    right_foot_index = [landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y]
    left_heel = [landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y]
    right_heel = [landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].y]
    right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
    right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
    right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
    right_shoulder = (world_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                  world_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y)
    world_right_ankle = [world_landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
               world_landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y,
               world_landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].z]
    world_right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
    
    # Hips Below knees
    if landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y <= landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y and landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y <= landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y:
        hipsBelowKnees = True
    else:
        hipsBelowKnees = False

    # Weight shift (Forward/Backward)
    shoulder_mid_x = (left_shoulder[0] + right_shoulder[0]) / 2
    ankle_mid_x = (left_ankle[0] + right_ankle[0]) / 2
    
    # Weight shift based on angle between toe heel ankle
    right_foot_angle = calculate_angle(right_foot_index, right_heel, right_ankle)
    left_foot_angle = calculate_angle(left_foot_index, left_heel, left_ankle)
    
    # Weight shift lateral
    left_mid_x = (left_hip[0] + left_ankle[0]) / 2

    metrics = {
    'depth_left': calculate_angle(left_ankle, left_knee, left_hip),
    
    'depth_right': calculate_angle(right_ankle, right_knee, right_hip),
    
    'knee_balance': [right_foot_angle, left_foot_angle],
    
    'hips_below_knees': hipsBelowKnees,
        
    'foot_distance': np.linalg.norm(np.array(world_left_ankle) - np.array(world_right_ankle)),
    
    'grip_width': np.linalg.norm(np.array(world_left_wrist) - np.array(world_right_wrist)),
    
    'weight_shift': (shoulder_mid_x - ankle_mid_x),
    
    'lateral_hip_position': left_mid_x,
    
    'spine_angle_1': calculate_angle(left_knee, left_hip, left_shoulder),
    'spine_angle_2': calculate_angle(right_knee, right_hip, right_shoulder),
    'spine_angle_3': left_shoulder[1] - left_hip[1]
    }
    
    return metrics


def analyze_video(video=0):
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    counter = 0
    stage = None
    apex = 1000
    prev_landmarks = None
    prev_world_landmarks = None
    top_rep_statistics = None
    top_hip_position = 0
    lateral_shift = 0

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            
            # Recolor Image because we want our image to be passed to MediaPipe in format to RGB (Default is of BGR)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            # Make detection (Pose model)
            results = pose.process(image)
            
            # Recolor back to BGR for opencv
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Extract Landmarks
            try:
                landmarks = results.pose_landmarks.landmark
                world_landmarks = results.pose_world_landmarks.landmark
                metrics = calculate_statistics(landmarks, world_landmarks)
                apex = min((world_landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y + world_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y) / 2, apex) # Bottom of Squat
                
                # Display the metrics on the image
                cv2.putText(image, stage, (10, 70), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, str(counter), (10, 90), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                
                if metrics["depth_left"] > 170:
                    stage = "top rep"
                    top_hip_position = metrics["lateral_hip_position"]
                    lateral_shift = 0
                if metrics["depth_left"] < 120 and stage == "top rep":
                    stage = "during rep"
                    counter += 1
                if metrics["depth_left"] < 150:
                    lateral_shift = (top_hip_position - metrics["lateral_hip_position"]) * 100
                    
            except:
                pass
            
            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                                    mp_drawing.DrawingSpec(color=(0,0,255), thickness=2, circle_radius=2))
            
            cv2.imshow('Mediapipe Feed', image)
            
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
            
            prev_landmarks = landmarks
            prev_world_landmarks = prev_world_landmarks

        cap.release()
        cv2.destroyAllWindows()