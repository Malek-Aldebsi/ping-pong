import torch
import random
import numpy as np
from collections import deque
from model import LinearQNet, QTrainer
import copy

MAX_MEMORY = 100_000
BATCH_SIZE = 32
LEARNING_RATE = 0.001  # learning rate


class Agent:
    def __init__(self, side, model_path, mode='train'):
        self.side = side
        self.mode = mode

        self.n_games = 0
        self.epsilon = 0  # tradeoff factor between exploration and exploitation
        self.gamma = 0.9  # discount rate

        self.memory = deque(maxlen=MAX_MEMORY)  # popleft if MAX_MEMORY is reached

        self.model = LinearQNet(5, 256, 3)
        if model_path is not None:
            self.model.load_state_dict(torch.load(model_path))

        self.Q_model = copy.deepcopy(self.model)

        self.trainer = QTrainer(self.model, self.Q_model, learning_rate=LEARNING_RATE, gamma=self.gamma)

    def get_state(self, game):
        if self.side == 'right':
            right_paddle_y = game.right_paddle.y
        else:
            left_paddle_y = game.left_paddle.y
        puck_x = game.puck.x
        puck_y = game.puck.y
        puck_x_vel = game.puck.x_vel
        puck_y_vel = game.puck.y_vel

        state = [
            right_paddle_y if self.side == 'right' else left_paddle_y,
            puck_x,
            puck_y,
            puck_x_vel,
            puck_y_vel
        ]
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def get_action(self, state):
        action = [0, 0, 0]  # go up, no move, go down
        if self.mode == 'play':
            _state = torch.tensor(state, dtype=torch.float)
            prediction = self.model(_state)  # ex. [0.2, 0.5, 0.3]
            predicted_action_index = torch.argmax(prediction).item()
            action[predicted_action_index] = 1
        else:
            self.epsilon = 80 - self.n_games
            if random.randint(0, 200) < self.epsilon:  # exploration
                random_action_index = random.randint(0, 2)
                action[random_action_index] = 1
            else:  # exploitation
                _state = torch.tensor(state, dtype=torch.float)
                prediction = self.model(_state)  # ex. [0.2, 0.5, 0.3]
                predicted_action_index = torch.argmax(prediction).item()
                action[predicted_action_index] = 1
        return action
