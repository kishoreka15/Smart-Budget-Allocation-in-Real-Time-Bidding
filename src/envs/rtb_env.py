import gymnasium as gym  # Updated to Gymnasium
import numpy as np
import pandas as pd
from gymnasium import spaces

class RTBEnv(gym.Env):
    def __init__(self, data, total_budget=1000, penalty=0.1):
        self.data = data
        self.total_budget = total_budget
        self.penalty = penalty
        self.num_slots = len(data)
        self.current_slot = 0
        self.remaining_budget = total_budget
        self.avg_ctr = 0
        
        # State: [time_slot, remaining_budget, traffic_volume, avg_ctr]
        self.observation_space = spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32)
        # Action: bid multiplier (0-1)
        self.action_space = spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32)
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_slot = 0
        self.remaining_budget = self.total_budget
        self.avg_ctr = 0
        return self._get_state(), {}
    
    def _get_state(self):
        time_slot = self.current_slot / self.num_slots
        rem_budget = self.remaining_budget / self.total_budget
        traffic = self.data.iloc[min(self.current_slot, self.num_slots - 1)]['traffic_volume']  # Prevent out-of-bounds
        return np.array([time_slot, rem_budget, traffic, self.avg_ctr])
    
    def step(self, action):
        multiplier = action[0]
        allocated_budget = multiplier * self.remaining_budget
        slot_data = self.data.iloc[self.current_slot]
        
        # Simulate clicks based on allocated budget and CTR (simplified model)
        potential_clicks = slot_data['impression'] * slot_data['ctr'] * (allocated_budget / slot_data['cost'].sum() if slot_data['cost'].sum() > 0 else 1)
        actual_clicks = min(potential_clicks, slot_data['click'])  # Cap at real clicks
        cost = allocated_budget  # Assume cost = allocated budget for simplicity
        
        # Update budget
        overspend = max(0, cost - self.remaining_budget)
        self.remaining_budget -= cost
        self.remaining_budget = max(0, self.remaining_budget)
        
        # Reward: clicks - penalty * overspend
        reward = actual_clicks - self.penalty * overspend
        
        # Update avg CTR
        self.avg_ctr = (self.avg_ctr * self.current_slot + slot_data['ctr']) / (self.current_slot + 1)
        
        # Increment slot after calculations
        self.current_slot += 1
        done = self.current_slot >= self.num_slots
        return self._get_state(), reward, done, False, {}