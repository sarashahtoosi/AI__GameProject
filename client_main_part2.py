import random
from statistics import multimode
from base import BaseAgent, Action
import numpy as np
import copy
import matplotlib.pyplot as plt


class Agent(BaseAgent):
    # effect of new values in old ones
    alpha = 0.9

    # effect of new values
    gama = 0.6

    trshld = 100
    current_location = (0 ,0)
    pre_location = (0, 0)
    pre_action = "noap"
    pre_map = []

    current_diamond = 0
    map = []
    width = 0
    height = 0
    q_table = {}
    
    first_turn = True

    action_map = {"up" : Action.UP, "down" : Action.DOWN, "left" : Action.LEFT, "right" : Action.RIGHT,
                     "downright" : Action.DOWN_RIGHT, "downleft" : Action.DOWN_LEFT,"upleft" : Action.UP_LEFT,
                     "upright" : Action.UP_RIGHT, "noap" : Action.NOOP}
    actions_moves = {"up":(-1 ,0), "down":(1 ,0), "right":(0 ,1), "left":(0 ,-1), "upleft":(-1 ,-1),
                         "upright":(-1 ,1), "downleft":(1 ,-1), "downright":(1 ,1) }#, "noap":(0 ,0)

    element_reward = {'E':0, '*':-25, 'G':0, 'R':0, 'Y':0, 'g':0, 'r':0, 'y':0, 'T':100}
    
    
    diamond_score = {0: [50, 0, 0, 0],
                    1: [50, 200, 100, 0], 
                    2: [100, 50, 200, 100], 
                    3: [50, 100, 50, 200], 
                    4: [250, 50, 100, 50]
                    }

    def do_turn(self) -> Action:
        self.map = self.grid
        self.width = len(self.map)
        self.height = len(self.map[0])
        
        def q_init():
            for i in range(self.width):
                for j in range(self.height):
                    self.q_table[(i,j)] = {0:{"dummy":0},
                                    1:{"dummy":0},
                                    2:{"dummy":0},
                                    3:{"dummy":0},
                                    4:{"dummy":0}}
        
        def seen_init():
            seen_state = []
            holes = []
            diamonds = []
            for i in range(self.width):
                seen_state.append([])
            
            for i in range(self.width):
                for j in range(self.height):
                    seen_state[i].append(1)
                    if self.map[i][j] in ['1', '2', '3', '4']:
                        diamonds.append((i, j))
                    if self.map[i][j] == 'T':
                        holes.append((i, j))
            return seen_state, holes, diamonds

        def probs(state, seen_state):
            probs = []
            act = []
            max_seen_val = -1
            
            for i in self.actions_moves:
                x, y = state[0] + self.actions_moves[i][0], state[1] + self.actions_moves[i][1]
                if x < self.width and x >= 0 and y < self.height and y >= 0 and self.map[x][y] != 'W':
                    probs.append(1/seen_state[x][y])
                    act.append(i)
                    if seen_state[x][y] > max_seen_val:
                        max_seen_val = seen_state[x][y]

            max_seen_val *= 100
            for i in range(len(probs)):
                probs[i] *= max_seen_val
            
            return act, probs

        def set_keydoor_values():
            for w in ['g','r','y']:
                m_score = 0
                for i in range(self.width):
                    for j in range(self.height):
                        if self.map[i][j] != w:
                            continue
                        score = 0
                        for n in range(-1,2):
                            if i+n >= 0 and i+n <= self.width-1 :
                                if self.map[i+n][j] == 'W':
                                    score += 100
                        for m in range(-1,2):
                            if i+m >= 0 and i+m <= self.height-1 :
                                if self.map[i][j+m] == 'W':
                                    score += 100
                        if m_score < score:
                            m_score = score
                self.element_reward[w] = m_score
        
        def do_state(state):
            if self.map[state[0]][state[1]] == 'T':
                action = random.choice(list(self.actions_moves.keys()))
            else:
                action = max(self.q_table[state][self.current_diamond], key = self.q_table[state][self.current_diamond].get)
                arr = []
                arr.append(action)
                for i in self.q_table[state][self.current_diamond]:
                    if self.q_table[state][self.current_diamond][action] == self.q_table[state][self.current_diamond][i]:
                        arr.append(i)
                
                action = random.choice(arr)

                if action == "dummy":
                    action = random.choice(list(self.actions_moves.keys()))
                
            return action

        def select_action(state, multiplier, seen_state):
            if random.uniform(0, 100) < self.trshld * multiplier:
                a, p = probs(state, seen_state)
                action = random.choices(a, weights=p)[0]
            else:
                action = max(self.q_table[state][self.current_diamond], key = self.q_table[state][self.current_diamond].get)
                arr = []
                arr.append(action)
                for i in self.q_table[state][self.current_diamond]:
                    if self.q_table[state][self.current_diamond][action] == self.q_table[state][self.current_diamond][i]:
                        arr.append(i)
                
                action = random.choice(arr)

                if action == "dummy":
                    action = random.choice(list(self.actions_moves.keys()))
                
            return action

        def get_reward(state, next_state, action, reward, total_reward):
            x = abs(state[0] - next_state[0])
            y = abs(state[1] - next_state[1])

            reward = -1
            if x+y <= 2:
                reward -= x + y
                total_reward -= x + y
            
            a_x = state[0] + self.actions_moves[action][0]
            a_y = state[1] + self.actions_moves[action][1]

            if a_x < 0 or a_y < 0 or a_y >= self.height or a_x >= self.width or self.map[a_x][a_y] == 'W':
                reward -= 10000

            ns_x = next_state[0]
            ns_y = next_state[1]

            if self.map[ns_x][ns_y] in self.element_reward.keys():
                reward += self.element_reward[self.map[ns_x][ns_y]] * 10
            elif self.map[ns_x][ns_y] in ['1','2','3','4']:
                tmp = self.diamond_score[self.current_diamond][int(self.map[ns_x][ns_y]) - 1] 
                total_reward += tmp
                reward += tmp * 10

            return reward, total_reward

        def remove_obj(x, y, multiplier, diamonds):
            if self.map[x][y] in ['1','2','3','4']:
                tmp = self.map[x][y]
                self.map[x][y] = 'E'
                multiplier = calculate_epsilon(diamonds)
                return int(tmp), multiplier
            elif self.map[x][y] in ['g','r','y']:
                self.element_reward[self.map[x][y].upper()] = self.element_reward[self.map[x][y]]
                self.map[x][y] = 'E'
            return self.current_diamond, multiplier

        def do_action(loc, action, keys):
            x,y = loc[0] + self.actions_moves[action][0] ,loc[1] + self.actions_moves[action][1]
            if x >= self.width or x < 0 or y >= self.height or y < 0 or self.map[x][y] == 'W':
                return loc
            elif self.map[x][y] in ["G","R","Y"]:
                if keys[self.map[x][y].lower()] == 0:
                    return loc
                else:
                    self.map[x][y] = 'E'
            elif self.map[x][y] in ["g","r","y"]:
                keys[self.map[x][y]] = 1
            return (x,y)

        def q_update(S, A, R, SS):
            tmp_k = self.q_table[S][self.current_diamond].keys()
            if A not in tmp_k:
                self.q_table[S][self.current_diamond][A] = 0
                if "dummy" in tmp_k:
                    del self.q_table[S][self.current_diamond]['dummy']
            if self.map[S[0]][S[1]] == 'T':
                return

            self.q_table[S][self.current_diamond][A] = round(self.q_table[S][self.current_diamond][A] + self.alpha * 
                                                        (R + self.gama * np.max(list(self.q_table[SS][self.current_diamond].values()))
                                                         - self.q_table[S][self.current_diamond][A]), 4)
        
        def finished():
            for i in range(self.width):
                for j in range(self.height):
                    if self.map[i][j] in ['1','2','3','4']:
                        return False
            return True

        def count_E(x):
            w = 0
            for i in range(x):
                for j in range(self.height):
                    if self.map[i][j] == 'W':
                        w += 1
            return x * self.height - w

        def calculate_alpha():
            for i in range(self.width-1,-1,-1):
                for j in range(self.height-1,-1,-1):
                    if self.map[i][j] in ['1','2','3','4']:
                        return (count_E(i)) / ( self.width * self.height )

        def calculate_epsilon(diamonds):
            mn_distance = np.Infinity
            save = 0
            for i in diamonds:
                distance = abs(i[0] - self.current_location[0]) + abs(i[1] - self.current_location[1])
                if mn_distance > distance:
                    mn_distance = distance
                    save = i

            diamonds.remove(save)

            if 30 < mn_distance <= 40:
                return 11/8
            elif 20 < mn_distance <= 30:
                return 10/8
            elif 15 < mn_distance <= 20:
                return  9/8
            elif 10 < mn_distance <= 15:
                return 1
            else:
                return 7/8

        def find_char():
            for i in range(self.width):
                for j in range(self.height):
                    if 'A' in self.map[i][j]:
                        self.current_location = (i, j)
                        return

        def learn():
            save_grid = copy.deepcopy(self.grid)

            seen_state, holes, diamonds = seen_init()
            holes.append(self.current_location)
            set_keydoor_values()
            q_init()
            
            epoch = 10000
            self.trshld = 100 # epsilon
            max_epoch = 500
            counter = 0

            sv_diamonds = copy.deepcopy(diamonds)

            each_hole_round = round(epoch/len(holes))
            sub_trshd = round((self.trshld*90/100)/epoch, 6)
            multiplier = calculate_epsilon(diamonds)
            self.alpha = round(calculate_alpha(), 4)

            number_of_init_rounds = 100
            if self.max_turn_count > 100:
                number_of_init_rounds = self.max_turn_count
            
            score_list = []
            mx_score = 0

            for hole in holes:
                self.trshld = 100
                for __ in range(each_hole_round):
                    self.map = copy.deepcopy(save_grid)
                    diamonds = copy.deepcopy(sv_diamonds)

                    self.current_location = hole
                    reward = 0
                    sv_score = 0
                    self.current_diamond = 0
                    keys = {'g':0,'r':0,'y':0}

                    for _ in range(number_of_init_rounds):
                        if finished():
                            break

                        action = select_action(self.current_location, multiplier, seen_state)
                        
                        location = do_action(self.current_location, action, keys)        
                        
                        reward, sv_score = get_reward(self.current_location, location, action, reward, sv_score)
                        
                        next_diamond, multiplier = remove_obj(location[0], location[1], multiplier, diamonds)
                        
                        q_update(self.current_location, action, reward, location)
                        
                        self.current_diamond = next_diamond
                        self.current_location = location
                        seen_state[location[0]][location[1]] += 1
                        
                    if mx_score <= sv_score:
                        counter += 1
                        mx_score = sv_score
                        if counter == max_epoch:
                            break
                    
                    self.trshld -= sub_trshd
                    score_list.append(sv_score)
            plt.plot(score_list)

            plt.show()
            
        def do():
            if finished():
                return "noap"

            self.trshld = 0
            reward = 0

            if self.first_turn:
                action = do_state(self.current_location)
                self.pre_location = self.current_location
                self.pre_action = action
                self.pre_map = copy.deepcopy(self.grid)
                self.first_turn = False
                return action
            
            x, y = self.current_location[0], self.current_location[1]
            new_diamond = self.current_diamond

            q_update(self.pre_location, self.pre_action, reward, self.current_location)
            
            self.q_table[self.pre_location][self.current_diamond][self.pre_action] -= 50

            if self.pre_map[x][y] in ['1','2','3','4']:
                reward = self.diamond_score[self.current_diamond][int(self.pre_map[x][y])-1] * 10
                new_diamond = int(self.pre_map[x][y])
            elif self.pre_map[x][y] in self.element_reward.keys():
                reward = self.element_reward[self.pre_map[x][y]]
            
            action = do_state(self.current_location)

            self.pre_action = action
            self.current_diamond = new_diamond
            self.pre_location = self.current_location
            self.pre_map = copy.deepcopy(self.grid)

            return action
        
        
        if self.turn_count == 1:
            print("learn")
            learn()
            print("learning is finished")
            
            self.trshld = 0
            self.current_diamond = 0
        else:
            find_char()
        return self.action_map[do()]

if __name__ == '__main__':
    data = Agent().play()
    print("FINISH : ", data)