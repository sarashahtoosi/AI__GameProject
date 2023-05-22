import random
from base import BaseAgent, Action
import pandas as pd
from queue import PriorityQueue as PQ


class Agent(BaseAgent):
    pre_color = 0
    ans_list = []
    current_location = (0, 0)
    own_key = {
            'g': False,
            'r': False,
            'y': False 
        }

    def do_turn(self) -> Action:
        global_score = self.score

        elements = {1: [], 2: [], 3: [], 4: [],
                        "y": [], "r": [], "g": [],
                        "Y": [], "R": [], "G": []
                        }

        priority = {0: [1, 2, 3, 4],
                    1: [2, 3, 1, 4], 
                    2: [3, 1, 4, 2], 
                    3: [4, 2, 3, 1], 
                    4: [1, 3, 4, 2]
                    }
        diamond_score = {0: [50, 0, 0, 0],
                        1: [200, 100, 50, 0], 
                        2: [200, 100, 100, 50], 
                        3: [200, 100, 50, 50], 
                        4: [250, 100, 50, 50]
                    }

        infinit = 1000000000

        chart = self.grid

        def analysis() -> None:

            satr, soton = len(chart), len(chart[0])
            
            for i in range(satr):
                    for j in range(soton):
                        if chart[i][j] == 1 or chart[i][j] == '1':
                                elements[1].append((i, j))
                        
                        elif chart[i][j] == 2 or chart[i][j] == '2':
                                elements[2].append((i, j))
                        
                        elif chart[i][j] == 3 or chart[i][j] == '3':
                                elements[3].append((i, j))
                        
                        elif chart[i][j] == 4 or chart[i][j] == '4':
                                elements[4].append((i, j))
                        
                        elif chart[i][j] == 'G':
                                elements["G"].append((i, j))
                        
                        elif chart[i][j] == 'R':
                                elements["R"].append((i, j))

                        elif chart[i][j] == 'Y':
                                elements["Y"].append((i, j))
                        
                        elif chart[i][j] == 'g':
                                elements["g"].append((i, j))
                        
                        elif chart[i][j] == 'r':
                                elements["r"].append((i, j))
                        
                        elif chart[i][j] == 'y':
                                elements["y"].append((i, j))
    
        class way:
            steps = []
            guess = []
            score = []
            cost = []
            final_score = []

            way_steps = []

            def calculate_final_score(self):
                    tmp = 0
                    
                    for i in range(len(self.steps)):
                        tmp += (self.score[i] - self.cost[i])

                    self.final_score.append(tmp)
                    if len(self.score) > 0 and len(self.cost) > 0:
                        self.final_score.append(self.score[0] - self.cost[0])
                    
                    return self.final_score

            def step_length(self):
                    tmp = 0
                    for x in self.way_steps:
                        tmp += len(x)
                    return tmp-3

            def total_guess(self):
                    ans = 0
                    for x in self.guess:
                        ans += x
                    return ans 

            def total_score(self):
                    ans = 0
                    for x in self.score:
                        ans += x
                    return ans
            
            def total_cost(self):
                    ans = 0
                    for x in self.cost:
                        ans += x
                    return ans

            def copy(self):
                    b = way()
                    
                    b.steps = self.steps.copy()
                    b.guess = self.guess.copy()
                    b.cost = self.cost.copy()
                    b.score = self.score.copy()
                    b.way_steps = (self.way_steps).copy()
                    b.final_score = self.final_score.copy()

                    return b

            def print(self):
                    if len(self.steps) != 0:
                        print (self.steps[0], end = "")
                    for i in range(0, len(self.steps)-1):
                        print (" ->", self.steps[i+1], end = "")
                    print ()
                    print ()
                    print ("Guess is :", self.guess) 
                    print ("Cost is :", self.cost) 
                    print ("Score is :", self.score)
                    print ("Final Scores is:", self.final_score)
                    
                    print ("---")
                    for i in range(len(self.way_steps)):
                        print ("Way form ", i, " to ", i+1, " is: ")
                        print (self.way_steps[i])
                        print ("----")
                    
                    print ("----------------------")

        def distance(coordinate1: tuple, coordinate2: tuple) -> int:
            return abs(coordinate1[0] - coordinate2[0]) + abs(coordinate1[1] - coordinate2[1]) 

        def find_closest(current_location: tuple, item) -> tuple:

                    min_distance = infinit
                    closest_diamond_coordinate = (-1, -1)
                    
                    for diamond in elements[item]:
                        if 0 < distance(current_location, diamond) < min_distance: 
                                min_distance = distance(current_location, diamond)
                                closest_diamond_coordinate = diamond
                    
                    return closest_diamond_coordinate

        def making_list_of_guess_ways(current_location: tuple, pre_color: int) -> list:
            w = way()
            observed, ways = [], []
            
            def sorting ():
                    for i in range(len(ways)):
                        for j in range(len(ways)-i-1):
                                if ways[j].total_cost() < ways[j+1].total_guess():
                                    ways[j], ways[j+1] = ways[j+1], ways[j]

            def distance(coordinate1: tuple, coordinate2: tuple) -> int:
                    return abs(coordinate1[0] - coordinate2[0]) + abs(coordinate1[1] - coordinate2[1])
            
            def find_diamond(current_location: tuple, pre_color: int, counter: int) -> None:
                    if counter == 3 and len(w.steps) > 0:
                        ways.append(w.copy())
                        return 
                    
                    _is_any_step = False
                    for x in range(4):
                        
                        next_location = find_closest(current_location, priority[pre_color][x])
                        
                        if next_location not in observed and next_location != (-1, -1):
                                _is_any_step = True
                                
                                d = distance(current_location, next_location)
                                s = diamond_score[pre_color][x]
                                
                                w.guess.append(s/d)
                                w.score.append(s)
                                
                                observed.append(next_location)
                                w.steps.append(next_location)
                                
                                find_diamond(next_location, priority[pre_color][x], counter+1)
                                
                                w.steps.pop()
                                observed.pop()

                                w.guess.pop()
                                w.score.pop()
                                
                    
                    if _is_any_step == False:
                        ways.append(w.copy())
                        return

            find_diamond(current_location, pre_color, 0)
            sorting()
            
            return ways

        def find_way(current_location: tuple, des: tuple, li: list, step) -> tuple:
            movements = {(1, 0): 1, (-1, 0): 1, (0, 1): 1, (0, -1): 1,
                        (1, 1): 2, (-1, -1): 2, (-1, 1): 2, (1, -1): 2}
            father = {}

            def movements_of_way(child: tuple):
                    li = []
                    while child != (-1, -1):
                        li.append(child)
                        child = father[child]
                    li.reverse()
                    return li

            def check(current_location: tuple, destination: tuple, w: list, step: int):
                    
                    x, y = current_location
                    
                    if current_location == destination or current_location in w[:step]:
                        return True
                    
                    if 0 <= x < len(chart) and 0 <= y < len(chart[0]) and chart[x][y] not in ['W', '1', '2', '3', '4', 1, 2, 3, 4]:
                        return True
                    
                    return False

            def bfs(current_location: tuple, destination: tuple, li: list, step: int):
                    q = PQ()
                    
                    observed = [current_location]
                    father[current_location] = (-1, -1)
                    q.put((0, current_location))
                    
                    while q.qsize() != 0:
                        
                        cost, head = q.get()

                        if head == destination:

                                return (cost, movements_of_way(destination))
                        
                        for move in movements.keys():
                                next_move = (head[0] + move[0], head[1] + move[1])

                                if check(next_move, destination, li, step) == True and next_move not in observed:
                                    
                                    observed.append(next_move)
                                    cost_of_move = cost + movements[move]
                                    
                                    x, y = next_move
                                    if chart[x][y] == "*": 
                                            cost_of_move += 50
                                    q.put((cost_of_move, next_move))
                                    father[next_move] = head
        
                    return (infinit, [])

            cost, l = bfs(current_location, des, li, step)

            for coordinate in l:
                    x, y = coordinate
                    if chart[x][y] in ['G', 'R', 'Y'] and self.own_key[chart[x][y].lower()] == False:
                        
                        tmp = chart[x][y]
                        chart[x][y] = 'W'
                        cost1 , l1 = find_way(current_location, des, li, step)
                        chart [x][y] = tmp

                        key_location = find_closest(current_location, tmp.lower())
                        tmp = chart[x][y]
                        chart[x][y] = 0
                        cost2, l2 = find_way(current_location, key_location, li, step)
                        
                        cost3, l3 = find_way(key_location, coordinate, li, step)
                        
                        cost4, l4 = find_way(coordinate, des, li, step)
                        
                        chart[x][y] = tmp
                        cost_total = cost2 + cost3 + cost4
                        if len(l2) > 0:
                                l2.pop()
                        if len(l3) > 0:
                                l3.pop()
                        l_total = l2 + l3 + l4

                        if cost1 < cost_total : 
                                cost, l = cost1, l1
                        else:
                                cost, l = cost_total, l_total

            return (cost, l)

        def real_cost(current_location: tuple, w: way()) -> None:
            loc1 = current_location
            for i in range(len(w.steps)):
                    loc2 = w.steps[i]
                    cost, l = find_way(loc1, loc2, w.steps, i)
                    loc1 = loc2
                    w.way_steps.append(l)
                    w.cost.append(cost)

        def printing_ways(ways: list) -> None:
            for x in ways:
                    x.print()
            print ("---------------") 

        def start(current_location: tuple, pre_color: int, number_of_round: int) -> list:

            analysis()
            ways = making_list_of_guess_ways(current_location, pre_color)
            
            answer1 = way()
            answer2 = way()

            max_score1 = -1
            max_score2 = -1

            for i in range(60):
                    if i < len(ways):
                        real_cost(current_location, ways[i])
                        final_score = ways[i].calculate_final_score()
                        if len(final_score) == 2:
                                if max_score1 < final_score[0] and ways[i].total_score() - ways[i].total_cost() > 0 and number_of_round >= len(ways[i].way_steps[0]):
                                        answer1 = ways[i].copy()
                                        max_score1 = final_score[0]
                                
                                if max_score2 < final_score[1] and number_of_round >= len(ways[i].way_steps[0]):
                                        answer2 = ways[i].copy()
                                        max_score2 = final_score[1]
                    else:
                        break  
            
            
            if max_score1 < 0:
                    if (max_score2 > 0):
                        #print (answer2.way_steps)
                        return answer2.way_steps[0]
                    else:
                        return [(-1000, -1000), (-1000, -1000)]
            else:
                    #print (answer1.way_steps)
                    return answer1.way_steps[0]

        move_action = {(1, 0): Action.DOWN, (-1, 0): Action.UP, (0, 1): Action.RIGHT, (0, -1): Action.LEFT, (0, 0): Action.NOOP,
                     (1, 1): Action.DOWN_RIGHT, (-1, 1): Action.UP_RIGHT, (1, -1): Action.DOWN_LEFT, (-1, -1): Action.UP_LEFT
                }

        def find_action(current_location: tuple, next_move: tuple) -> Action:
                tmp = (next_move[0] - current_location[0], next_move[1] - current_location[1])
                return move_action[tmp]


        if self.turn_count == 1:
                self.pre_color = 0
                self.ans_list = []
                self.current_location = (0, 0)
        
        if len(self.ans_list) == 0:
                self.ans_list = start(self.current_location, self.pre_color, self.max_turn_count - self.turn_count + 1)
                if len(self.ans_list) > 0:
                        self.ans_list.pop(0)
        print(self.grid)
        if len(self.ans_list) > 0 and self.ans_list[0] == (-1000, -1000):
                print("noop")
                return Action.NOOP
        
        else:
                tmp = self.current_location
                if len(self.ans_list) > 0:
                        self.current_location = self.ans_list.pop(0)
                
                x, y = self.current_location
                c = chart[x][y]
                if c in ['g', 'r', 'y']:
                        self.own_key[c] = True

                elif c in ['1', '2', '3', '4']:
                        self.pre_color = (int(c) - int('0'))
                
                return find_action(tmp,self.current_location)


if __name__ == '__main__':
    data = Agent().play()
    print("FINISH : ", data)
