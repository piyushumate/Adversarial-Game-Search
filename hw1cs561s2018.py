__author__ = "Piyush Umate"

from copy import deepcopy
import sys

INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"
ROW_SIZE = COLUMN_SIZE = 8
algorithm = max_depth = weights = None
row_names = ['H','G','F','E','D','C','B','A']
player_prefix_map = {
    'star': 'S',
    'circle': 'C'
}
player = None
node_counter = 0

class Node:
    def __init__(self, board_state=None, player=None, utility_value=None):
        self.board_state = board_state
        self.next_moves, self.children = [], []
        self.player = player
        self.utility_value = utility_value

    def add_move(self, row_start, col_start, row_end, col_end):
        self.next_moves.append((
            str(row_start)+str(col_start),
            str(row_end)+str(col_end),
        ))

    def sort(self):
        # if self.player == 'circle':
        #     self.next_moves.sort(
        #         key=lambda k: (k[0], -int(k[1])), reverse=True
        #     )
        # else:
        self.next_moves.sort(
            key=lambda k: (k[0], k[1])
        )

    def compute_next_moves(self):
        operator_map = {
            'S': sub,
            'C': add
        }
        player_prefix = player_prefix_map[self.player]
        alt_player_prefix = 'C' if player_prefix == 'S' else 'S'
        last_row = 0 if player_prefix == 'S' else ROW_SIZE-1
        operator = operator_map[player_prefix]
        for row in range(ROW_SIZE):
            for col in range(COLUMN_SIZE):
                if self.board_state[row][col].startswith(player_prefix):
                    poss_row, poss_col = operator(row, 1), add(col, 1)
                    if in_range(poss_row, 0, ROW_SIZE) and \
                        in_range(poss_col, 0, COLUMN_SIZE):
                            if self.board_state[poss_row][poss_col] == '0': #empty spot
                                self.add_move(row, col, poss_row, poss_col)
                            elif self.board_state[poss_row][poss_col].startswith(alt_player_prefix): #alternate player in spot
                                poss_row, poss_col = operator(poss_row, 1), add(poss_col, 1)
                                if in_range(poss_row, 0, ROW_SIZE) and \
                                    in_range(poss_col, 0, COLUMN_SIZE):
                                        if self.board_state[poss_row][poss_col] == '0' or \
                                            (poss_row == last_row and \
                                            self.board_state[poss_row][poss_col].startswith(player_prefix)):
                                                self.add_move(row, col, poss_row, poss_col)
                            else: #same player in spot
                                if poss_row == last_row:
                                    self.add_move(row, col, poss_row, poss_col)

                    poss_row, poss_col = operator(row, 1), sub(col, 1)
                    if in_range(poss_row, 0, ROW_SIZE) and \
                        in_range(poss_col, 0, COLUMN_SIZE):
                            if self.board_state[poss_row][poss_col] == '0': #empty spot
                                self.add_move(row, col, poss_row, poss_col)
                            elif self.board_state[poss_row][poss_col].startswith(alt_player_prefix): #alternate player in spot
                                poss_row, poss_col = operator(poss_row, 1), sub(poss_col, 1)
                                if in_range(poss_row, 0, ROW_SIZE) and \
                                    in_range(poss_col, 0, COLUMN_SIZE):
                                        if self.board_state[poss_row][poss_col] == '0' or \
                                            (poss_row == last_row and \
                                            self.board_state[poss_row][poss_col].startswith(player_prefix)):
                                                self.add_move(row, col, poss_row, poss_col)
                            else: #same player in spot
                                if poss_row == last_row:
                                    self.add_move(row, col, poss_row, poss_col)
        #handle pass and no move here
        self.sort()
        if not len(self.next_moves):
            self.next_moves.append('pass')

    def is_move(self):
        star_player_available, circle_player_available = False, False
        for row in range(ROW_SIZE):
            for col in range(COLUMN_SIZE):
                if self.board_state[row][col].startswith('S'):
                    star_player_available = True
                if self.board_state[row][col].startswith('C'):
                    circle_player_available = True
        return star_player_available and circle_player_available

    def updated_board_state(self, isAdd, temp_board_state, spot_row, spot_col):
        #returns a new copy of board state
        if isAdd:
            if self.board_state[spot_row][spot_col] == '0':
                temp_board_state[spot_row][spot_col] = \
                    player_prefix_map[self.player]+'1'
            else:
                val = self.board_state[spot_row][spot_col]
                temp_list = list(val)
                temp_list[1] = str(int(temp_list[1])+1)
                temp_board_state[spot_row][spot_col] = ''.join(temp_list)
        else:
            val = self.board_state[spot_row][spot_col]
            temp_list = list(val)
            if int(temp_list[1]) > 1:
                temp_list[1] = str(int(temp_list[1]-1))
                temp_board_state[spot_row][spot_col] = ''.join(temp_list)
            else:
                temp_board_state[spot_row][spot_col] = '0'
        return temp_board_state

    def compute_utility(self):
        star_player_sum, circle_player_sum = 0, 0
        for row in range(ROW_SIZE):
            for col in range(COLUMN_SIZE):
                pos_val= self.board_state[row][col]
                if pos_val.startswith('S'):
                    star_player_sum += weights[ROW_SIZE-1-row] * int(list(pos_val)[1])
                elif pos_val.startswith('C'):
                    circle_player_sum += weights[row] * int(list(pos_val)[1])
        if player == 'circle':
            return circle_player_sum - star_player_sum
        return star_player_sum - circle_player_sum

    def create_children(self):
        #using the next moves create board with updated states
        alternate_player = 'circle' if self.player == 'star' else 'star'
        for move in self.next_moves:
            if isinstance(move, tuple):
                temp_board_state = deepcopy(self.board_state)
                move_index = map(int, list((move[0]+move[1])))
                #capture
                if abs(move_index[2] - move_index[0]) == \
                    abs(move_index[1] - move_index[3]) == 2:
                        #remove from old spot
                        temp_board_state = self.updated_board_state(
                            False, temp_board_state, move_index[0], move_index[1]
                        )
                        #add to new spot
                        temp_board_state = self.updated_board_state(
                            True, temp_board_state, move_index[2], move_index[3]
                        )
                        #remove opponent by finding mid point
                        temp_board_state = self.updated_board_state(
                            False, temp_board_state, (move_index[0]+move_index[2])/2,
                            (move_index[1]+move_index[3])/2
                        )

                else:
                    #remove from old spot
                    temp_board_state = self.updated_board_state(
                        False, temp_board_state, move_index[0], move_index[1]
                    )

                    #add to new spot
                    temp_board_state = self.updated_board_state(
                        True, temp_board_state, move_index[2], move_index[3]
                    )
                child = Node(temp_board_state, alternate_player)
                self.children.append(child)
        if 'pass' in self.next_moves:
            self.children.append(
                Node(self.board_state, alternate_player)
            )


