from board import Board
from solver import solve
from math import floor
from time import time

raw_file = open('./tests_and_drafts/end_easy.txt', 'r')

data = raw_file.readlines()

for i in range(len(data)):
    data[i] = data[i].split()     # split on whitespace
    data[i][1] = int(data[i][1])  # string to int

raw_file.close()

print('number of samples:', len(data))
print('running test...')

incorrect_eval = False
start = time()
for i in range(len(data)):  # NOTE: CHECK BEFORE RUNNING
    test_board = Board()
    for col in data[i][0]:
        test_board.play(int(col) - 1)
    result = solve(test_board)
    if result != data[i][1]:
        incorrect_eval = True
end = time()

if incorrect_eval:
    print('!! something broke - scores wrong !!')
else:
    print('scores all good')

print('elapsed time:', end - start)
