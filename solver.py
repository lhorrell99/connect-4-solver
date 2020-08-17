from collections import OrderedDict


class LRUCache(OrderedDict):
    # limit size, removing the least recently used key when full
    # source: https://docs.python.org/3/library/collections

    def __init__(self, maxsize=128, *args, **kwds):
        self.maxsize = maxsize
        super().__init__(*args, **kwds)

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]


def get_tt_entry(value, UB=False, LB=False):
    return {'value': value, 'UB': UB, 'LB': LB}


def solve(board):
    TT = LRUCache(4096)

    def recurse(alpha, beta):
        alpha_original = alpha

        # transposition table lookup
        if board.get_key() in TT:
            entry = TT[board.get_key()]
            if entry['LB']:
                alpha = max(alpha, entry['value'])  # lower bound stored in TT
            elif entry['UB']:
                beta = min(beta, entry['value'])    # upper bound stored in TT
            else:
                return entry['value']               # exact value stored in TT
            if alpha >= beta:
                return entry['value']               # cut-off (from TT)

        # negamax implementation
        if board.winning_board_state():
            return board.get_score()        # base case 1: winning alignment
        elif board.moves == board.w * board.h:
            return 0                        # base case 2: draw game
        value = -board.w * board.h
        for col in board.get_search_order():
            board.play(col)
            value = max(value, -recurse(-beta, -alpha))
            board.backtrack()
            alpha = max(alpha, value)
            if alpha >= beta:
                break                   # alpha cut-off

        # transposition table storage
        if value <= alpha_original:
            TT[board.get_key()] = get_tt_entry(value, UB=True)
        elif value >= beta:
            TT[board.get_key()] = get_tt_entry(value, LB=True)
        else:
            TT[board.get_key()] = get_tt_entry(value)       # store exact in TT

        return value
    return recurse(-1e9, 1e9)
