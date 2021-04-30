import gym
import random
import copy
import numpy as np
from account import *


class TradingEnvDiscrete(gym.Env):
    def __init__(self, datafeed, window, stride, episode_length, starting_balance, trade_size):
        self.datafeed = datafeed
        self.window = window
        self.stride = stride
        self.episode_length = episode_length
        self.starting_balance = starting_balance
        self.trade_size = trade_size
        self.action_space = gym.spaces.Discrete(2) # buy / sell 1 unit
        self.observation_space = gym.spaces.Box(low=0, high=np.inf, shape=(window+3,))
        self.reward_range = (-np.inf, np.inf)
    
    def step(self, action):
        price_0 = self.datafeed[self.t:self.t+self.window][-1]
        balance_0 = self.account.total_balance
        if action == 0: # BUY
            self.account.update_position('equity', self.trade_size/price_0, price_0)
        if action == 1: # SELL
            self.account.update_position('equity', -self.trade_size/price_0, price_0)
        
        self.t += self.stride
        info = np.array([self.account.total_balance, self.account.cash_balance, self.account.positions.get('equity', [0])[0]])
        state_1 = np.insert(self.datafeed[self.t:self.t+self.window], 0, info)
        price_1 = state_1[-1]
        self.account.update_position('equity', 0, price_1)
        balance_1 = self.account.total_balance

        reward = balance_1 - balance_0
        
        self.iter += 1
        done = self.iter >= self.episode_length
        info = self.account
        
        return state_1, reward, done, info
    
    
    def reset(self):
        self.iter = 0
        self.t = random.randint(0, len(self.datafeed)-self.episode_length*self.stride - self.window)
        self.account = Account(self.starting_balance, interest=0.01)
        info = np.array([self.account.total_balance, self.account.cash_balance, self.account.positions.get('equity', [0])[0]])
        state = np.insert(self.datafeed[self.t:self.t+self.window], 0, info)
        return state
    
    def render(self):
        pass
    
    def close(self):
        pass
    
    def seed(self):
        pass


class TradingEnvContinuous(gym.Env):
    def __init__(self, datafeed, window, stride, episode_length, starting_balance):
        self.datafeed = datafeed
        self.window = window
        self.stride = stride
        self.episode_length = episode_length
        self.starting_balance = starting_balance
        self.action_space = gym.spaces.Box(low=-1, high=1, shape=(1,)) # buy / sell % of portfolio
        self.observation_space = gym.spaces.Box(low=0, high=np.inf, shape=(window+3,)) # total_balance, cash, n
        self.reward_range = (-np.inf, np.inf)
    
    def step(self, action):
        if not isinstance(action, float):
            action = action[0]
        price_0 = self.datafeed[self.t:self.t+self.window][-1]
        balance_0 = self.account.total_balance
        if action > 0:
            n = action*self.account.cash_balance/price_0
        elif action < 0:
            pos = self.account.positions.get('equity', [0])
            n = action*pos[0]
        else:
            n = 0
        self.account.update_position('equity', n, price_0)
        
        self.t += self.stride
        info = np.array([self.account.total_balance, self.account.cash_balance, self.account.positions.get('equity', [0])[0]])
        state_1 = np.insert(self.datafeed[self.t:self.t+self.window], 0, info)
        price_1 = state_1[-1]
        self.account.update_position('equity', 0, price_1)
        balance_1 = self.account.total_balance

        reward = balance_1 - balance_0
        
        self.iter += 1
        done = self.iter >= self.episode_length
        
        return state_1, reward, done, info
    
    def reset(self):
        self.iter = 0
        self.t = random.randint(0, len(self.datafeed)-self.episode_length*self.stride - self.window)
        self.account = Account(self.starting_balance, interest=None)
        info = np.array([self.account.total_balance, self.account.cash_balance, self.account.positions.get('equity', [0])[0]])
        state = np.insert(self.datafeed[self.t:self.t+self.window], 0, info)
        return state
    
    def render(self):
        pass
    
    def close(self):
        pass
    
    def seed(self):
        pass

    
class TradingEnvContinuous2(gym.Env):
    def __init__(self, datafeed, window, stride, episode_length, starting_balance):
        self.datafeed = datafeed
        self.window = window
        self.stride = stride
        self.episode_length = episode_length
        self.starting_balance = starting_balance
        self.action_space = gym.spaces.Box(low=-1, high=1, shape=(1,)) # buy / sell % of portfolio
        self.observation_space = gym.spaces.Box(low=0, high=np.inf, shape=(window,)) # total_balance, cash, n
        self.reward_range = (-np.inf, np.inf)
    
    def step(self, action):
        if not isinstance(action, float):
            action = action[0]
        price_0 = self.datafeed[self.t:self.t+self.window][-1]
        balance_0 = self.account.total_balance
        if action > 0:
            n = action*self.account.cash_balance/price_0
        elif action < 0:
            pos = self.account.positions.get('equity', [0])
            n = action*pos[0]
        else:
            n = 0
        self.account.update_position('equity', n, price_0)
        
        self.t += self.stride
#         info = np.array([self.account.total_balance, self.account.cash_balance, self.account.positions.get('equity', [0])[0]])
#         state_1 = np.insert(self.datafeed[self.t:self.t+self.window], 0, info)
        state_1 = copy.deepcopy(self.datafeed[self.t:self.t+self.window])
        price_1 = state_1[-1]
        self.account.update_position('equity', 0, price_1)
        balance_1 = self.account.total_balance

        reward = (price_1 - price_0)*action
        
        self.iter += 1
        done = self.iter >= self.episode_length
        
        return state_1, reward, done, None
    
    def reset(self):
        self.iter = 0
        self.t = random.randint(0, len(self.datafeed)-self.episode_length*self.stride - self.window)
        self.account = Account(self.starting_balance, interest=None)
#         info = np.array([self.account.total_balance, self.account.cash_balance, self.account.positions.get('equity', [0])[0]])
#         state = np.insert(self.datafeed[self.t:self.t+self.window], 0, info)
        state = copy.deepcopy(self.datafeed[self.t:self.t+self.window])
        return state
    
    def render(self):
        pass
    
    def close(self):
        pass
    
    def seed(self):
        pass
    