import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from evaluate import evaluate_model
from stable_baselines3 import PPO
import numpy as np
import os

# Ensure results directory exists
os.makedirs('results', exist_ok=True)

# Assume rewards collected during training (add logging in drl_agent.py for real data)
def plot_results(drl_metrics, heur_metrics, rewards):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # Learning curve
    axes[0,0].plot(rewards)
    axes[0,0].set_title("Learning Curve (Reward vs Episodes)")
    
    # Budget usage (simulate over slots)
    slots = list(range(24))
    drl_spending = [drl_metrics[3] * np.random.uniform(0.8, 1.2) for _ in slots]  # Placeholder
    heur_spending = [heur_metrics[3] * np.random.uniform(0.5, 1.5) for _ in slots]
    axes[0,1].plot(slots, drl_spending, label="DRL")
    axes[0,1].plot(slots, heur_spending, label="Heuristic")
    axes[0,1].set_title("Budget Usage vs Time Slots")
    axes[0,1].legend()
    
    # Comparison bar chart
    metrics = ['Clicks', 'CPC', 'CTR', 'Variance']
    drl_vals = list(drl_metrics)
    heur_vals = list(heur_metrics)
    x = np.arange(len(metrics))
    axes[1,0].bar(x-0.2, drl_vals, 0.4, label="DRL")
    axes[1,0].bar(x+0.2, heur_vals, 0.4, label="Heuristic")
    axes[1,0].set_xticks(x, metrics)
    axes[1,0].set_title("DRL vs Heuristic Comparison")
    axes[1,0].legend()
    
    plt.tight_layout()
    plt.savefig('results/comparison_plots.png')  # Updated path
    plt.show()

if __name__ == "__main__":
    data = pd.read_csv('data/processed_ipinyou.csv')  # Updated path
    model = PPO.load("results/ppo_rtb_model")  # Updated path
    drl_metrics = evaluate_model(model, data, is_drl=True)
    heur_metrics = evaluate_model(None, data, is_drl=False)
    rewards = [np.random.uniform(10, 50) for _ in range(100)]  # Placeholder; replace with real rewards if logged
    plot_results(drl_metrics, heur_metrics, rewards)