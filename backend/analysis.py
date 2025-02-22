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
    squat1 = analyze_all_reps(squat1)
    squat2 = analyze_all_reps(squat2)
    
    distance = np.sqrt(sum((squat1[key] - squat2[key]) ** 2 for key in squat1))
    return distance

def compare_2_squats_mse(squat1, squat2):
    squat1 = analyze_all_reps(squat1)
    squat2 = analyze_all_reps(squat2)
    
    errors = [(squat1[key] - squat2[key]) ** 2 for key in squat1]
    mse = np.mean(errors)
    return mse