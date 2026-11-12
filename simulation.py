import numpy as np
from kernels import one_time_step


def create_arrays(settings):
    shape = (19, settings.nx, settings.ny, settings.nz)
    populations_now  = np.empty(shape, dtype=np.float32)
    populations_next = np.empty(shape, dtype=np.float32)
    cell_type = np.zeros(shape[1:], dtype=np.uint8)   # 0 = fluid
    return populations_now, populations_next, cell_type


def run_simulation(settings):
    populations_now, populations_next, cell_type = create_arrays(settings)

    progress_interval = max(1, settings.total_steps // 100)
    for i in range(settings.total_steps):
        if i % progress_interval == 0:
            print(f"Step progress: {(i/settings.total_steps * 100):.2f}%")
        one_time_step(populations_now, populations_next, cell_type, settings.relaxation_time, settings.smagorinsky_constant)
        # the new values become the current ones for the next step
        populations_now, populations_next = populations_next, populations_now
