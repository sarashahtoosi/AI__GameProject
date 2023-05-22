import random
from base import BaseAgent, Action
import pandas as pd 
import numpy as np
import copy

class Agent(BaseAgent):
    sheets = {}
    pre_color = '0'
    gems_list = [[0, 0, 0, 0]]
    matrix = []
    pre_chart = []
    key = {'g': False, 'y': False, 'r': False}

    def do_turn(self) -> Action:
        def printing (l):
            for x in l:
                print (x)
            print ("=========")

        move = [(-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1),
                (-1, -1, 2),(1, 1, 2), (1, -1, 2), (-1, 1, 2)]

        def check(point):
            return 0 <= point[0] < len(self.grid) and 0 <= point[1] < len(self.grid[0])

        def block_type(x):      
            if x in ['r', 'g', 'y', '1', '2', '3', '4']:
                return "slider" 
            if x ==  '*':
                return "barbed" 
            if x ==  'T':
                return "teleport" 
            return "normal"

        def markov(matrix, chart):
            def calculate_markov_score(point, probilities):
                x, y = point

                if matrix[x][y] not in [-10, 50, 100, 150, 200, 250, 300]:      
                    ans = -100
                    for i in range(len(move)):
                        total = 0
                        for j in range(len(move)):
                            a, b = x+move[j][0], y+move[j][1]

                            if check((a, b)) and matrix[a][b] != -10:
                                cost = move[j][2] * 0.1
                                if chart[a][b] == 12: 
                                    cost = 0.1
                                
                                total += probilities[i][j] * (0.9 * matrix[a][b] - cost)  
                        
                        ans = max(ans, round(total, 2))
                    printing (matrix)
                    matrix[x][y] = ans
            
            for k in range(len(chart)):
                for i in range(len(chart)):
                    for j in range(len(chart[0])):
                        calculate_markov_score((i, j), self.sheets[block_type(chart[i][j])])
            return matrix
        
        def get_sheets():
            sheets = {}
            for x in ["normal", "slider", "barbed", "teleport"]:
                sheets[x] = pd.read_excel("../server/probabilities/1.xlsx", x)
                sheets[x].drop(columns=sheets[x].columns[0], axis=1,  inplace=True)
                sheets[x] = sheets[x].values.tolist()
            return sheets
        
        colors_list = {
            '0' : {'1': 100, '2': 50, '3': 50, '4': 50, 'r': 50, 'y': 50, 'g': 50, 'T': 50},
            '1' : {'1': 100, '2': 250, '3': 150, '4': 50, 'r': 50, 'y': 50, 'g': 50, 'T': 50},
            '2' : {'1': 150, '2': 100, '3': 250, '4': 150, 'r': 50, 'y': 50, 'g': 50, 'T': 50},
            '3' : {'1': 100, '2': 150, '3': 100, '4': 250, 'r': 50, 'y': 50, 'g': 50, 'T': 50},
            '4' : {'1': 300, '2': 100, '3': 150, '4': 100, 'r': 50, 'y': 50, 'g': 50, 'T': 50}
        }
        
        def make_empty_matrix(chart):
            matrix = []
            [matrix.append([]) for i in range(len(chart))]
            for i in range(len(chart)):
                for j in range(len(chart[0])):
                    matrix[i].append(0)
            return matrix
        
        def make_matrix(pre_color, chart, list_key):
            matrix = make_empty_matrix(chart)

            for i in range(len(chart)):
                for j in range(len(chart[0])):
                    x = chart[i][j]

                    if x in ['W']:
                        matrix[i][j] = -10
                    
                    elif x in ['1', '2', '3', '4', 'y', 'r', 'g', 'T']:
                        if pre_color in ['r', 'y', 'g']:
                            matrix[i][j] = -10
                        else:
                            matrix[i][j] = colors_list[pre_color][x]
                    
                    elif pre_color in ['r', 'y', 'g'] and x == pre_color:
                        matrix[i][j] = 100

                    elif x in ['R', 'Y', 'G']:
                        if list_key[x.lower()] == False:
                            matrix[i][j] = -10
            return matrix
        
        action = {(1, 0): Action.DOWN, (-1, 0): Action.UP, (0, 1): Action.RIGHT,
                  (0, -1): Action.LEFT, (0, 0): Action.NOOP, (1, 1): Action.DOWN_RIGHT,
                  (-1, 1): Action.UP_RIGHT, (1, -1): Action.DOWN_LEFT, (-1, -1): Action.UP_LEFT}

        def find_action(start, matrix):
            point, value = start, -100
            x, y = start
            for mv in move:
                nx, ny = x+mv[0], y+mv[1]
                
                if check((nx, ny)) and matrix[nx][ny] > matrix[x][y]:
                    
                    if matrix[nx][ny] > value:
                        value = matrix[nx][ny]
                        point = (nx, ny)

            return action[(point[0]-x, point[1]-y)]
        
        def get_start(chart):
            for i in range(len(chart)):
                for j in range(len(chart[0])):
                    if 'A' in chart[i][j]:
                        return (i, j)
        
        def color(l1, l2):
            for x in range(4):
                if l1[0][x] != l2[0][x]:
                    return x+1
            return 0

        def main(pre_color, list_key):
            def run():
                self.matrix = make_matrix(pre_color, chart, list_key)
                self.matrix = markov(self.matrix, chart)
            
            chart = self.grid
            start = get_start(chart)

            if self.turn_count == 1:
                self.sheets = get_sheets()
                self.pre_chart = copy.deepcopy(chart)
                run()
            
            x, y = start

            v = self.pre_chart[x][y]
            if v in ['r', 'g', 'y', '1', '2', '3', '4']:
                if v in ['r', 'g', 'y']:
                    self.key[v] = True
                else:
                    self.pre_color = v
                    pre_color = v
                run()
            tmp = find_action(start, self.matrix)
            
            if tmp == Action.NOOP:  
                for c in ['r', 'g', 'y']:
                    if self.key[c] == False:
                        li = copy.deepcopy(self.key)
                        li[c] = True
                        aa = make_matrix(pre_color, chart, li)
                        aa = markov(aa, chart)
                        tmp1 = find_action(start, aa)
                      
                        if tmp1 != Action.NOOP:
                            aa = make_matrix(c, chart, self.key)
                            aa = markov(aa, chart)
                            tmp2 = find_action(start, aa)
                            if tmp2 != Action.NOOP:
                                self.matrix = aa
                                return find_action(start, aa)

            if tmp == Action.NOOP:
                run()
                tmp = find_action(start, self.matrix)

            if tmp == Action.NOOP and chart[x][y] == 'TA':
                tmp = random.choice([Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT])
            
            self.pre_chart = copy.deepcopy(chart)   
            return tmp
        
        return main(self.pre_color, self.key)

if __name__ == '__main__':
    data = Agent().play()
    print("FINISH : ", data)
