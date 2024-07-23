from game import PingPong
from agents.human_agent import Agent as HumanAgent
from agents.hard_coded_agent import Agent as HardCodedAgent
from agents.defense_agent import Agent as DefenseAgent
from agents.general_agent import Agent as GeneralAgent
import os


def run(left_agent, right_agent):
    game = PingPong()
    left_agent_record = 0
    right_agent_record = 0

    iteration = 0
    while True:
        iteration += 1

        left_state = left_agent.get_state(game)
        left_action = left_agent.get_action(left_state)

        right_state = right_agent.get_state(game)
        right_action = right_agent.get_action(right_state)

        left_reward, right_reward, done, left_score, right_score = game.play_step(left_action, right_action)

        if left_agent.mode == 'train':
            left_new_state = left_agent.get_state(game)
            left_agent.remember(left_state, left_action, left_reward, left_new_state, done)

            if iteration % 4 == 0:
                left_agent.train_long_memory()

            if iteration % 10000 == 0:
                left_agent.model.save(file_name='left_agent.pth')

        if right_agent.mode == 'train':
            right_new_state = right_agent.get_state(game)
            right_agent.remember(right_state, right_action, right_reward, right_new_state, done)

            if iteration % 4 == 0:
                right_agent.train_long_memory()

            if iteration % 10000 == 0:
                right_agent.model.save(file_name='right_agent.pth')

        if done:
            game.reset()
            left_agent.n_games += 1
            right_agent.n_games += 1

            if left_score > left_agent_record:
                left_agent_record = left_score
            if right_score > right_agent_record:
                left_agent_record = right_score

            print('iter', iteration, 'Game', left_agent.n_games, f'Score: {left_score}:{right_score}',
                  f'Record: {left_agent_record}:{right_agent_record}')


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    # left_model_path = os.path.join(local_dir, 'models/left_agent.pth')
    left_model_path = os.path.join(local_dir, 'models/defense_model_v1.pth')
    # left_model_path = None
    right_model_path = os.path.join(local_dir, 'models/defense_model_v1.pth')
    # right_model_path = os.path.join(local_dir, 'models/right_agent.pth')

    left_agent = HumanAgent(side='left')
    # left_agent = HardCodedAgent(side='left')
    # left_agent = DefenseAgent(side='left', model_path=left_model_path, mode='play')
    # left_agent = GeneralAgent(side='left', model_path=left_model_path, mode='play')

    # right_agent = HumanAgent(side='right')
    # right_agent = HardCodedAgent(side='right')
    right_agent = DefenseAgent(side='right', model_path=right_model_path, mode='play')
    # right_agent = GeneralAgent(side='right', model_path=right_model_path, mode='play')

    run(left_agent, right_agent)
