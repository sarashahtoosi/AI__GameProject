
chart = [[0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0]
        ]




def pre_procces(chart: list) -> None:
    
    satr = len(chart)
    soton = len(chart[0])
    
    INF = 10000000
    
    num = 1
    def chart_to_map():
        num = 1
        map = []

        for i in range(satr):
            map.append([])
            for j in range(soton):
                map[i].append(num)
                num += 1

    chart_to_map()
    
    movements = {(1, 0): 1, (-1, 0): 1, (0, 1): 1, (0, -1): 1,
                 (1, 1): 2, (1, -1): 2, (-1, 1): 2, (-1, -1): 2
                }

    def check(coordinate: tuple) -> bool:    #shahtoosi
        return 0 <= coordinate[0] < satr and 0 <= coordinate[1] < soton

    G = []
    for i in range(satr * soton):
        for j in range(satr * soton):
            /

    def convert_chart_to_graph():
        for i in range():
            for j in range(chart[0]):
                x = (i, j)
                for m in movements.keys: 
                    
                    y = (i+m[0], j+m[1])

                    if check(y) == True:
                       
                        if chart[y[0]][y[1]] != 'W':
                            G[x][y] = INF
                
                        elif chart[y[0]][y[1]] != '*':
                            G[x][y] = 50
                        
                        else:
                            G[x][y] = movements[m]


                


pre_procces(chart)
print (G)