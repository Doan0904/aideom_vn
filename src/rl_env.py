import gymnasium as gym
from gymnasium import spaces
import numpy as np

class VietnamEconomyEnv(gym.Env):
    """
    Môi trường Gymnasium mô phỏng quyết định phân bổ ngân sách kinh tế của Việt Nam.
    Trạng thái: [Ngưỡng K, Ngưỡng D, Ngưỡng AI, Ngưỡng H] (0=Thấp, 1=Trung bình, 2=Cao).
    Hành động: Chọn 1 trong 5 kịch bản phân bổ.
    Phần thưởng: Dựa trên GDP, Unemployment, Cyber Risk và Emission.
    """
    def __init__(self):
        super().__init__()
        self.action_space = spaces.Discrete(5)
        # State: K, D, AI, H (mỗi biến có 3 mức: Thấp, Trung bình, Cao)
        self.observation_space = spaces.MultiDiscrete([3, 3, 3, 3])
        self.T = 10
        self.allocation = {
            0: np.array([0.70, 0.10, 0.10, 0.10]),
            1: np.array([0.40, 0.25, 0.15, 0.20]),
            2: np.array([0.25, 0.45, 0.15, 0.15]),
            3: np.array([0.20, 0.20, 0.45, 0.15]),
            4: np.array([0.30, 0.20, 0.10, 0.40])
        }
        # Trọng số reward: GDP (0.5), Unemployment (-0.2), CyberRisk (-0.15), Emission (-0.15)
        self.w = np.array([0.50, -0.20, -0.15, -0.15])
        
        self.state = None
        self.t = 0
        self.K = self.D = self.AI = self.H = 0
        self.Y_prev = 0

    def reset(self, seed=None, options=None):
        """Khởi tạo lại môi trường."""
        super().reset(seed=seed)
        self.t = 0
        self.K, self.D, self.AI, self.H = 27500, 20.3, 86, 30
        self.Y_prev = self._calc_Y()
        self.state = self._get_discrete_state()
        return self.state, {}

    def _calc_Y(self):
        return (self.K**0.33) * (54.0**0.42) * (self.D**0.10) * (self.AI**0.08) * (self.H**0.07)

    def _get_discrete_state(self):
        """Discretize giá trị liên tục thành 3 mức [0, 1, 2]."""
        s_K = 0 if self.K < 30000 else (1 if self.K < 35000 else 2)
        s_D = 0 if self.D < 25 else (1 if self.D < 35 else 2)
        s_AI = 0 if self.AI < 100 else (1 if self.AI < 150 else 2)
        s_H = 0 if self.H < 35 else (1 if self.H < 45 else 2)
        return np.array([s_K, s_D, s_AI, s_H])

    def get_state_label(self, state: np.ndarray) -> str:
        """Dịch mảng trạng thái rời rạc thành string mô tả."""
        levels = {0: "low", 1: "mid", 2: "high"}
        return f"K:{levels[state[0]]} | D:{levels[state[1]]} | AI:{levels[state[2]]} | H:{levels[state[3]]}"

    def render(self, mode='human'):
        """In thông tin môi trường."""
        print(f"Bước {self.t}/{self.T} | State: {self.get_state_label(self.state)} | Y={self.Y_prev:,.1f}")

    def step(self, action):
        """Thực thi một bước thời gian, trả về trạng thái mới và reward đầy đủ."""
        a = self.allocation[action]
        budget = 1000  # Ngân sách đầu tư mỗi năm
        
        self.K += a[0] * budget
        self.D += a[1] * budget / 100
        self.AI += a[2] * budget / 20
        self.H += a[3] * budget / 200
        
        Y_new = self._calc_Y()
        delta_gdp = (Y_new - self.Y_prev) / self.Y_prev
        
        # Mô phỏng các chỉ số khác dựa trên đầu tư
        unemployment_risk = (a[1] + a[2]) * 0.8 - (a[3] * 1.5)  # Tech cao -> rủi ro việc làm, H cao -> giảm rủi ro
        cyber_risk = (self.D + self.AI) / 300  # Rủi ro an ninh mạng tăng theo D & AI
        emission = (self.K) / 40000  # Rủi ro phát thải phụ thuộc vào K

        # Normalize thành phần về khoảng [-1, 1] hoặc [0, 1]
        norm_delta_gdp = np.clip(delta_gdp * 10, 0, 1)
        norm_unemp = np.clip(unemployment_risk, -1, 1)
        norm_cyber = np.clip(cyber_risk, 0, 1)
        norm_emission = np.clip(emission, 0, 1)
        
        reward = (norm_delta_gdp * self.w[0] + 
                  norm_unemp * self.w[1] + 
                  norm_cyber * self.w[2] + 
                  norm_emission * self.w[3])
        
        self.Y_prev = Y_new
        self.state = self._get_discrete_state()
        self.t += 1
        done = self.t >= self.T
        
        return self.state, float(reward), done, False, {}

# TEST SCRIPT (chạy trực tiếp để verify)
if __name__ == "__main__":
    env = VietnamEconomyEnv()
    obs, _ = env.reset()
    print("Init state:", env.get_state_label(obs))
    total_r = 0
    for t in range(10):
        a = env.action_space.sample()
        obs, r, done, _, _ = env.step(a)
        print(f"t={t+1} | action={a} | state={env.get_state_label(obs)} | reward={r:.4f}")
        total_r += r
    print(f"Total reward: {total_r:.4f}")