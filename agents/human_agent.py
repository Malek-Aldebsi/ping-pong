import pygame
import numpy as np


class Agent:
    def __init__(self, side):
        self.side = side
        self.mode = 'play'

        self.n_games = 0

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

    def get_action(self, state):
        keys = pygame.key.get_pressed()
        if self.side == 'left':
            action = [keys[pygame.K_w], not keys[pygame.K_w] and not keys[pygame.K_s], keys[pygame.K_s]]
        else:
            action = [keys[pygame.K_UP], not keys[pygame.K_UP] and not keys[pygame.K_DOWN], keys[pygame.K_DOWN]]
        return action
