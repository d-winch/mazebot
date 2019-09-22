import numpy as np
import requests
import json
from node import Node
import sys

def get_nodes(node_map):
    
    # Create empty dict to store node objects
    nodes = {}
    
    for y, row in enumerate(node_map):
        for x, cell in enumerate(row):

            # If cell is X, we can't visit it
            if cell == 'X':
                continue

            # Create a dict to store possible movement
            directions = {}

            # If not the first row
            if y > 0:
                # Can we move North?
                if node_map[y-1][x] != 'X':
                    directions['N'] = (x,y-1)

            # If not the last row
            if y < len(node_map)-1:
                # Can we move South?
                if node_map[y+1][x] != 'X':
                    directions['S'] = (x,y+1)

            # If not the first column
            if x > 0:
                # Can we move West?
                if node_map[y][x-1] != 'X':
                    directions['W'] = (x-1,y)

            # If not the last column
            if x < len(row)-1:
                # Can we move East?
                if node_map[y][x+1] != 'X':
                    directions['E'] = (x+1,y)

            # Create a new node object and add it to our node dict
            n = Node(x, y, directions)
            nodes[x,y] = n

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
    
    while len(open_nodes) > 0:

        current = None
        current_f_score = None

        for node in open_nodes:
            if current is None or F[node] < current_f_score:
                current_f_score = F[node]
                current = node

        # If we're at the end, return the directions taken
        if list(current) == Node.end_location:

            #print("Open",sys.getsizeof(open_nodes))
            #print("Came From",sys.getsizeof(came_from))
            #print("F",sys.getsizeof(F))
            #print("G",sys.getsizeof(G))

            # Reverse our directions taken
            directions_taken = [dirs[current]]
            while current in came_from:
                current = came_from[current]
                if current != start:
                    direction_taken = dirs[current]
                    directions_taken.append(direction_taken)
            directions_taken.reverse()
            return directions_taken

        # We're finished with this node
        open_nodes.remove(current)
        closed_nodes.add(current)

        # Update scores for possible neighbour movements
        for direction, neighbour in nodes[current].possible_directions.items():
            if neighbour in closed_nodes:
                continue # We've already tested this node and removed it
            
            candidate_g = G[current] + Node.move_cost

            if neighbour not in open_nodes:
                open_nodes.add(neighbour) # New possible path
            elif candidate_g >= G[neighbour]:
                continue # This G score is worse than previous

            # Adopt this G score
            came_from[neighbour] = current
            G[neighbour] = candidate_g

            F[neighbour] = G[neighbour] + nodes[neighbour].distance_from_end
            dirs[neighbour] = direction


if __name__ == '__main__':

    # Best cert = 9.881 /mazebot/race/certificate/GC81T6AIkPZDXWpP2wJiEBMZkEBNTJE-lVc67OMFLdA

    BASE_URL = 'https://api.noopschallenge.com'
    user_details = {'login': 'd-winch'}
    response = requests.get(f'{BASE_URL}/mazebot/race').json()
    print(response['message'])
    response = requests.post(f'{BASE_URL}/mazebot/race/start', json=user_details).json()
    print(response['message'])
    
    while 'nextMaze' in response:
        maze = requests.get(f"{BASE_URL}{response['nextMaze']}").json()

        node_map = np.array( maze['map'] )
        Node.end_location = maze['endingPosition']

        traversable_nodes = get_nodes(node_map)

        solution = traverse(traversable_nodes)

        solution_submission = {
            "directions": ''.join(solution)
            }

        response = requests.post(f"{BASE_URL}{maze['mazePath']}",json=solution_submission).json()
        print(response)
