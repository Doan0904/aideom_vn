import gymnasium as gym
from gymnasium import spaces
import numpy as np

class VietnamEconomyEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.action_space = spaces.Discrete(5)
        # 4 state variables (GDP, D, AI, U), each has 3 levels
        self.observation_space = spaces.MultiDiscrete([3, 3, 3, 3])
        self.T = 10
        self.allocation = {
            0: np.array([0.70, 0.10, 0.10, 0.10]),
            1: np.array([0.40, 0.25, 0.15, 0.20]),
            2: np.array([0.25, 0.45, 0.15, 0.15]),
            3: np.array([0.20, 0.20, 0.45, 0.15]),
            4: np.array([0.30, 0.20, 0.10, 0.40])
        }
        self.w = np.array([0.40, 0.25, 0.20, 0.15])
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.array([1, 1, 0, 1])
        self.t = 0
        self.K, self.D, self.AI, self.H = 27500, 20.3, 86, 30
        return self.state, {}
        
    def step(self, action):
        a = self.allocation[action]
        budget = 1000  # Ngân sách (nghìn tỷ)
        
        self.K += a[0] * budget
        self.D += a[1] * budget / 100
        self.AI += a[2] * budget / 20
        self.H += a[3] * budget / 200
        
        # Hàm sản xuất
        Y = (self.K**0.33) * (54.0**0.42) * (self.D**0.10) * (self.AI**0.08) * (self.H**0.07)
        
        reward = (Y / 10000) * self.w[0] # Reward giả lập đơn giản hóa
        
        self.t += 1
        done = self.t >= self.T
        
        return self.state, reward, done, False, {}