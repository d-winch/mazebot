import numpy as np
import requests
import json
from node import Node
import sys

def get_nodes(map):
    nodes = {}
    for y, row in enumerate(map):
        for x, cell in enumerate(row):

            directions = {}

            #if cell in ['A', 'B', 'X']:
            if cell == 'X':
                continue

            # If not the first row
            if y > 0:
                # Can we move North?
                if map[y-1][x] != 'X':
                    directions['N'] = (x,y-1)

            # If not the last row
            if y < len(map)-1:
                # Can we move South?
                if map[y+1][x] != 'X':
                    directions['S'] = (x,y+1)

            # If not the first column
            if x > 0:
                # Can we move West?
                if map[y][x-1] != 'X':
                    directions['W'] = (x-1,y)

            # If not the last column
            if x < len(row)-1:
                # Can we move East?
                if map[y][x+1] != 'X':
                    directions['E'] = (x+1,y)

            n = Node(x, y, directions)
            nodes[x,y] = n

            #possible_directions[x,y] = directions

    return nodes

def traverse(traversable_nodes):

    nodes = traversable_nodes

    G = {} #Actual movement cost to each position from the start position
    F = {} #Estimated movement cost of start to end going via this position

    #Initialize starting values
    start = tuple(maze['startingPosition'])
    end = tuple(maze['endingPosition'])
    G[start] = 0
    F[start] = traversable_nodes[start].distance_from_end

    closed_nodes = set()
    open_nodes = set([start])
    came_from = {}
    dirs = {}
    i = 0
    while len(open_nodes) > 0:
        i = i+1

        current = None
        current_f_score = None

        for node in open_nodes:
            if current is None or F[node] < current_f_score:
                current_f_score = F[node]
                current = node

        # If we're at the end, return!
        if list(current) == Node.end_location:

            print("Open",sys.getsizeof(open_nodes))
            print("Came From",sys.getsizeof(came_from))
            print("F",sys.getsizeof(F))
            print("G",sys.getsizeof(G))

            #Retrace our route backward
            directions_taken = [dirs[current]]
            while current in came_from:
                current = came_from[current]
                if current != start:
                    direction_taken = dirs[current]
                    directions_taken.append(direction_taken)
            directions_taken.reverse()
            print(i)
            return directions_taken

        #Mark the current vertex as closed
        open_nodes.remove(current)
        closed_nodes.add(current)

        #Update scores for vertices near the current position
        for direction, neighbour in nodes[current].possible_directions.items():
            if neighbour in closed_nodes:
                continue #We have already processed this node exhaustively
            candidate_g = G[current] + Node.move_cost

            if neighbour not in open_nodes:
                open_nodes.add(neighbour) #Discovered a new vertex
            elif candidate_g >= G[neighbour]:
                continue #This G score is worse than previously found

            #Adopt this G score
            came_from[neighbour] = current
            G[neighbour] = candidate_g

            F[neighbour] = G[neighbour] + nodes[neighbour].distance_from_end
            dirs[neighbour] = direction


if __name__ == '__main__':

    # Best cert = /mazebot/race/certificate/Wln6EJuKH27oGmvl6TYDPy3lyBkxTpHIEIh2nR_mtqNUyUd_VeCesDU86IHS89DY
    # 9.881 /mazebot/race/certificate/GC81T6AIkPZDXWpP2wJiEBMZkEBNTJE-lVc67OMFLdA

    api = 'https://api.noopschallenge.com'
    user_details = {'login': 'd-winch'}
    response = requests.get(api+'/mazebot/race').json()
    print(response)
    response = requests.post(api+'/mazebot/race/start', json=user_details).json()
    print(response)
    
    while 'nextMaze' in response:
        maze = requests.get(api+response['nextMaze']).json()

        map = np.array( maze['map'] )
        Node.end_location = maze['endingPosition']

        traversable_nodes = get_nodes(map)

        solution = traverse(traversable_nodes)

        solution_submission = {
            "directions": ''.join(solution)
            }

        response = requests.post(api+maze['mazePath'],json=solution_submission).json()
        print(response)
