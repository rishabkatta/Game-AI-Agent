
'''
@author-name: Rishab Katta
@author-name: Akhil Karrothu

Game AI Agent for achieving a high score on Atari Berzerk - Agent 2
'''
import argparse
import sys
import pdb
import traceback
import gym
from gym import wrappers, logger
from queue import PriorityQueue

ACTION_MEANING = {
    0: "NOOP",
    1: "FIRE",
    2: "UP",
    3: "RIGHT",
    4: "LEFT",
    5: "DOWN",
    6: "UPRIGHT",
    7: "UPLEFT",
    8: "DOWNRIGHT",
    9: "DOWNLEFT",
    10: "UPFIRE",
    11: "RIGHTFIRE",
    12: "LEFTFIRE",
    13: "DOWNFIRE",
    14: "UPRIGHTFIRE",
    15: "UPLEFTFIRE",
    16: "DOWNRIGHTFIRE",
    17: "DOWNLEFTFIRE",
}


class Agent(object):
    __slots__ = "player_pos", "action_space", "player", "monster", "wall", "exit", "neighbours", "flag"
    """The world's simplest agent!"""

    def __init__(self, action_space):
        self.action_space = action_space
        self.player_pos = (0, 0)
        self.player = [240, 170, 103]
        self.monster = [210, 210, 64]
        self.wall = [84, 92, 214]
        self.exit = (0, 0)
        self.flag = False

    # You should modify this function
    def act(self, observation, reward, done):
        # print(observation.shape)
        """for _ in range(observation.shape[0]):
            for i in range(observation.shape[1]):
                print(observation[_][i], end= "")
            print("\n")"""

        self.get_monster_color(observation)

        self.find_person_loc(observation)
        self.find_exit_node(observation)
        move = self.look_around(observation)
        print(move)
        return move

    def get_monster_color(self, game):
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

        self.monster = colors[0] if len(colors) >= 1 else None

    def find_exit_node(self, game):
        """

        :return:
        """
        self.exit = (5, game.shape[1] // 2)

    def heuristic(self, position):
        """

        :param position:
        :return:
        """
        return abs(self.exit[0] - position[0]) + abs(self.exit[1] - position[1])

    def get_direction(self, g):
        """

        :return:
        """
        dist = 10
        pq = PriorityQueue()
        leg = self.player_pos[0] + 25

        # best Direction to move
        pq.put((self.heuristic((self.player_pos[0] - 1, self.player_pos[1])), 'up'))
        pq.put((self.heuristic((self.player_pos[0] + 1, self.player_pos[1])), 'down'))
        pq.put((self.heuristic((self.player_pos[0], self.player_pos[1] - 1)), 'left'))
        pq.put((self.heuristic((self.player_pos[0], self.player_pos[1] + 1)), 'right'))

        not_safe_move = {'down': False
            , 'up': False
            , 'left': False
            , 'right': False}

        move_command = {
            "up": 2,
            "right": 3,
            "left": 4,
            "down": 5,
        }
        # move down
        safe = True
        for y in range(0, dist):
            if self.player_pos[0] + y >= 155 or list(g[self.player_pos[0] + y][self.player_pos[1]]) == self.wall:
                safe = False
                break
            if leg >= 155 or list(g[leg][self.player_pos[1]]) == self.wall:
                safe = False
                break
        if not safe:
            not_safe_move['down'] = True

        # move up
        safe = True
        for y in range(0, dist):
            if self.player_pos[0] - y <= 1 or list(g[self.player_pos[0] - y][self.player_pos[1]]) == self.wall:
                safe = False
                break
        if not safe:
            not_safe_move['up'] = True

        # move left
        safe = True
        for y in range(0, dist):
            if self.player_pos[1] - y <= 1 or list(g[self.player_pos[0]][self.player_pos[1] - y]) == self.wall:
                safe = False
                break
            if list(g[leg][self.player_pos[1] - y]) == self.wall:
                safe = False
                break

        if not safe:
            not_safe_move['left'] = True

        # move right
        safe = True
        for y in range(0, dist):
            if self.player_pos[1] + y >= 209 or list(g[self.player_pos[0]][self.player_pos[1] + y]) == self.wall:
                safe = False
                break
            if list(g[leg][self.player_pos[1] + y]) == self.wall:
                safe = False
                break

        if not safe:
            not_safe_move['right'] = True

        while (not pq.empty()):
            m = pq.get()[1]
            if not not_safe_move[m]:
                print(m)
                return move_command[m]

        return 0

    def find_person_loc(self, game):
        """

        :param game:
        :return:
        """
        row, col, depth = game.shape

        try:
            for row in range(game.shape[0]):
                if self.player in game[row].tolist():
                    for column in range(game.shape[1]):
                        if self.player == game[row][column].tolist():
                            self.player_pos = (row + 8, column + 2)
                            return
        except:
            print("Wait here")

    def look_around(self, game: object) -> object:
        """

        :param game:
        :return:
        """

        try:
            px, py = self.player_pos[0], self.player_pos[1]
            su = 10

            rw, lw, uw, dw, luw, ruw, rdw, ldw = False, False, False, False, False, False, False, False

            for i in range(30):
                # move back if monster to right
                for i in range(su):
                    if list(game[px][py - i]) == self.wall:
                        rw = True

                if list(game[px][py + i]) == self.monster and not rw:
                    self.flag = not self.flag
                    if self.flag:
                        return 4
                    else:
                        return 11

                # monster to the left
                for i in range(su):
                    if list(game[px][py + i]) == self.wall:
                        lw = True

                if list(game[px][py - 1]) == self.monster and not lw:
                    self.flag = not self.flag
                    if self.flag:
                        return 3
                    else:
                        return 12

                # monster to the top
                for i in range(su):
                    if list(game[px + i][py]) == self.wall:
                        uw = True

                if list(game[px - i][py]) == self.monster and not uw:
                    self.flag = not self.flag
                    if self.flag:
                        return 5
                    else:
                        return 10

                # monster to the bottom
                for i in range(su):
                    if list(game[px - i][py]) == self.wall:
                        dw = True

                if list(game[px + i][py]) == self.monster and not dw:
                    self.flag = not self.flag
                    if self.flag:
                        return 2
                    else:
                        return 13

                # monster to the bottom left
                for i in range(su):
                    if list(game[px - i][py + i]) == self.wall:
                        ldw = True
                if list(game[px + i][py - i]) == self.monster and not ldw:
                    self.flag = not self.flag
                    if self.flag:
                        return 6
                    else:
                        return 17

                # monster to the bottom right
                for i in range(su):
                    if list(game[px - i][py - i]) == self.wall:
                        rdw = True
                        break

                if list(game[px + i][py + i]) == self.monster and not rdw:
                    self.flag = not self.flag
                    if self.flag:
                        return 7
                    else:
                        return 16

                # monster to the up right
                for i in range(su):
                    if list(game[px + i][py - i]) == self.wall:
                        ruw = True

                if list(game[px - i][py + i]) == self.monster and not ruw:
                    self.flag = not self.flag
                    if self.flag:
                        return 9
                    else:
                        return 14

                # monster to the up left
                for i in range(su):
                    if list(game[px + i][py + i]) == self.wall:
                        luw = True

                if list(game[px - i][py - i]) == self.monster and not luw:
                    self.flag = not self.flag
                    if self.flag:
                        return 8
                    else:
                        return 15

            self.flag = False
            dist = 100
            width = 6

            # Looking above
            for r1 in range(self.player_pos[0], max(0, self.player_pos[0] - dist), -1):
                # Checking for monster
                l = [list(game[r1][self.player_pos[1] + x]) for x in range(0, width)] + [
                    list(game[r1][self.player_pos[1] - x]) for x in range(0, width)]
                if self.wall in l:
                    break
                if self.monster in l:
                    return 10

            # looking down
            for r2 in range(self.player_pos[0], min(self.player_pos[0] + dist, 209), 1):
                # Checking for monster

                # l = [list(game[r2][self.player_pos[1]+x]) for x in range(0,width)] + [list(game[r2][self.player_pos[1] - x]) for x in range(0,width)]
                l = [list(game[r2][self.player_pos[1] + x]) for x in range(0, 3)] + [
                    list(game[r2][self.player_pos[1] - x]) for x in range(0, 3)]
                if self.wall in l:
                    break
                if self.monster in l:
                    return 13

            # looking left
            for c1 in range(self.player_pos[1], max(0, self.player_pos[1] - dist), -1):
                # Checking for monster
                l = [list(game[self.player_pos[0] + x][c1]) for x in range(0, width)] + [
                    list(game[self.player_pos[0] - x][c1]) for x in range(0, width)]
                if self.wall in l:
                    break
                if self.monster in l:
                    return 12

            # looking right
            for c2 in range(self.player_pos[1], min(self.player_pos[1] + dist, 159), 1):
                # Checking for monster
                l = [list(game[self.player_pos[0] + x][c2]) for x in range(0, width)] + [
                    list(game[min(self.player_pos[0] - x, 0)][c2]) for x in range(0, width)]
                if self.wall in l:
                    break
                if self.monster in l:
                    return 11

            ####################

            # Looking above left
            for r1 in range(px, max(0, py - dist), -1):
                # Checking for monster
                l = [list(game[r1 - x][py - x]) for x in range(0, width)]
                if self.wall in l:
                    break
                if self.monster in l:
                    return 15

            for r2 in range(px, min(px + dist, 209), 1):
                # Checking for monster above right
                l = [list(game[r2 - x][py + x]) for x in range(0, width)]
                if self.wall in l:
                    break
                if self.monster in l:
                    return 14

            for c1 in range(py, max(0, py - dist), -1):
                # Checking for monster left bottom
                l = [list(game[px + x][c1 - x]) for x in range(0, width)]
                if self.wall in l:
                    break
                if self.monster in l:
                    return 17

            for c2 in range(py, min(py + dist, 159), 1):
                # Checking for monster right bottom
                l = [list(game[min(px + x, 209)][min(c2 + x, 159)]) for x in range(0, width)]
                if self.wall in l:
                    break

                if self.monster in l:
                    return 16

            # No monster near by, can walk towards the exit
            return self.get_direction(game)

        except Exception as e:
            print(e)
            traceback.print_exc()
            return 0


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