class Board:
    ''' class to store and manipulate connect 4 game states '''

    def __init__(self, width=7, height=6):
        self.w = width
        self.h = height
        self.board_state = [0, 0]
        self.col_heights = [(height + 1) * i for i in range(width)]
        self.moves = 0
        self.history = []
        self.node_count = 0
        # self.buffer = self.__get_buffer()
        self.bit_shifts = self.__get_bit_shifts()
        self.base_search_order = self.__get_base_search_order()

    def __repr__(self):
        state = []
        for i in range(self.h):                         # row
            row_str = ''
            for j in range(self.w):                     # col
                pos = 1 << (self.h + 1) * j + i
                if self.board_state[0] & pos == pos:
                    row_str += 'x '
                elif self.board_state[1] & pos == pos:
                    row_str += 'o '
                else:
                    row_str += '. '
            state.append(row_str)
        state.reverse()         # inverted orientation more readable
        return '\n'.join(state)

    def get_current_player(self):
        ''' returns current player: 0 or 1 (0 always plays first) '''
        return self.moves & 1

    def get_opponent(self):
        ''' returns opponent to current player: 0 or 1 '''
        return (self.moves + 1) & 1

    def get_search_order(self):
        ''' returns column search order containing playable columns only '''
        col_order = filter(self.can_play, self.base_search_order)
        return sorted(col_order, key=self.__col_sort, reverse=True)

    def get_mask(self):
        ''' returns bitstring of all occupied positions '''
        return self.board_state[0] | self.board_state[1]

    def get_key(self):
        ''' returns unique game state identifier '''
        return self.get_mask() + self.board_state[self.get_current_player()]

    def can_play(self, col):
        ''' returns true if col (zero indexed) is playable '''
        return not self.get_mask() & 1 << (self.h + 1) * col + (self.h - 1)

    def play(self, col):
        player = self.get_current_player()
        move = 1 << self.col_heights[col]
        self.col_heights[col] += 1
        self.board_state[player] |= move
        self.history.append(col)
        self.moves += 1

    def backtrack(self):
        opp = self.get_opponent()
        col = self.history.pop()
        self.col_heights[col] -= 1
        move = 1 << (self.col_heights[col])
        self.board_state[opp] ^= move
        self.moves -= 1

    def winning_board_state(self):
        ''' returns true if last played column creates winning alignment '''
        opp = self.get_opponent()
        for shift in self.bit_shifts:
            test = self.board_state[opp] & (self.board_state[opp] >> shift)
            if test & (test >> 2 * shift):
                return True
        return False

    def get_score(self):
        ''' returns score of complete game (evaluated for winning opponent) '''
        return - (self.w * self.h + 1 - self.moves) // 2

    def __get_bit_shifts(self):
        return [
            1,              # | vertical
            self.h,         # \ diagonal
            self.h + 1,     # - horizontal
            self.h + 2      # / diagonal
        ]

    def __get_base_search_order(self):
        base_search_order = list(range(self.w))
        base_search_order.sort(key=lambda x: abs(self.w // 2 - x))
        return base_search_order

    def __col_sort(self, col):
        player = self.get_current_player()
        move = 1 << self.col_heights[col]
        count = 0
        state = self.board_state[player] | move

        for shift in self.bit_shifts:
            test = state & (state >> shift) & (state >> 2 * shift)
            if test:
                count += bin(test).count('1')

        return count
