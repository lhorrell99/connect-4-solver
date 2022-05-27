# A Perfect Connect 4 Solver in Python

## Introduction

After the [4-in-a-Robot](https://github.com/lhorrell99/4-in-a-robot) project led me down a wormhole, I wanted to see if I could implement a perfect solver for Connect 4 in Python. This readme documents the process of tuning and pruning a brute force minimax approach to solve progressively more complex game states.

### Solvers: perfect versus imperfect

4-in-a-Robot did not require a perfect solver - it just needed to beat any human opponent. Consequently, if it couldn't find a game-ending state after searching to a specified depth, 4-in-a-robot stopped exploring subsequent moves and returned a heuristic evaluation of the intermediate game state. This strategy is a powerful weapon in the fight against asymptotic complexity - it caps the maximum time the solver spends on any given move. Using this strategy, 4-in-a-Robot can still comfortably beat any human opponent (I've certainly never beaten it), but it does still lose if faced with a perfect solver.

So this perfect solver project exists solely to beat another project of mine at a kid's game... Was it worth the effort? Absolutely.

### [Standing on the shoulders of giants:](https://en.wikipedia.org/wiki/Standing_on_the_Shoulder_of_Giants) some great resources I've learnt from

- [Solving Connect 4](http://blog.gamesolver.org/solving-connect-four/01-introduction/) | *Pascal Pons, 2015*
- [Creating the (nearly) perfect Connect 4 bot](https://towardsdatascience.com/creating-the-perfect-connect-four-ai-bot-c165115557b0) | *Gilles Vandewiele, 2017*
- [John's Connect 4 playground](https://tromp.github.io/c4/c4.html) | *John Tromp, 2004*
- [Bitboards and Connect 4]() | *Dominikus Herzberg, 2016*

## Version 1: Minimax

A staple of all board game solvers, the minimax algorithm simulates thousands of future game states to find the path taken by 2 players with perfect strategic thinking. Game states (represented as nodes of the game tree) are evaluated by a scoring function, which the maximising player seeks to maximise (and the minimising player seeks to minimise). Since this is a perfect solver, heuristic evaluations of non-final game states are not included, and the algorithm only calculates a score once a terminal node is reached. 

A board's score is positive if the maximiser can win or negative if the minimiser can win. The magnitude of the score increases the earlier in the game it is achieved (favouring the fastest possible wins):

- A score of 2 implies the maximiser wins with his second to last stone
- A score of -1 implies the minimiser wins with his last stone
- A score of 0 implies a draw game

This solver uses a variant of minimax known as negamax. This simplified implementation can be used for zero-sum games, where one player's loss is exactly equal to another players gain (as is the case with this scoring system).

![](https://github.com/lhorrell99/Connect4Solver/blob/master/images/C4S%20Graphic%201.png)

###### Figure 1: minimax game tree containing a winning path ([modified from here](https://towardsdatascience.com/creating-the-perfect-connect-four-ai-bot-c165115557b0))

To solve the empty board, a brute force minimax approach would have to evaluate 4,531,985,219,092 game states. At 50,000 game states per second, that's nearly 3 years of computation. Time for some pruning...

## Version 2: Alpha-Beta Pruning

Alpha-beta pruning is the classic minimax optimisation. The principle is simple: At any point in the computation, two additional parameters are monitored (alpha and beta). At any node of the tree, alpha represents the min assured score for the maximiser, and beta the max assured score for the minimiser. They can be thought of as 'worst-case scenarios' for each player. If the maximiser ever reaches a node where beta < alpha, there is a guaranteed better score elsewhere in the tree, such that they need not search descendants of that node. This logic is also applicable for the minimiser.

## Version 3: Bitboards

Integral to any good solver is the right data structure. Up to this point, boards were represented by 2-dimensional NumPy arrays. These provided an intuitive and readable representation of any board state, but from an efficiency perspective, we can do better. The data structure I've used in the final solver uses a compact bitwise representation of states (in programming terms, this is as low-level as I've ever dared to venture...)

Using this binary representation, any board state can be fully encoded using 2 64-bit integers: the first stores the locations of one player's discs, and the second stores locations of the other player's discs.

![](https://github.com/lhorrell99/Connect4Solver/blob/master/images/C4S%20Graphic%202.png)

###### Figure 2: the indexing of bits to form a bitboard, with 0 as the rightmost bit ([modified from here](https://towardsdatascience.com/creating-the-perfect-connect-four-ai-bot-c165115557b0))

Note the sentinel row (6, 13, 20, 27, 34, 41, 48) in Figure 2, included to prevent false positives when checking for alignments of 4 connected discs. Using this structure, the game state above can be fully encoded as the two integers in figure 3.

![](https://github.com/lhorrell99/Connect4Solver/blob/master/images/C4S%20Graphic%203.png)

###### Figure 3: Encoding bitboards for a game state

The solver has to check for alignments of 4 connected discs after (almost) every move it makes, so it's a job that's worth doing efficiently. This is where bitboards really come into their own - checking for alignments is reduced to a few bitwise operations. We can also check the whole board for alignments in parallel, instead of having to check the area surrounding one specified location on the board - pretty neat.

## Version 4: Memoization

Borrowed from dynamic programming, a memoization cache trades increased memory requirements for decreased computation time. The scores of recently calculated boards are saved in memory, saving potentially lengthy recalculation if they recur along other branches of the game tree.

Alpha-beta pruning slightly complicates the transposition table implementation (since the score returned from a node is no longer necessarily its true value). Check [Wikipedia](https://en.wikipedia.org/wiki/Negamax) for a simple workaround to address this.

A simple Least Recently Used (LRU) cache (borrowed from the [Python docs](https://docs.python.org/3/library/collections.html#collections.OrderedDict)) evicts the least recently used result once it has grown to a specified size. This prevents the cache from growing unfeasibly large during a tricky computation.

## Version 5: Optimised Move Ordering

Alpha-beta works best when it finds a promising path through the tree early in the computation. This increases the number of branches that can be pruned (since the early result was near the optimal). At any point in a game of Connect 4, the most promising next move is unknown, so we return to the world of heuristic estimates. Any move ordering heuristic also needs to be pretty efficient, otherwise the overheads from running it quickly surpass the benefits of increased pruning.

The starting point for the improved move order is to simply arrange the columns from the middle out. Middle columns are more likely to produce alignments, so they are searched first. The neat thing about this approach is that it carries (effectively) zero overhead - the columns can be ordered from the middle out when the Board class initialises and then just referenced during the computation.

The second phase move ordering uses a slightly more targeted approach, in which each playable move is evaluated to see how many 3-disc alignments it produces (these have strong potential to create a winning alignment later). The code to do this is very similar to the winning alignment check, utilising a few bitwise operations. Any ties that arising from this approach are resolved by defaulting back to the initial middle out search order.

That's enough work on this solver for now. I've learnt a fair bit about algorithms and certainly polished up my Python. The solver is still not quite ready to take on solving the empty board though, so keep an eye out for some more optimisations one day soon...
