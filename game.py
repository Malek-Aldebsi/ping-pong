import pygame

pygame.init()
font = pygame.font.SysFont('Arial', 20)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


class PingPong:
    WINNING_SCORE = 10

    def __init__(self, width=800, height=400, paddle_width=20, paddle_height=100, paddle_vel=10, puck_radius=10,
                 puck_max_vel=15, game_speed=60):
        self.width = width
        self.height = height

        self.paddle_width = paddle_width
        self.paddle_height = paddle_height
        self.paddle_vel = paddle_vel
        self.left_paddle = Paddle(10, self.height // 2 - self.paddle_height // 2, self.paddle_width, self.paddle_height,
                                  self.paddle_vel, BLUE)
        self.right_paddle = Paddle(self.width - self.paddle_width - 10, self.height // 2 - self.paddle_height // 2,
                                   self.paddle_width, self.paddle_height, self.paddle_vel, RED)

        self.puck_radius = puck_radius
        self.puck_max_vel = puck_max_vel
        self.puck = Puck(self.width // 2, self.height // 2, self.puck_radius, self.puck_max_vel, WHITE)

        self.game_speed = game_speed

        # init display
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Air Hockey')
        self.clock = pygame.time.Clock()

        # init game state
        self.left_score = 0
        self.right_score = 0
        self.left_paddle_reward = 0
        self.right_paddle_reward = 0
        
    def reset(self):
        self.reset_paddles()
        self.reset_puck()
        self.left_score = 0
        self.right_score = 0

    def reset_paddles(self):
        self.left_paddle.reset()
        self.right_paddle.reset()

    def reset_puck(self):
        self.puck.reset()

    def play_step(self, left_paddle_action, right_paddle_action):  # actions: 1 up 0 down
        self.left_paddle_reward = 0
        self.right_paddle_reward = 0
        game_over = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        if self.paddle_collision('left', left_paddle_action):
            self.left_paddle_reward = -0.1
        else:
            self.paddle_movement('left', left_paddle_action)

        if self.paddle_collision('right', right_paddle_action):
            self.right_paddle_reward = -0.1
        else:
            self.paddle_movement('right', right_paddle_action)

        puck_col = self.puck_collision()
        if puck_col != 'hit the border':
            self.puck_movement()

        if puck_col == 'left_paddle_hit_puck':
            self.left_paddle.hits += 1
            self.left_score += 1

        if puck_col == 'right_paddle_hit_puck':
            self.right_paddle.hits += 1
            self.right_score += 1

        if self.puck.x < 0:
            if self.right_paddle.hits > 0:
                self.right_paddle_reward = 3
            self.left_paddle_reward = -1
            self.left_paddle_reward += -1 * abs(self.left_paddle.y - self.puck.y) / self.height
            self.reset_paddles()
            self.reset_puck()
            game_over = True
            return self.left_paddle_reward, self.right_paddle_reward, game_over, self.left_score, self.right_score

        elif self.puck.x > self.width:
            if self.left_paddle.hits > 0:
                self.left_paddle_reward = 3
            self.right_paddle_reward = -1
            self.right_paddle_reward += -1 * abs(self.right_paddle.y - self.puck.y) / self.height
            self.reset_paddles()
            self.reset_puck()
            game_over = True
            return self.left_paddle_reward, self.right_paddle_reward, game_over, self.left_score, self.right_score

        self.update_ui()
        self.clock.tick(self.game_speed)
        return self.left_paddle_reward, self.right_paddle_reward, game_over, self.left_score, self.right_score

    def paddle_collision(self, paddle, action):
        if paddle == 'left' and action[0] and self.left_paddle.y - self.left_paddle.vel < 0:
            return True
        if paddle == 'left' and action[2] and self.left_paddle.y + self.left_paddle.vel + self.left_paddle.height > self.height:
            return True

        if paddle == 'right' and action[0] and self.right_paddle.y - self.right_paddle.vel < 0:
            return True
        if paddle == 'right' and action[2] and self.right_paddle.y + self.right_paddle.vel + self.right_paddle.height > self.height:
            return True

    def paddle_movement(self, paddle, action):  # action [up, no move, down]
        if paddle == 'left':
            if action[0]:
                self.left_paddle.move(up=True)
            elif action[2]:
                self.left_paddle.move(up=False)
            else:
                pass
        if paddle == 'right':
            if action[0]:
                self.right_paddle.move(up=True)
            elif action[2]:
                self.right_paddle.move(up=False)
            else:
                pass

    def puck_collision(self):
        # collision with top or bottom
        if self.puck.y + self.puck.radius >= self.height and self.puck.y_vel > 0:
            self.puck.y_vel *= -1
            return 'hit the border'
        elif self.puck.y - self.puck.radius <= 0 and self.puck.y_vel < 0:
            self.puck.y_vel *= -1
            return 'hit the border'

        # collision with left paddle
        if self.puck.x_vel < 0:
            if self.puck.y >= self.left_paddle.y and self.puck.y <= self.left_paddle.y + self.left_paddle.height:
                if self.puck.x - self.puck.radius <= self.left_paddle.x + self.left_paddle.width:
                    self.puck.x_vel *= -1

                    middle_y = self.left_paddle.y + self.left_paddle.height / 2
                    difference_in_y = middle_y - self.puck.y
                    reduction_factor = (self.left_paddle.height / 2) / self.puck.max_vel
                    y_vel = difference_in_y / reduction_factor
                    self.puck.y_vel = -1 * y_vel
                    return 'left_paddle_hit_puck'

        # collision with right paddle
        else:
            if self.puck.y >= self.right_paddle.y and self.puck.y <= self.right_paddle.y + self.right_paddle.height:
                if self.puck.x + self.puck.radius >= self.right_paddle.x:
                    self.puck.x_vel *= -1

                    middle_y = self.right_paddle.y + self.right_paddle.height / 2
                    difference_in_y = middle_y - self.puck.y
                    reduction_factor = (self.right_paddle.height / 2) / self.puck.max_vel
                    y_vel = difference_in_y / reduction_factor
                    self.puck.y_vel = -1 * y_vel
                    return 'right_paddle_hit_puck'

    def puck_movement(self):
        self.puck.move()

    def update_ui(self):
        self.display.fill(BLACK)

        left_score_text = font.render(f"{self.left_score}", 1, WHITE)
        right_score_text = font.render(f"{self.right_score}", 1, WHITE)
        self.display.blit(left_score_text, (self.width // 4 - left_score_text.get_width() // 2, 20))
        self.display.blit(right_score_text, (self.width * (3 / 4) - right_score_text.get_width() // 2, 20))

        self.left_paddle.draw(self.display)
        self.right_paddle.draw(self.display)

        self.puck.draw(self.display)

        pygame.display.flip()


class Paddle:

    def __init__(self, x, y, width, height, vel, color):
        self.x = self.origin_X = x
        self.y = self.origin_Y = y
        self.width = width
        self.height = height
        self.vel = vel
        self.color = color
        self.hits = 0

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        if up:
            self.y -= self.vel
        else:
            self.y += self.vel

    def reset(self):
        self.x = self.origin_X
        self.y = self.origin_Y
        self.hits = 0


class Puck:

    def __init__(self, x, y, radius, max_vel, color):
        self.x = self.origin_X = x
        self.y = self.origin_Y = y
        self.radius = radius
        self.x_vel = max_vel  # TODO check what is this velocities
        self.y_vel = 0  # TODO check what is this velocities
        self.max_vel = max_vel  # TODO for what
        self.color = color

    def draw(self, window):
        pygame.draw.circle(window, self.color, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.origin_X
        self.y = self.origin_Y
        self.y_vel = 0
        self.x_vel *= 1
        # self.x_vel = -self.max_vel