from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from src.envs.rtb_env import RTBEnv
import pandas as pd
import os

def train_drl(data, total_episodes=100):  # Reduced for testing
    os.makedirs('results', exist_ok=True)
    env = make_vec_env(lambda: RTBEnv(data), n_envs=1)
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003, n_steps=2048, batch_size=64, n_epochs=10)
    model.learn(total_timesteps=total_episodes * 24)  # 24 steps per episode
    model.save("results/ppo_rtb_model")
    return model

if __name__ == "__main__":
    data = pd.read_csv('data/processed_ipinyou.csv')
    model = train_drl(data)
    print("Model trained and saved.")