def in_range(value, min, max):
    if min <= value < max:
        return True
    return False


def add(op1, op2):
    return op1 + op2

def sub(op1, op2):
    return op1 - op2

def alphabeta(game_node, current_depth, max_depth, is_max, is_parent_pass, alpha, beta):
    global node_counter
    node_counter += 1
    if current_depth == max_depth or not game_node.is_move():
        return game_node.compute_utility()
    game_node.compute_next_moves()
    pass_move = True if 'pass' in game_node.next_moves else False

    if pass_move and is_parent_pass:
        node_counter += 1
        return game_node.compute_utility()

    game_node.create_children()
    if is_max:
        max_val = -sys.maxint - 1
        for child in game_node.children:
            max_val = max(max_val, alphabeta(
                child, current_depth+1, max_depth, False, pass_move, alpha, beta)
            )
            alpha = max(alpha, max_val)
            child.utility_value = max_val
            if beta <= alpha:
                break
        return max_val
    else:
        min_val = sys.maxint
        for child in game_node.children:
            min_val = min(min_val, alphabeta(
                child, current_depth+1,max_depth, True, pass_move, alpha, beta)
            )
            beta = min(beta, min_val)
            child.utility_value = min_val
            if beta <= alpha:
                break
        return min_val

def minimax(game_node, current_depth, max_depth, is_max, is_parent_pass):
    global node_counter
    node_counter += 1
    if current_depth == max_depth or not game_node.is_move():
        return game_node.compute_utility()
    game_node.compute_next_moves()
    pass_move = True if 'pass' in game_node.next_moves else False
    if pass_move and is_parent_pass:
        node_counter+= 1
        return game_node.compute_utility()

    game_node.create_children()

    if is_max:
        max_val = -sys.maxint - 1
        for child in game_node.children:
            max_val = max(max_val, minimax_v2(child, current_depth+1,max_depth, False, pass_move))
            child.utility_value = max_val
        return max_val
    else:
        min_val = sys.maxint
        for child in game_node.children:
            min_val = min(min_val, minimax_v2(child, current_depth+1,max_depth, True, pass_move))
            child.utility_value = min_val
        return min_val

def compute_next_move(game_node, best_value):
    if 'pass' in game_node.next_moves:
        return 'pass', game_node.compute_utility()
    else:
        for index, child in enumerate(game_node.children):
            if child.utility_value == best_value:
                break
        move = []
        for pos in game_node.next_moves[index]:
            unpacked_move = list(pos)
            move.append(
                row_names[int(unpacked_move[0])]+str(int(unpacked_move[1])+1)
            )
        return '-'.join(move), child.compute_utility()

def process_output(game_node, best_value):
    move, myopic_utility = compute_next_move(game_node, best_value)
    output = [move+'\n',
              str(myopic_utility)+'\n',
              str(best_value)+'\n',
              str(node_counter)]
    file_handle = open(OUTPUT_FILE, "w")
    file_handle.writelines(output)
    file_handle.close()

def create_board_state(stringy_board_state):
    board_state = []
    for board_row in stringy_board_state:
        board_state.append(board_row.split(','))
    return board_state

def process_input(input=INPUT_FILE):
    with open(input, 'r') as file_pointer:
        lines = file_pointer.read().splitlines()
    global algorithm, max_depth, weights, player
    algorithm, max_depth, player = lines[1], int(lines[2]), lines[0].lower()
    weights = map(int, lines[-1].split(','))
    root = Node(create_board_state(lines[3:-1]), player)
    if algorithm == 'MINIMAX':
        best_value = minimax(root, 0, max_depth, True, False)
    else:
        best_value = alphabeta(
            root, 0, max_depth, True, False, -sys.maxint - 1 , sys.maxint
        )
    process_output(root, best_value)
process_input()
