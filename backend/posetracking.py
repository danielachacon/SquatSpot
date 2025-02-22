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


def analyze_video(video_source=0):
    cap = cv2.VideoCapture(video_source)
    target_width, target_height = 640, 480

    counter = 0
    stage = None
    apex = 1000
    prev_landmarks = None
    prev_world_landmarks = None
    top_rep_statistics = None
    top_hip_position = 0
    lateral_shift = 0
    perSquatMetrics = {}
    current_rep = {
        'max_depth': 0,
        'min_spine_angle': float('inf'),
        'max_lateral_shift': 0,
        'max_forward_shift': 0,
        'foot_distance': 0,
        'grip_width': 0,
        'knee_balance_bottom': None,
        'bottom_position_held': 0,  # frames spent at bottom position
        'knee_imbalance': 0
    }

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break # for uploaded videos
            
            # Recolor Image because we want our image to be passed to MediaPipe in format to RGB (Default is of BGR)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            # Make detection (Pose model)
            results = pose.process(image)
            
            # Recolor back to BGR for opencv
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            image = resize_and_crop(image, target_width, target_height)  # Resize the frame to 640x480

            # Extract Landmarks
            try:
                landmarks = results.pose_landmarks.landmark
                world_landmarks = results.pose_world_landmarks.landmark
                metrics = calculate_statistics(landmarks, world_landmarks)
                apex = min((world_landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y + world_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y) / 2, apex) # Bottom of Squat
                
                # Display the metrics on the image
                print(metrics["knee_balance"])
                print(metrics["foot_distance"])
                cv2.putText(image, str(metrics["knee_balance"]), (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(image, str(metrics["knee_balance"][0] - metrics["knee_balance"][1]), (10, 50), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, stage, (10, 70), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, str(counter), (10, 90), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                
                # Get Squat Metrics Per Frame and Per Rep
                if metrics["depth_left"] > 160 :
                    if stage != "top rep":
                        if counter > 0:
                            perSquatMetrics[counter] = current_rep.copy()
                            current_rep = {
                                'max_depth': float('inf'),
                                'min_spine_angle': float('inf'),
                                'max_lateral_shift': 0,
                                'max_forward_shift': 0,
                                'foot_distance': 0,
                                'grip_width': 0,
                                'knee_balance_bottom': None,
                                'bottom_position_held': 0,  # frames spent at bottom position
                                'hips_below_knees': False,
                                'knee_imbalance': 0
                            }
                    stage = "top rep"
                    top_hip_position = metrics["lateral_hip_position"]
                    lateral_shift = 0
                if metrics["depth_left"] < 160 and stage == 'top rep':
                    stage = "bottom rep"
                    counter += 1
                if stage == "bottom rep":
                    current_rep['max_depth'] = min(current_rep['max_depth'], metrics["depth_left"])
                    current_rep['min_spine_angle'] = min(current_rep['min_spine_angle'], metrics["spine_angle_3"])
                    lateral_shift = (top_hip_position - metrics["lateral_hip_position"]) * 100
                    current_rep['max_lateral_shift'] = lateral_shift if abs(lateral_shift) > abs(current_rep['max_lateral_shift']) else current_rep['max_lateral_shift']
                    current_rep['max_forward_shift'] = metrics['weight_shift'] if abs(metrics['weight_shift']) > abs(current_rep['max_forward_shift']) else current_rep['max_forward_shift']
                    current_rep['foot_distance'] = max(current_rep['foot_distance'], metrics["foot_distance"])
                    current_rep['grip_width'] = max(current_rep['grip_width'], metrics["grip_width"])
                    knee_imbalance = metrics["knee_balance"][0] - metrics["knee_balance"][1]
                    current_rep['knee_imbalance'] = knee_imbalance if abs(knee_imbalance) > abs(current_rep['knee_imbalance']) else current_rep['knee_imbalance']

                    if metrics["hips_below_knees"]:
                        current_rep['hips_below_knees'] = True
                        
                    # Track knee balance at bottom position
                    if metrics["depth_left"] < 120:  # Deep squat position
                        current_rep['bottom_position_held'] += 1

                        if current_rep['knee_balance_bottom'] is None:
                            current_rep['knee_balance_bottom'] = metrics["knee_balance"]
                    
            except:
                pass
            
            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                                    mp_drawing.DrawingSpec(color=(0,0,255), thickness=2, circle_radius=2))
            #replaces cv2 imshow with the following so that cv2 encodes the frames as JPEG (for web streaming) and uses
            #yield to continuously send frames back to flask
            #Got rid of the wait key, bc flask doesn't need it for streaming
            _, buffer = cv2.imencode('.jpg', image)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            prev_landmarks = landmarks
            prev_world_landmarks = prev_world_landmarks

        cap.release()
        cv2.destroyAllWindows()


def resize_and_crop(image, target_width=640, target_height=480):
    """Resizes and crops the image while maintaining aspect ratio."""
    h, w = image.shape[:2]

    #maintain asp ratio
    scale = min(target_width / w, target_height / h)
    new_w, new_h = int(w * scale), int(h * scale)

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    #out is 640x480 with black padding if needed
    canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    start_x = (target_width - new_w) // 2
    start_y = (target_height - new_h) // 2
    canvas[start_y:start_y + new_h, start_x:start_x + new_w] = resized

    return canvas

