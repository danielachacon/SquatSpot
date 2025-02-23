import pandas as pd
import numpy as np
from posetracking import analyze_video

def analyze_all_reps(metrics):    
    
    for rep_num, rep_data in metrics.items():
        if rep_data['knee_balance_bottom']:
            rep_data['knee_balance_right'] = rep_data['knee_balance_bottom'][0]
            rep_data['knee_balance_left'] = rep_data['knee_balance_bottom'][1]
            
    df = pd.DataFrame(metrics.values())
    
    metrics_to_analyze = [
        'max_depth', 'min_spine_angle', 'max_lateral_shift', 
        'max_forward_shift', 'foot_distance', 'grip_width', 
        'elbow_angle', 'knee_balance_right', 'knee_balance_left',
        'bottom_position_held', 'knee_imbalance'
    ]
    
    overall_stats = df[metrics_to_analyze].agg(['mean', 'std']).round(2)
    return overall_stats

def calculate_z_scores_to_gold_standard(your_squat):
    your_stats = analyze_all_reps(your_squat)
    gold_standard = pd.read_csv('squat_analysis_results.csv')
    
    z_scores = {}
    for metric in your_stats.columns:
        your_mean = your_stats.loc['mean', metric]
        your_std = your_stats.loc['std', metric]
        gold_mean = gold_standard[metric].mean()
        gold_std = gold_standard[metric].std()
        
        if gold_std != 0:
            z_scores[metric] = (your_mean - gold_mean) / gold_std
            print(f"\n{metric}:")
            print(f"Your stats: {your_mean:.2f} ± {your_std:.2f}")
            print(f"Gold standard: {gold_mean:.2f} ± {gold_std:.2f}")
            print(f"Z-score: {z_scores[metric]:.2f}")
    
    return z_scores

def compare_2_squats(squat1, squat2):
    # Get the stats DataFrames
    stats1 = analyze_all_reps(squat1)
    stats2 = analyze_all_reps(squat2)
    
    # We only want to compare the mean values
    means1 = stats1.loc['mean']
    means2 = stats2.loc['mean']
    
    print("Means 1:", means1)  # Debug print
    print("Means 2:", means2)  # Debug print
    
    # Define weights for each metric (adjust these based on importance)
    weights = {
        'max_depth': 1.0,
        'min_spine_angle': 0.8,
        'max_lateral_shift': 0.8,
        'max_forward_shift': 0.8,
        'foot_distance': 0.6,
        'grip_width': 0.6,
        'elbow_angle': 0.4,
        'knee_balance_right': 0.7,
        'knee_balance_left': 0.7,
        'bottom_position_held': 0.5,
        'knee_imbalance': 0.7
    }
    
    squared_diff_sum = 0
    total_weight = 0
    
    for col in means1.index:
        # Skip if either value is not numeric
        if not (isinstance(means1[col], (int, float)) and isinstance(means2[col], (int, float))):
            continue
        # Skip if either value is NaN
        if np.isnan(means1[col]) or np.isnan(means2[col]):
            continue
            
        weight = weights.get(col, 1.0)
        # Scale the differences based on typical ranges for each metric
        diff = means1[col] - means2[col]
        if col == 'max_depth':
            diff /= 50  # Typical range of depth variation
        elif col in ['min_spine_angle', 'elbow_angle']:
            diff /= 30  # Typical range of angle variation
        elif col in ['max_lateral_shift', 'max_forward_shift']:
            diff /= 0.5  # Typical range of shift variation
        elif col in ['foot_distance', 'grip_width']:
            diff /= 0.3  # Typical range of distance variation
        elif col in ['knee_balance_right', 'knee_balance_left']:
            diff /= 20  # Typical range of knee angle variation
        elif col == 'bottom_position_held':
            diff /= 15  # Typical range of hold time variation
        elif col == 'knee_imbalance':
            diff /= 10  # Typical range of imbalance variation
            
        squared_diff_sum += (diff ** 2) * weight
        total_weight += weight
        print(f"Weighted difference for {col}: {diff * weight}")  # Debug print
    
    # Calculate weighted average distance
    if total_weight > 0:
        distance = np.sqrt(squared_diff_sum / total_weight)
    else:
        distance = 0
    print("Total weighted distance:", distance)  # Debug print
    
    # Keep k=0.01 but now our distances are better scaled
    k = 0.01
    score = 100 * np.exp(-k * distance)
    
    print("Final score:", score)  # Debug print
    
    # Round to 2 decimal places and ensure it's between 0 and 100
    return max(min(round(float(score), 2), 100), 0)

def compare_2_squats_mse(squat1, squat2):
    squat1 = analyze_all_reps(squat1)
    squat2 = analyze_all_reps(squat2)
    
    errors = [(squat1[key] - squat2[key]) ** 2 for key in squat1]
    mse = np.mean(errors)
    return mse