import cv2
import mediapipe as mp
import numpy as np
import os
from datetime import datetime

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

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
    world_left_wrist = [world_landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                       world_landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y,
                       world_landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].z]
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
    world_right_wrist = [world_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                        world_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y,
                        world_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].z]
    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

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
        
    'foot_distance': abs(np.linalg.norm(np.array(world_left_ankle) - np.array(world_right_ankle))),
    
    'grip_width': abs(np.linalg.norm(np.array(world_left_wrist) - np.array(world_right_wrist))),
    
    'elbow_angle': calculate_angle(left_shoulder, left_elbow, left_wrist),

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
        'max_depth': float('inf'),
        'min_spine_angle': float('inf'),
        'max_lateral_shift': 0,
        'max_forward_shift': 0,
        'foot_distance': 0,
        'grip_width': 0,
        'elbow_angle': 0,
        'hips_below_knees': False,
        'knee_balance_bottom': None,
        'bottom_position_held': 0,  # frames spent at bottom position
        'knee_imbalance': 0
    }

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()

            if not ret or frame is None:
                print("Error: Failed to read frame.")
                break

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
                cv2.putText(image, str(metrics["depth_left"]), (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, str(metrics["knee_balance"][0] - metrics["knee_balance"][1]), (10, 50), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, stage, (10, 70), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, str(counter), (10, 90), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, str(current_rep['max_lateral_shift']), (10, 110), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

                
                # Get Squat Metrics Per Frame and Per Rep
                if metrics["depth_left"] > 150 :
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
                                'elbow_angle': metrics["elbow_angle"],  # Initialize with current value
                                'hips_below_knees': metrics["hips_below_knees"],  # Initialize with current value
                                'knee_balance_bottom': None,
                                'bottom_position_held': 0,
                                'knee_imbalance': 0
                            }
                    stage = "top rep"
                    top_hip_position = metrics["lateral_hip_position"]
                    lateral_shift = 0
                if metrics["depth_left"] < 150 and stage == 'top rep':
                    stage = "bottom rep"
                    counter += 1
                if stage == "bottom rep":
                    current_rep['max_depth'] = min(current_rep['max_depth'], metrics["depth_left"]) if metrics["depth_left"] > 0 else current_rep['max_depth']
                    current_rep['min_spine_angle'] = min(current_rep['min_spine_angle'], metrics["spine_angle_3"])
                    lateral_shift = (top_hip_position - metrics["lateral_hip_position"]) * 100
                    current_rep['max_lateral_shift'] = lateral_shift if abs(lateral_shift) > abs(current_rep['max_lateral_shift']) else current_rep['max_lateral_shift']
                    current_rep['max_forward_shift'] = metrics['weight_shift'] if abs(metrics['weight_shift']) > abs(current_rep['max_forward_shift']) else current_rep['max_forward_shift']
                    current_rep['foot_distance'] = max(current_rep['foot_distance'], metrics["foot_distance"])
                    current_rep['grip_width'] = max(current_rep['grip_width'], metrics["grip_width"])
                    current_rep['elbow_angle'] = max(current_rep['elbow_angle'], metrics["elbow_angle"])
                    current_rep['hips_below_knees'] = current_rep['hips_below_knees'] or metrics["hips_below_knees"]

                    # Track knee balance at bottom position
                    if metrics["depth_left"] < 120:  # Deep squat position
                        current_rep['bottom_position_held'] += 1
                        if current_rep['knee_balance_bottom'] is None:
                            current_rep['knee_balance_bottom'] = metrics["knee_balance"]
                        knee_imbalance = metrics["knee_balance"][0] - metrics["knee_balance"][1]
                        current_rep['knee_imbalance'] = knee_imbalance if abs(knee_imbalance) > abs(current_rep['knee_imbalance']) else current_rep['knee_imbalance']
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
    cap.release()
    cv2.destroyAllWindows()

    return perSquatMetrics

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

def analyze_video_upload(video_source):
    print(f"Starting video analysis from: {video_source}")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_source)
    
    # Check if video opened successfully
    if not cap.isOpened():
        print(f"Error: Could not open video file: {video_source}")
        return None, None

    # Initialize metrics tracking variables
    counter = 0
    stage = None
    apex = 1000
    top_hip_position = 0
    lateral_shift = 0
    perSquatMetrics = {}
    current_rep = {
        'max_depth': float('inf'),
        'min_spine_angle': float('inf'),
        'max_lateral_shift': 0,
        'max_forward_shift': 0,
        'foot_distance': 0,
        'grip_width': 0,
        'elbow_angle': 0,
        'hips_below_knees': False,
        'knee_balance_bottom': None,
        'bottom_position_held': 0,
        'knee_imbalance': 0
    }

    # Get video properties and set up writer
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"processed_video_{timestamp}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    frame_count = 0
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            
            try:
                # Process frame
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = pose.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # Extract Landmarks and calculate metrics
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    world_landmarks = results.pose_world_landmarks.landmark
                    metrics = calculate_statistics(landmarks, world_landmarks)
                    
                    # Track squat metrics
                    if metrics["depth_left"] > 150:
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
                                    'elbow_angle': metrics["elbow_angle"],
                                    'hips_below_knees': metrics["hips_below_knees"],
                                    'knee_balance_bottom': None,
                                    'bottom_position_held': 0,
                                    'knee_imbalance': 0
                                }
                        stage = "top rep"
                        top_hip_position = metrics["lateral_hip_position"]
                        lateral_shift = 0
                    if metrics["depth_left"] < 150 and stage == 'top rep':
                        stage = "bottom rep"
                        counter += 1
                    if stage == "bottom rep":
                        current_rep['max_depth'] = min(current_rep['max_depth'], metrics["depth_left"]) if metrics["depth_left"] > 0 else current_rep['max_depth']
                        current_rep['min_spine_angle'] = min(current_rep['min_spine_angle'], metrics["spine_angle_3"])
                        lateral_shift = (top_hip_position - metrics["lateral_hip_position"]) * 100
                        current_rep['max_lateral_shift'] = lateral_shift if abs(lateral_shift) > abs(current_rep['max_lateral_shift']) else current_rep['max_lateral_shift']
                        current_rep['max_forward_shift'] = metrics['weight_shift'] if abs(metrics['weight_shift']) > abs(current_rep['max_forward_shift']) else current_rep['max_forward_shift']
                        current_rep['foot_distance'] = max(current_rep['foot_distance'], metrics["foot_distance"])
                        current_rep['grip_width'] = max(current_rep['grip_width'], metrics["grip_width"])
                        current_rep['elbow_angle'] = max(current_rep['elbow_angle'], metrics["elbow_angle"])
                        current_rep['hips_below_knees'] = current_rep['hips_below_knees'] or metrics["hips_below_knees"]

                        if metrics["depth_left"] < 120:
                            current_rep['bottom_position_held'] += 1
                            if current_rep['knee_balance_bottom'] is None:
                                current_rep['knee_balance_bottom'] = metrics["knee_balance"]
                            knee_imbalance = metrics["knee_balance"][0] - metrics["knee_balance"][1]
                            current_rep['knee_imbalance'] = knee_imbalance if abs(knee_imbalance) > abs(current_rep['knee_imbalance']) else current_rep['knee_imbalance']

                    # Draw metrics on frame
                    cv2.putText(image, f"Depth: {metrics['depth_left']:.1f}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.putText(image, f"Rep: {counter}", (10, 50), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.putText(image, f"Stage: {stage}", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

                # Draw landmarks
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        image, 
                        results.pose_landmarks, 
                        mp_pose.POSE_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                        mp_drawing.DrawingSpec(color=(0,0,255), thickness=2, circle_radius=2)
                    )
                
                # Write frame to output video
                out.write(image)
                
            except Exception as e:
                print(f"Error processing frame {frame_count}: {str(e)}")
                continue

    # Save final rep if exists
    if counter > 0 and stage == "bottom rep":
        perSquatMetrics[counter] = current_rep

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    print(f"Successfully processed {frame_count} frames")
    print(f"Processed video saved to: {output_path}")
    print(f"Found {len(perSquatMetrics)} squats")
    
    return output_path, perSquatMetrics

