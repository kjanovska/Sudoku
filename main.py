import copy


class Variable:
    def __init__(self, x_coord, y_coord, init_domain):
        self.x = x_coord
        self.y = y_coord
        self.domain = init_domain
        self.assigned = False
        self.value = None

    def domain_remove(self, value):
        self.domain.remove(value)


def build_environment(filename):
    sudoku = []
    file = open(filename, 'r').read().splitlines()
    for line in file:
        sudoku.append(list(line))
    return build_class_environment(sudoku)


def build_class_environment(sudoku):
    """
    :return: 2D list containing variables
    """
    res = []
    for i in range(0, 9):
        line = []
        for j in range(0, 9):
            if sudoku[i][j] == '_':
                new_var = Variable(i, j, {1, 2, 3, 4, 5, 6, 7, 8, 9})
            else:
                new_domain = {int(sudoku[i][j])}
                new_var = Variable(i, j, new_domain)
                new_var.assigned = True
                new_var.value = int(sudoku[i][j])
            line.append(new_var)
        res.append(line)
    print("Beginning:")
    print_board(res)
    return res


def init_constraints():
    """
    :return: a list of binary constraints
    """
    constraints = []
    for i in range(0, 9):
        for j in range(0, 9):
            constraints_1 = neighbours(board[i][j], board[i][j], board)
            for plep in constraints_1:
                constraints.append(([i, j], plep))
    return constraints


def ac3(constr, state):
    """
    AC3 - constraint propagation algorithm - tries to achieve arc consistency
    a variable in state is arc-consistent, if every value of variable.domain satisfies all of that variable's binary
    constraints
    :param constr: set of binary constraints - arcs
    :param state: sudoku board - 2D list with variables
    :return: True if arc consistency is achievable
    """
    queue = constr  # queue of arcs - initially all arcs in csp
    while len(queue) != 0:
        constraint = queue.pop(0)
        x_i = state[constraint[0][0]][constraint[0][1]]
        x_j = state[constraint[1][0]][constraint[1][1]]
        if x_i != x_j and revise(x_i, x_j):
            if len(x_i.domain) == 0:
                return False
            for x in neighbours(x_i, x_j, state):
                queue.append((x, [x_i.x, x_i.y]))
    return True


def revise(x_i, x_j):
    """
    :return: True if assignment of pair x_i, x_j is achievable
    """
    revised = False
    tmp_domain = copy.deepcopy(x_i.domain)
    for x in tmp_domain:
        if not is_combination_possible(x, x_j.domain):
            x_i.domain_remove(x)
            revised = True
    return revised


def is_combination_possible(x, domain):
    """
    :return: False if checked domain contains only one value and that value equals x - combination of them is not possible
    """
    if len(domain) == 1 and x in domain:
        return False
    return True


def neighbours(x_i, x_j, state):
    """
    :return: neighbourhood of variable x_i with the exception of variable x_j
    neighbourhood = row, column and box
    """
    neigh = []
    for i in range(0, 9):
        if state[x_i.x][i] != x_j:
            neigh.append([x_i.x, i])
        if state[i][x_i.y] != x_j:
            neigh.append([i, x_i.y])
    box_x = x_i.x % 3
    box_y = x_i.y % 3
    x_iter = set()
    y_iter = set()
    if box_x == 0:
        x_iter = {0, 1, 2}
    elif box_x == 1:
        x_iter = {-1, 0, 1}
    else:
        x_iter = {-2, 0, -1}
    if box_y == 0:
        y_iter = {1, 0, 2}
    elif box_y == 1:
        y_iter = {-1, 0, 1}
    else:
        y_iter = {-2, 0, -1}
    for i in x_iter:
        for j in y_iter:
            if state[i + x_i.x][j + x_i.y] != x_i and state[i + x_i.x][j + x_i.y] != x_j:
                neigh.append([i + x_i.x, j + x_i.y])
    return neigh


def nine_consistent(state):  # state = list o deviti prvcich = prirazenych hodnotach
    """
    check, if row/column/box is consistent - each value is present at most once
    :return: True if consistent
    """
    full_states = []
    for i in range(0, len(state)):
        if state[i] is not None:
            full_states.append(state[i])
    set_states = set(full_states)
    if len(set_states) != len(full_states):
        return False
    return True


def select_row(x, sudoku_state):
    """
    :return: values in row x
    """
    column = []
    for y in range(0, 9):
        column.append(sudoku_state[x][y].value)
    return column


def select_column(y, sudoku_state):
    """
    :return: values in column y
    """
    column = []
    for x in range(0, 9):
        column.append(sudoku_state[x][y].value)
    return column


