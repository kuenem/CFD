import numpy as np
from numba import njit, prange


@njit(parallel=True, fastmath=True, cache=True)
def one_time_step(populations_now, populations_next, cell_type, relaxation_time, smagorinsky_constant):
    nx, ny, nz = cell_type.shape  # read the size from the array, not from globals
    for x in prange(1, nx - 1):
        arriving = np.empty((19,), dtype=np.float32)
        for y in range(1, ny - 1):
            for z in range(1, nz - 1):
                if cell_type[x, y, z] == 1:
                    continue  # Skip solid cells
                for direction in range(19):
                    neighbor = (x, y ,z) - direction_arrows[direction]
                    if cell_type[neighbor] is SOLID or FLOOR:
                        # Bounce-back for solid cells
                        arriving[direction] = populations_now[opposite_directions[direction], x, y, z] # bounce-back: air hitting a surface returns the way it came
                    continue


def equilibrium(direction, density, velocity_x, velocity_y, velocity_z):
    # Placeholder for the actual equilibrium distribution function
    return 0.0