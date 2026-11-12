import numpy as np

# Fixed properties of the D3Q19 grid (19 directions per cell).

FLUID = 0       # normal air
SOLID = 1       # the model (rider, drone): bounce-back, counted for drag
INLET = 2       # layer z = 0: fixed wind, never changes
OUTLET = 3      # layer z = nz-1: copy of the layer before it
SLIP_WALL = 4   # ceiling (y = ny-1), side walls (x = 0, nx-1)
FLOOR = 5       # y = 0: bounce-back (sticks), NOT counted for drag

direction_arrows = np.array([
    # Rest vector
    [0, 0, 0],

    # Six axis directions
    [ 1, 0, 0],
    [-1, 0, 0],
    [ 0, 1, 0],
    [ 0,-1, 0],
    [ 0, 0, 1],
    [ 0, 0,-1],

    # Twelve diagonal directions
    [ 1, 1, 0],
    [-1, 1, 0],
    [ 1,-1, 0],
    [-1,-1, 0],

    [ 1, 0, 1],
    [-1, 0, 1],
    [ 1, 0,-1],
    [-1, 0,-1],

    [ 0, 1, 1],
    [ 0,-1, 1],
    [ 0, 1,-1],
    [ 0,-1,-1]
], dtype=np.int8)
direction_weights = np.array([
    1/3,

    # Six axis directions
    1/18, 1/18, 1/18,
    1/18, 1/18, 1/18,

    # Twelve diagonal directions
    1/36, 1/36, 1/36, 1/36,
    1/36, 1/36, 1/36, 1/36,
    1/36, 1/36, 1/36, 1/36
], dtype=np.float32)
opposite_directions = np.array([
    np.where((direction_arrows == -arrow).all(axis=1))[0][0]
    for arrow in direction_arrows])