def select_box(x, y, state):
    """
    :return: values assigned in the same box in which [x, y] coordinates lay
    """
    box = []
    box_x = x % 3
    box_y = y % 3
    x_iter = set()
    y_iter = set()
    if box_x == 0:
        x_iter = {0, 1, 2}
    elif box_x == 1:
        x_iter = {-1, 0, 1}
    else:
        x_iter = {-2, 0, -1}
    if box_y == 0:
        y_iter = {1, 0, 2}
    elif box_y == 1:
        y_iter = {-1, 0, 1}
    else:
        y_iter = {-2, 0, -1}
    for i in x_iter:
        for j in y_iter:
            if [i + x, j + y] != [x, y]:
                box.append(state[i + x][j + y].value)
    return box


def consistent(value, variable, sudoku_state):
    """
    checks if neighbourhood of variable is consistent after variable is assigned value
    neighbourhood == variable's column, row and box
    :return: True if consistent, False otherwise
    """
    tmp_state = copy.deepcopy(sudoku_state)
    tmp_state[variable[0]][variable[1]].value = value
    row = select_row(variable[0], tmp_state)
    if not nine_consistent(row):
        return False
    column = select_column(variable[1], tmp_state)
    if not nine_consistent(column):
        return False
    box = select_box(variable[0], variable[1], tmp_state)
    if not nine_consistent(box):
        return False
    return True


def solved(sudoku_state):
    """"
    :return: True if all variables have an assigned value, else return False
    """
    for x in range(0, 9):
        for y in range(0, 9):
            if not sudoku_state[x][y].assigned:
                return False
    return True


def select_unassigned(sudoku_state, constr):
    """"
    MINIMUM-REMAINING VALUES heuristics
    chooses that variable, which is both unassigned and has the least amount of possible values in its domain
    """
    next_variable = []
    domain_len = 10
    for x in range(0, 9):
        for y in range(0, 9):
            if len(sudoku_state[x][y].domain) < domain_len and not sudoku_state[x][y].assigned:
                domain_len = len(sudoku_state[x][y].domain)
                next_variable = [x, y]
    return next_variable


def order_domain_values(variable, state, constr):
    """
    LEAST-CONSTRAINING VALUE heuristics
    chooses which from variable's domain that interferes with neighbouring variables the least
    :return: a list of tuples (value, number of conflicts), sorted by number of conflicts from lowest to highest
    number of conflicts = how many other domains has this choice affected
    """
    neigh = neighbours(state[variable[0]][variable[1]], state[variable[0]][variable[1]], state) # jsou tam vsichni
    all_values_counters = []
    for value in state[variable[0]][variable[1]].domain:
        conflict_counter = 0
        for neighbour in neigh:
            if value in state[neighbour[0]][neighbour[1]].domain:
                conflict_counter += 1
        all_values_counters.append((value, conflict_counter))
    return sorted(all_values_counters, key=lambda x: x[1])


def backtracking(state, constr):
    """"
    backtracking algorithm using AC3 as inference for achieving arc consistency
    :param constr: set of binary constraints - arcs
    :param state: sudoku board - 2D list with variables
    :return: solved sudoku board with all variables assigned, None if result doesn't exist
    """
    sudoku_state = copy.deepcopy(state)
    if solved(sudoku_state):
        return sudoku_state
    variable = select_unassigned(sudoku_state, constr)  # a box in sudoku - board[x][y]
    for val in order_domain_values(variable, sudoku_state, constr):
        value = val[0]
        if consistent(value, variable, sudoku_state):
            sudoku_state[variable[0]][variable[1]].domain = {value}
            sudoku_state[variable[0]][variable[1]].assigned = True
            sudoku_state[variable[0]][variable[1]].value = value
            if ac3(constr, sudoku_state):
                res = backtracking(sudoku_state, constr)
                if res is not None:
                    return res
    return None


def print_board(board):
    for x in range(0, 9):
        print("|", end="")
        for y in range(0, 9):
            if board[x][y].value is not None:
                print(board[x][y].value, end="|")
            else:
                print(" ", end="|")
        print("")
        print('_'*19)


if __name__ == '__main__':
    for i in {1, 2, 3}:
        board = build_environment('sudoku_example_' + str(i) + '.txt')
        constraints = init_constraints()
        # 1. AC3 algorithm -> reducing domains
        ac3_result = ac3(constraints, board)
        # 2. Backtracking
        result = backtracking(board, constraints)
        print("Result:")
        print_board(result)
