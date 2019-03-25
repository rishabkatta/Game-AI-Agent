'''
@author-name: Rishab Katta
@author-name: Akhil Karrothu

Game AI Agent for achieving a high score on Atari Berzerk - Agent 1
'''
import argparse
import sys
# import pdb
import gym
from gym import wrappers, logger
from queue import PriorityQueue
import math


class Agent(object):
    """The world's simplest agent!"""

    __slots__ = "player_head_pos","player_leg_pos", "action_space", "player", "monster", "wall", "exit", "neighbours", "dodge_flag"

    def __init__(self, action_space):
        self.action_space = action_space
        self.player_head_pos = (0, 0)
        self.player_leg_pos = (0, 0)
        self.player = [240, 170, 103]
        self.monster = [210, 210, 64]
        self.wall = [84, 92, 214]
        self.exit = (0, 0)
        self.dodge_flag = True


    def get_monster_color(self,game):
        colors = []
        for r in range(game.shape[0]):
            for c in range(game.shape[1]):
                if list(game[r][c]) not in colors:
                    colors.append(list(game[r][c]))

        if [232, 232, 74] in colors:
            colors.remove([232, 232, 74])
        if self.wall in colors:
            colors.remove(self.wall)
        if self.player in colors:
            colors.remove(self.player)
        colors.remove([0, 0, 0])
        self.monster = colors[0] if len(colors)>= 1 else None

    def find_person_head_loc(self, game):
        """

        :param game:
        :return:
        """
        try:
            for row in range(game.shape[0]):
                if self.player in game[row].tolist():
                    for column in range(game.shape[1]):
                        if self.player == game[row][column].tolist():
                            self.player_head_pos = (row +1 , column+1)
                            return

        except:
            print("unable to find person")

    def find_person_leg_loc(self, game):
        """

        :param game:
        :return:
        """
        try:
            neck = 10
            for row in range(self.player_head_pos[0],game.shape[0]):
                if self.player not in game[row].tolist():
                    self.player_leg_pos = (row, self.player_head_pos[1] + 5)
                    neck -=1
                    if neck ==0:
                        return
        except Exception as e:
            print("unable to find person leg")
            print(e)

    def get_sorrounding_vertices(self, radius):
        diag_search_width = 50
        # Left_vertices
        left= set()
        for rows in range(self.player_head_pos[0], self.player_leg_pos[0]):
            if self.player_head_pos[1]- radius < 0:
                break
            left.add((rows,self.player_head_pos[1] - radius))

        # right_vertices
        right = set()
        for rows in range(self.player_head_pos[0], self.player_leg_pos[0]):
            if self.player_head_pos[1] + radius < 159:
                right.add((rows, self.player_head_pos[1] + radius))

        # UP_vertices
        up = set()
        for cols in range(self.player_head_pos[1], self.player_leg_pos[1]):
            if self.player_head_pos[0] - radius < 0:
                break
            up.add((self.player_head_pos[0] - radius, cols))

        # down_vertices
        down = set()
        for cols in range(self.player_leg_pos[1], self.player_leg_pos[1]+5):
            if self.player_leg_pos[0] + radius < 209:
                down.add((self.player_leg_pos[0] + radius, cols))

        #up_left
        up_left = set()
        down_left = set()
        up_right = set()
        down_right = set()
        x = (self.player_head_pos[0] + self.player_leg_pos[0])//2
        y = (self.player_head_pos[1] + self.player_leg_pos[1])//2
        for cols in range(diag_search_width):
            try:
                if x - cols > 0 and y-cols > 0:
                    up_left.add((x - cols, y- cols))
                if x + cols < 209 and y - cols > 0:
                    down_left.add((x + cols, y - cols))
                if x - cols > 0 and y + cols < 159:
                    up_right.add((x - cols, y + cols))
                if x + cols < 209 and cols + y < 159:
                    down_right.add((x + cols, y + cols))
            except:
                pass
        #returning all the vertices
        return [left,right,up,down,up_left,up_right,down_left,down_right]

    def look_monster(self, game):
        found_wall = {'down': False
            ,'up': False
            ,'left': False
            ,'right': False,
            "UPRIGHT": False,
            "UPLEFT": False,
            "DOWNRIGHT": False,
            "DOWNLEFT": False
            }
        for r in range(100):
            vertices = self.get_sorrounding_vertices(r)

            # Looking left for monster
            for left_v in vertices[0]:
                if list(game[left_v[0]][left_v[1]]) == self.wall:
                    found_wall['left'] = True
                    break
                if not found_wall['left'] and list(game[left_v[0]][left_v[1]]) == self.monster and not self.dodge_flag:
                    # Shoot left
                    self.dodge_flag = not self.dodge_flag
                    return 12
                if not found_wall['DOWNRIGHT'] and list(game[left_v[0]][left_v[1]]) == self.monster and self.dodge_flag:
                    self.dodge_flag = not self.dodge_flag
                    return self.decidemove(game)

                # Looking right for monster
                for v in vertices[1]:
                    # print(list(game[v[0]][v[1]]), " monster :", self.monster)
                    if list(game[v[0]][v[1]]) == self.wall:
                        found_wall['right'] = True
                        break
                    if not found_wall['right'] and list(game[v[0]][v[1]]) == self.monster and not self.dodge_flag:
                        # Shoot right
                        self.dodge_flag = not self.dodge_flag
                        return 11
                    if not found_wall['right'] and list(game[v[0]][v[1]]) == self.monster and self.dodge_flag:
                        print("I am dodging bullet")
                        self.dodge_flag = not self.dodge_flag
                        return self.decidemove(game)

                # Looking up for monster
                for v in vertices[2]:
                    if list(game[v[0]][v[1]]) == self.wall:
                        found_wall['up'] = True
                        break
                    if not found_wall['up'] and list(game[v[0]][v[1]]) == self.monster and not self.dodge_flag:
                        # Shoot up
                        self.dodge_flag = not self.dodge_flag
                        return 10
                    if not found_wall['up'] and list(game[v[0]][v[1]]) == self.monster and self.dodge_flag:
                        self.dodge_flag = not self.dodge_flag
                        return self.decidemove(game)

                # Looking down for monster
                for v in vertices[3]:
                    if list(game[v[0]][v[1]]) == self.wall:
                        found_wall['down'] = True
                        break
                    if not found_wall['down'] and list(game[v[0]][v[1]]) == self.monster and not self.dodge_flag:
                        # Shoot down
                        self.dodge_flag = not self.dodge_flag
                        return 13
                    if not found_wall['down'] and list(game[v[0]][v[1]]) == self.monster and self.dodge_flag:
                        self.dodge_flag = not self.dodge_flag
                        return self.decidemove(game)

                # Looking up left for monster
                for v in vertices[4]:
                    if list(game[v[0]][v[1]]) == self.wall:
                        found_wall['UPLEFT'] = True
                        break
                    if not found_wall['UPLEFT'] and list(game[v[0]][v[1]]) == self.monster and not self.dodge_flag:
                        # Shoot up left
                        self.dodge_flag = not self.dodge_flag
                        return 15
                    if not found_wall['left'] and list(game[v[0]][v[1]]) == self.monster and self.dodge_flag:
                        self.dodge_flag = not self.dodge_flag
                        return self.decidemove(game)

                # Looking up right for monster
                for v in vertices[5]:
                    if list(game[v[0]][v[1]]) == self.wall:
                        found_wall['UPRIGHT'] = True
                        break
                    if not found_wall['UPRIGHT'] and list(game[v[0]][v[1]]) == self.monster and not self.dodge_flag:
                        # Shoot up left
                        self.dodge_flag = not self.dodge_flag
                        return 14
                    if not found_wall['UPRIGHT'] and list(game[v[0]][v[1]]) == self.monster and self.dodge_flag:
                        self.dodge_flag = not self.dodge_flag
                        return self.decidemove(game)

                # Looking down right for monster
                for v in vertices[7]:
                    if list(game[v[0]][v[1]]) == self.wall:
                        found_wall['DOWNRIGHT'] = True
                        break
                    if not found_wall['DOWNRIGHT'] and list(
                            game[v[0]][v[1]]) == self.monster and not self.dodge_flag:
                        # Shoot up left
                        self.dodge_flag = not self.dodge_flag
                        return 16
                    if not found_wall['DOWNRIGHT'] and list(game[v[0]][v[1]]) == self.monster and self.dodge_flag:
                        self.dodge_flag = not self.dodge_flag
                        return self.decidemove(game)

                # Looking down left for monster
                for v in vertices[6]:
                    if list(game[v[0]][v[1]]) == self.wall:
                        found_wall['DOWNLEFT'] = True
                        break
                    if not found_wall['DOWNLEFT'] and list(game[v[0]][v[1]]) == self.monster and not self.dodge_flag:
                        # Shoot up left
                        self.dodge_flag = not self.dodge_flag
                        return 17
                    if not found_wall['DOWNLEFT'] and list(game[v[0]][v[1]]) == self.monster and self.dodge_flag:
                        self.dodge_flag = not self.dodge_flag
                        return self.decidemove(game)





        #print("deciding move")
        return self.decidemove(game)

    def decidemove(self, game):

        not_safe_move = {'down' : False
        ,'up' : False
        ,'left' : False
        ,'right' : False,
        "UPRIGHT": False,
        "UPLEFT": False,
        "DOWNRIGHT": False,
        "DOWNLEFT": False
                         }

        move_command = {
            "up": 2,
            "right": 3,
            "left": 4,
            "down": 5,
            "UPRIGHT":6,
            "UPLEFT":7,
            "DOWNRIGHT":8,
            "DOWNLEFT":9
        }

        pq = PriorityQueue()

        sorroundings = [(self.player_head_pos[0] - 2, self.player_head_pos[1]),
                        (self.player_leg_pos[0] + 2, self.player_leg_pos[1]),
                        (self.player_head_pos[0], self.player_head_pos[1] - 2),
                        (self.player_head_pos[0], self.player_head_pos[1] + 2),
                        (self.player_head_pos[0] - 1, self.player_head_pos[1] + 1),
                        (self.player_head_pos[0] - 1, self.player_head_pos[1] - 1),
                        (self.player_leg_pos[0] + 1, self.player_leg_pos[1] + 1),
                        (self.player_leg_pos[0] + 1, self.player_leg_pos[1] - 1)]

        # best Direction to move
        pq.put((self.heuristic(sorroundings[0]), 'up'))
        pq.put((self.heuristic(sorroundings[1]), 'down'))
        pq.put((self.heuristic(sorroundings[2]), 'left'))
        pq.put((self.heuristic(sorroundings[3]), 'right'))
        #pq.put((self.heuristic(sorroundings[4]), 'UPRIGHT'))
        #pq.put((self.heuristic(sorroundings[5]), 'UPLEFT'))
        #pq.put((self.heuristic(sorroundings[6]), 'DOWNRIGHT'))
        #pq.put((self.heuristic(sorroundings[7]), 'DOWNLEFT'))

        for r in range(12):
            moves = self.get_sorrounding_vertices(r)
            # Looking left for the wall or monster
            for v in moves[0]:
                if list(game[v[0]][v[1]]) == self.wall:
                    not_safe_move['left'] = True
                    break
            for v in moves[1]:
                if list(game[v[0]][v[1]]) == self.wall:
                    not_safe_move['right'] = True
                    break
            for v in moves[2]:
                if list(game[v[0]][v[1]]) == self.wall:
                    not_safe_move['up'] = True
                    break
            for v in moves[3]:
                if list(game[v[0]][v[1]]) == self.wall:
                    not_safe_move['down'] = True
                    break
            for v in moves[4]:
                if list(game[v[0]][v[1]]) == self.wall:
                    not_safe_move['UPLEFT'] = True
                    break
            for v in moves[5]:
                if list(game[v[0]][v[1]]) == self.wall:
                    not_safe_move['UPRIGHT'] = True
                    break
            for v in moves[6]:
                if list(game[v[0]][v[1]]) == self.wall:
                    not_safe_move['DOWNLEFT'] = True
                    break
            for v in moves[7]:
                if list(game[v[0]][v[1]]) == self.wall:
                    not_safe_move['DOWNRIGHT'] = True
                    break

        while (not pq.empty()):
            m = pq.get()[1]
            if not not_safe_move[m]:
                print(m)
                return move_command[m]
        return 0

    def heuristic(self, position):
        """

        :param position:
        :return:
        """
        return abs(self.exit[0] - position[0]) + abs(self.exit[1] - position[1])

    def find_exit_node(self, game):
        """

        :return:
        """
        self.exit = (5, game.shape[1]//2)

    # You should modify this function
    def act(self, observation, reward, done):
        self.get_monster_color(observation)
        self.find_exit_node(observation)
        self.find_person_head_loc(observation)
        self.find_person_leg_loc(observation)
        move = self.look_monster(observation)
        print(move)
        return move

        #return self.action_space.sample()


## YOU MAY NOT MODIFY ANYTHING BELOW THIS LINE OR USE
## ANOTHER MAIN PROGRAM
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('--env_id', nargs='?', default='Berzerk-v0', help='Select the environment to run')
    args = parser.parse_args()

    # You can set the level to logger.DEBUG or logger.WARN if you
    # want to change the amount of output.
    logger.set_level(logger.INFO)

    env = gym.make(args.env_id)

    # You provide the directory to write to (can be an existing
    # directory, including one with existing data -- all monitor files
    # will be namespaced). You can also dump to a tempdir if you'd
    # like: tempfile.mkdtemp().
    outdir = 'random-agent-results'

    env.seed(0)
    agent = Agent(env.action_space)

    episode_count = 100
    reward = 0
    done = False
    score = 0
    special_data = {}
    special_data['ale.lives'] = 3
    ob = env.reset()
    while not done:
        action = agent.act(ob, reward, done)
        ob, reward, done, x = env.step(action)
        score += reward
        env.render()

    # Close the env and write monitor result info to disk
    print("Your score: %d" % score)
    env.close()
