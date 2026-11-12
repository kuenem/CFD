# CFD Simulator: Six Pseudocode Variants

Nov 12, 2026

## 1. Plain-language version

The simulation fills a virtual wind tunnel with 11.25 million tiny boxes and repeats one short routine 60,000 times, until the push of the air on the rider stops changing.

**The picture**

- The tunnel is a 3D grid of boxes, each 2 cm wide: 150 × 150 × 500 boxes.
- Every box holds 19 “air buckets”, one per direction the air can move: stay put, 6 straight, 12 diagonal. A bucket stores how much air is heading that way.
- The rider is a block of boxes marked “solid”.

**One step, repeated 60,000 times**

1. **Look.** In every box, add up the buckets. The sum is how much air is there; the lean of the buckets is where it flows.
2. **Mix.** Nudge each bucket toward what perfectly settled air moving at that speed would look like. This nudge is what makes air “sticky”. Where air is sheared hard, nudge a bit more: that stands in for little whirls the boxes are too coarse to see.
3. **Move.** Every bucket empties into the neighbouring box it points to.
4. **Edges.** The front pushes in fresh wind, the back lets air out, the sides and ceiling let air slide along, and the floor and the rider bounce air back, so air stops at their surface.
5. **Count the push.** Each bounce off the rider hands it some momentum. Adding all bounces up gives the drag force. This runs only every \~200 steps, in the second half of the run.

**Why 6 laps.** Air crosses the 10 m tunnel in 10,000 steps (one “flow-through”). The first 3 flow-throughs let the start-up chaos settle; the last 3 are measured.

**Back to real units.** Inside, everything is counted in boxes and steps. At the end the push becomes newtons, then a “drag area” in m² (the flat plate that would feel the same push), then watts. A drag area of 0.30 m² at 10 m/s costs 180 W.

| Plain word | Technical term | In your code |
| --- | --- | --- |
| box | lattice cell | `x, y, z` |
| air bucket | population | `populations_now[i, x, y, z]` |
| nudge toward settled air | BGK collision | `relaxation_time` |
| whirl stand-in | Smagorinsky turbulence model | `smagorinsky_constant` |
| bounce | bounce-back | `cell_type == 1` |

## 2. Formula-true version

Every equation the simulation relies on, grouped by job; the loop around them is only a skeleton. Wind runs along x here, as in the pseudocode. Variants 4–6 use z, as in settings.py.

Symbols: U = `wind_speed`, ν = `fluid_kinematic_viscosity`, ρ\_phys = `fluid_density`, Δx = `cell_size`, u\_lb = `lattice_speed`, C\_s = `smagorinsky_constant`, L = 1.8 m (rider length). Without subscript, ρ is the lattice density (≈ 1). c\_i are the 19 direction arrows, f\_i the air amounts, ī the direction opposite to i.

**A · Units, once**

```latex
\begin{aligned}
\Delta t &= \frac{u_{lb}\,\Delta x}{U} \quad (= 10^{-4}\ \mathrm{s}) \\
\nu_{lb} &= \nu\,\frac{\Delta t}{\Delta x^{2}} \quad (= 3.75\cdot 10^{-6}) \\
\tau_0 &= \frac{\nu_{lb}}{c_s^{2}} + \frac{1}{2}, \quad c_s^{2}=\frac{1}{3} \quad (= 0.500011) \\
\mathrm{Ma} &= \frac{u_{lb}}{c_s} \quad (= 0.087) \\
\mathrm{Re} &= \frac{U L}{\nu} \quad (= 1.2\cdot 10^{6}) \\
N_{ft} &= \frac{L_{dom}/\Delta x}{u_{lb}}, \quad N_{tot} = n_{ft}\,N_{ft} \quad (= 10^{4},\ 6\cdot 10^{4})
\end{aligned}
```

**B · Lattice and start state**

```latex
\begin{aligned}
w_i &= \tfrac{1}{3}\ (i=0), \quad \tfrac{1}{18}\ (\text{6 axis}), \quad \tfrac{1}{36}\ (\text{12 diagonal}), \qquad \textstyle\sum_i w_i = 1 \\
f_i(\mathbf{x},0) &= f_i^{eq}\big(\rho=1,\ \mathbf{u}=(u_{lb},0,0)\big)
\end{aligned}
```

**C1 · Measure**

```latex
\rho=\sum_i f_i, \qquad \mathbf{u}=\frac{1}{\rho}\sum_i f_i\,\mathbf{c}_i
```

**C2 · Balance (equilibrium)**

```latex
f_i^{eq}=w_i\,\rho\left[1+3(\mathbf{c}_i\cdot\mathbf{u})+\tfrac{9}{2}(\mathbf{c}_i\cdot\mathbf{u})^{2}-\tfrac{3}{2}\,\mathbf{u}\cdot\mathbf{u}\right]
```

**C3 · Turbulence model (Smagorinsky, Δ = 1 cell)**

```latex
\begin{aligned}
\Pi_{ab} &= \sum_i c_{ia}c_{ib}\,\big(f_i-f_i^{eq}\big) \\
S_{ab} &= -\frac{3\,\Pi_{ab}}{2\,\rho\,\tau_0} \\
|S| &= \sqrt{2\,S_{ab}S_{ab}} \\
\nu_t &= C_s^{2}\,|S| \\
\tau_{eff} &= 3\,(\nu_{lb}+\nu_t)+\tfrac{1}{2}
\end{aligned}
```

**C4 · Mix (BGK collision)**

```latex
f_i \leftarrow f_i-\frac{f_i-f_i^{eq}}{\tau_{eff}}
```

**C5 · Move (streaming)**

```latex
f_i(\mathbf{x}+\mathbf{c}_i,\ t+1)=f_i(\mathbf{x},\ t)
```

**C6 · Edges**

```latex
\begin{aligned}
\text{solid, floor:}&\quad f_i \leftrightarrow f_{\bar i}, \qquad \mathbf{c}_{\bar i}=-\mathbf{c}_i \\
\text{inlet:}&\quad f_i = f_i^{eq}\big(1,\ (u_{lb},0,0)\big) \\
\text{outlet:}&\quad f_i(N)=f_i(N-1) \\
\text{sides, top (free-slip):}&\quad f_i = f_{i'}, \qquad \mathbf{c}_{i'}=\mathbf{c}_i-2(\mathbf{c}_i\cdot\mathbf{n})\,\mathbf{n}
\end{aligned}
```

**C7 · Drag (momentum exchange)**

```latex
F_{lb}=\sum_{\text{links}}2\,f_i^{*}\,c_{i,x}
```

Links are fluid cells touching a solid, with i pointing into the solid. f\* is the post-collision amount.

**D · Back to SI units**

```latex
\begin{aligned}
F &= F_{lb}\,\rho_{phys}\,\frac{\Delta x^{4}}{\Delta t^{2}} \\
C_dA &= \frac{2F}{\rho_{phys}\,U^{2}} \\
P &= \tfrac{1}{2}\,\rho_{phys}\,C_dA\,U^{3} \\
p &= c_s^{2}\,(\rho-1)\,\rho_{phys}\left(\frac{\Delta x}{\Delta t}\right)^{2}
\end{aligned}
```

**Skeleton around them**

```text
setup:  A (Δt, ν_lb, τ0)   ·   B (start state f = f_eq(1, u_in))
repeat N_tot times:
    C1  measure   → ρ, u
    C2  balance   → f_eq
    C3  turbulence → Π, S, ν_t, τ_eff
    C4  mix       → f
    C7  drag      → F_lb   (only if step ≥ 3·N_ft and step % 200 == 0)
    C5  move
    C6  edges
after loop: average F_lb over the last 3 flow-throughs → D
```

**Two notes on the pseudocode**

- **Drag timing.** The pseudocode evaluates the drag after streaming. By then, the fluid cell’s amount for a direction pointing into the solid has been replaced by the amount arriving from the other side. The wall-bound amount is the post-collision one, so the skeleton sums C7 between C4 and C5.
- **τ inside the strain.** C3 divides by τ\_0, but the stress belongs to τ\_eff. Solving that in closed form removes the S, |S|, ν\_t and τ\_eff lines and needs no iteration:

```latex
\tau_{eff}=\tfrac{1}{2}\left[\tau_0+\sqrt{\tau_0^{2}+18\sqrt{2}\,C_s^{2}\,\frac{\sqrt{\Pi_{ab}\Pi_{ab}}}{\rho}}\right]
```

The pseudocode version overestimates ν\_t by the factor τ\_eff / τ\_0, for example 10 % at τ\_eff = 0.55. Treat the closed form as an optional refinement.

## 3. Code A · snake\_case pseudocode

The whole simulation as Python-style pseudocode with the pseudocode’s own names, written over whole arrays (numpy style). I read “Snakecode” as snake\_case, indentation-based code. Axes follow the pseudocode: x is the wind direction. It is a readable model, not a tested script; each line maps to one formula in variant 2.

```python
import numpy as np

# ---------- PART 0 · chosen values (SI) ----------
wind_speed = 10.0                     # m/s
fluid_density = 1.2                   # kg/m^3
fluid_kinematic_viscosity = 1.5e-5    # m^2/s
cell_size = 0.02                      # m
domain_length, domain_width, domain_height = 10.0, 3.0, 3.0   # m
characteristic_length = 1.8           # m, rider length (Reynolds number)
lattice_speed = 0.05                  # cells per step
smagorinsky_constant = 0.1
flow_throughs_to_simulate = 6

# ---------- PART 1 · derived values ----------
time_step = lattice_speed * cell_size / wind_speed                         # s per step
lattice_viscosity = fluid_kinematic_viscosity * time_step / cell_size**2   # cells^2 per step
speed_of_sound_squared = 1 / 3
relaxation_time = lattice_viscosity / speed_of_sound_squared + 0.5
reynolds_number = wind_speed * characteristic_length / fluid_kinematic_viscosity
steps_per_flow_through = round(domain_length / cell_size) / lattice_speed
total_steps = round(flow_throughs_to_simulate * steps_per_flow_through)

nx = round(domain_length / cell_size)     # x = wind axis
ny = round(domain_width / cell_size)
nz = round(domain_height / cell_size)

direction_arrows, direction_weights = d3q19()     # (19, 3) int, (19,) float

def index_of(arrows):                             # which of the 19 directions has this arrow?
    return np.array([np.where((direction_arrows == a).all(axis=1))[0][0] for a in arrows])

opposite_direction = index_of(-direction_arrows)                  # (19,)
mirror_y = index_of(direction_arrows * np.array([1, -1, 1]))      # y-component flipped
mirror_z = index_of(direction_arrows * np.array([1, 1, -1]))      # z-component flipped

# ---------- PART 2 · building blocks ----------
def equilibrium(density, velocity):
    # what settled air with this density and velocity would look like
    alignment = np.einsum('ia,a...->i...', direction_arrows, velocity)
    speed_squared = (velocity ** 2).sum(axis=0)
    weights = direction_weights.reshape(19, *[1] * np.ndim(density))
    return weights * density * (1 + 3 * alignment + 4.5 * alignment ** 2 - 1.5 * speed_squared)

def measure(air_amounts):                                         # A
    density = air_amounts.sum(axis=0)
    velocity = np.einsum('ia,ixyz->axyz', direction_arrows, air_amounts) / density
    return density, velocity

def mix(air_amounts, density, velocity):                          # B + B2
    balanced_amount = equilibrium(density, velocity)
    off_balance = air_amounts - balanced_amount
    stress = np.einsum('ia,ib,ixyz->abxyz', direction_arrows, direction_arrows, off_balance)
    strain = -3 * stress / (2 * density * relaxation_time)
    strain_magnitude = np.sqrt(2 * (strain ** 2).sum(axis=(0, 1)))
    turbulent_viscosity = smagorinsky_constant ** 2 * strain_magnitude
    effective_relaxation_time = 3 * (lattice_viscosity + turbulent_viscosity) + 0.5
    return air_amounts - off_balance / effective_relaxation_time

def push_on_model(air_amounts):                                   # E, run BEFORE move()
    force_along_wind = 0.0
    for i, arrow in enumerate(direction_arrows):
        if arrow[0] == 0:
            continue
        # fluid cells whose neighbour in direction i is solid
        points_into_solid = np.roll(is_solid, shift=tuple(-arrow), axis=(0, 1, 2)) & ~is_solid
        force_along_wind += 2 * air_amounts[i][points_into_solid].sum() * arrow[0]
    return force_along_wind

def move(air_amounts):                                            # C
    for i, arrow in enumerate(direction_arrows):
        air_amounts[i] = np.roll(air_amounts[i], shift=tuple(arrow), axis=(0, 1, 2))

def apply_edges(air_amounts):                                     # D
    air_amounts[:, is_solid] = air_amounts[opposite_direction][:, is_solid]   # bounce-back
    air_amounts[:, 0, :, :] = inlet_amounts[:, None, None]                    # inlet
    air_amounts[:, -1, :, :] = air_amounts[:, -2, :, :]                       # outlet
    air_amounts[:, :, 0, :] = air_amounts[mirror_y, :, 1, :]                  # side wall, free-slip
    air_amounts[:, :, -1, :] = air_amounts[mirror_y, :, -2, :]                # side wall, free-slip
    air_amounts[:, :, :, -1] = air_amounts[mirror_z, :, :, -2]                # ceiling, free-slip
    # floor: is_solid[:, :, 0] is True, so it bounces back like the model

# ---------- PART 2 · main loop ----------
is_solid = voxelize('model.stl')                  # bool (nx, ny, nz), floor layer included
inlet_amounts = equilibrium(1.0, np.array([lattice_speed, 0.0, 0.0]))        # (19,)
air_amounts = np.tile(inlet_amounts[:, None, None, None], (1, nx, ny, nz))    # start with moving air

drag_samples = []
for step in range(total_steps):
    density, velocity = measure(air_amounts)                      # A
    air_amounts = mix(air_amounts, density, velocity)             # B
    if step >= 3 * steps_per_flow_through and step % 200 == 0:    # E
        drag_samples.append(push_on_model(air_amounts))
    move(air_amounts)                                             # C
    apply_edges(air_amounts)                                      # D

# ---------- PART 3 · real numbers ----------
average_force_along_wind = np.mean(drag_samples)
drag_force_in_newtons = average_force_along_wind * fluid_density * cell_size**4 / time_step**2
drag_area = 2 * drag_force_in_newtons / (fluid_density * wind_speed**2)
power_in_watts = 0.5 * fluid_density * drag_area * wind_speed**3
pressure_in_pascals = speed_of_sound_squared * (density - 1) * fluid_density * (cell_size / time_step)**2
```

Three differences from the pseudocode: the drag sum runs between mixing and moving (see the notes in variant 2), the floor is a solid layer instead of a special case, and every step works on whole arrays instead of one cell at a time.

## 4. Code B · following your existing files

The pseudocode spread over your five files, with your names. Axes follow settings.py: `nx` = width, `ny` = height, `nz` = length, so the wind runs along z, the third index. Inlet at z = 0, outlet at z = nz − 1, floor at y = 0, ceiling at y = ny − 1, side walls at x = 0 and x = nx − 1. The sketches are untested; `one_time_step` is the part to test first.

| File | Now | Change |
| --- | --- | --- |
| `settings.py` | matches Parts 0–1 | add `drag_interval`, `force_scale`, `drag_start_step` |
| `lattice.py` | arrows, weights, opposite ✓ | add `mirror_x`, `mirror_y`, `equilibrium` |
| `main.py` | complete | decide the Smagorinsky default: 0.17 here, 0.1 in the pseudocode |
| `kernels.py` | stub (`continue`) | the whole body of `one_time_step` |
| `simulation.py` | buffers + swap | start state, geometry, boundaries, drag, results |
| `results.py` | new | Part 3 conversions |

**settings.py** (additions only)

```python
    drag_interval: int = 200   # steps between drag samples (add to the chosen values)

    # ---- derived values (add to the field(init=False) block) ----
    force_scale: float = field(init=False)       # lattice force -> newton
    drag_start_step: int = field(init=False)     # first 3 flow-throughs wash out the start

    # ---- inside derive_values() ----
    self.force_scale = self.fluid_density * self.cell_size**4 / self.time_step**2
    self.drag_start_step = int(3 * self.steps_per_flow_through)
```

**lattice.py** (additions only)

```python
def mirrored_directions(axis):
    flipped = direction_arrows.copy()
    flipped[:, axis] *= -1
    return np.array([np.where((direction_arrows == arrow).all(axis=1))[0][0] for arrow in flipped])

mirror_x = mirrored_directions(0)   # side walls (free-slip)
mirror_y = mirrored_directions(1)   # ceiling (free-slip)


def equilibrium(density, velocity):
    # one cell, numpy: start state, inlet, tests. The kernel has its own per-cell copy.
    velocity = np.asarray(velocity, dtype=np.float32)
    alignment = direction_arrows @ velocity
    speed_squared = velocity @ velocity
    return direction_weights * density * (1 + 3 * alignment + 4.5 * alignment**2 - 1.5 * speed_squared)
```

**kernels.py**

```python
import numpy as np
from numba import njit, prange
from lattice import direction_arrows, direction_weights, opposite_directions  # numba freezes these as constants


@njit(parallel=True, fastmath=True, cache=True)
def one_time_step(populations_now, populations_next, cell_type, relaxation_time,
                  smagorinsky_constant, force_per_slice, measure_drag):
    nx, ny, nz = cell_type.shape  # read the size from the array, not from globals
    lattice_viscosity = (relaxation_time - 0.5) / 3.0
    for x in prange(1, nx - 1):
        arriving = np.empty((19,), dtype=np.float32)
        balanced = np.empty((19,), dtype=np.float32)
        slice_force = 0.0
        for y in range(1, ny - 1):
            for z in range(1, nz - 1):
                if cell_type[x, y, z] == 1:
                    continue  # Skip solid cells

                # C + D. move (pull) and bounce back: take what arrives from each neighbour
                for i in range(19):
                    sx = x - direction_arrows[i, 0]
                    sy = y - direction_arrows[i, 1]
                    sz = z - direction_arrows[i, 2]
                    if cell_type[sx, sy, sz] == 1:
                        arriving[i] = populations_now[opposite_directions[i], x, y, z]
                    else:
                        arriving[i] = populations_now[i, sx, sy, sz]

                # A. measure
                density = 0.0
                momentum_x = 0.0
                momentum_y = 0.0
                momentum_z = 0.0
                for i in range(19):
                    density += arriving[i]
                    momentum_x += arriving[i] * direction_arrows[i, 0]
                    momentum_y += arriving[i] * direction_arrows[i, 1]
                    momentum_z += arriving[i] * direction_arrows[i, 2]
                ux = momentum_x / density
                uy = momentum_y / density
                uz = momentum_z / density
                speed_squared = ux * ux + uy * uy + uz * uz

                # B. balanced amounts and off-balance stress
                pxx = 0.0
                pyy = 0.0
                pzz = 0.0
                pxy = 0.0
                pxz = 0.0
                pyz = 0.0
                for i in range(19):
                    cx = direction_arrows[i, 0]
                    cy = direction_arrows[i, 1]
                    cz = direction_arrows[i, 2]
                    alignment = cx * ux + cy * uy + cz * uz
                    balanced[i] = direction_weights[i] * density * (
                        1.0 + 3.0 * alignment + 4.5 * alignment * alignment - 1.5 * speed_squared)
                    off = arriving[i] - balanced[i]
                    pxx += cx * cx * off
                    pyy += cy * cy * off
                    pzz += cz * cz * off
                    pxy += cx * cy * off
                    pxz += cx * cz * off
                    pyz += cy * cz * off

                # B2. turbulence model
                strain_factor = -3.0 / (2.0 * density * relaxation_time)
                strain_squared = strain_factor * strain_factor * (
                    pxx * pxx + pyy * pyy + pzz * pzz + 2.0 * (pxy * pxy + pxz * pxz + pyz * pyz))
                strain_magnitude = np.sqrt(2.0 * strain_squared)
                turbulent_viscosity = smagorinsky_constant * smagorinsky_constant * strain_magnitude
                effective_relaxation_time = 3.0 * (lattice_viscosity + turbulent_viscosity) + 0.5

                # B. mix and write; E. drag from the post-collision amounts (wind axis = z)
                for i in range(19):
                    after = arriving[i] - (arriving[i] - balanced[i]) / effective_relaxation_time
                    populations_next[i, x, y, z] = after
                    if measure_drag and cell_type[x + direction_arrows[i, 0],
                                                  y + direction_arrows[i, 1],
                                                  z + direction_arrows[i, 2]] == 1:
                        slice_force += 2.0 * after * direction_arrows[i, 2]
        force_per_slice[x] = slice_force  # each thread writes only its own slot: no race
```

**simulation.py**

```python
import numpy as np
from kernels import one_time_step
from lattice import equilibrium, mirror_x, mirror_y
from results import to_real_units


def create_arrays(settings):
    ...  # unchanged


def initialise(populations_now, populations_next, settings):
    # start with moving air; np.empty leaves garbage that would be pulled into the interior
    inlet_amounts = equilibrium(1.0, (0.0, 0.0, settings.lattice_speed)).astype(np.float32)  # (19,)
    populations_now[:] = inlet_amounts[:, None, None, None]
    populations_next[:] = inlet_amounts[:, None, None, None]


def build_geometry(cell_type, settings):
    cell_type[:, 0, :] = 1                      # floor at y = 0 bounces back like the model
    # cell_type[voxelised_model] = 1            # the rider, from the voxelised 3D model


def apply_boundaries(populations_next):
    # inlet (z = 0) keeps its start value: the kernel never writes the outer layer
    populations_next[:, :, :, -1] = populations_next[:, :, :, -2]        # outlet: zero gradient
    populations_next[:, 0, :, :] = populations_next[mirror_x, 1, :, :]   # side walls: free-slip
    populations_next[:, -1, :, :] = populations_next[mirror_x, -2, :, :]
    populations_next[:, :, -1, :] = populations_next[mirror_y, :, -2, :] # ceiling: free-slip


def run_simulation(settings):
    populations_now, populations_next, cell_type = create_arrays(settings)
    build_geometry(cell_type, settings)
    initialise(populations_now, populations_next, settings)
    force_per_slice = np.zeros(settings.nx, dtype=np.float64)
    drag_samples = []

    progress_interval = max(1, settings.total_steps // 100)
    for i in range(settings.total_steps):
        # (progress print unchanged)
        measure_drag = i >= settings.drag_start_step and i % settings.drag_interval == 0
        one_time_step(populations_now, populations_next, cell_type, settings.relaxation_time,
                      settings.smagorinsky_constant, force_per_slice, measure_drag)
        apply_boundaries(populations_next)
        if measure_drag:
            drag_samples.append(force_per_slice.sum())
        # the new values become the current ones for the next step
        populations_now, populations_next = populations_next, populations_now

    return to_real_units(settings, np.mean(drag_samples))
```

**results.py** (new)

```python
def to_real_units(settings, average_force_lattice):
    drag_force_in_newtons = average_force_lattice * settings.force_scale
    drag_area = 2 * drag_force_in_newtons / (settings.fluid_density * settings.wind_speed**2)
    power_in_watts = 0.5 * settings.fluid_density * drag_area * settings.wind_speed**3
    return drag_force_in_newtons, drag_area, power_in_watts


def pressure_in_pascals(settings, lattice_density):
    return (settings.speed_of_sound_squared * (lattice_density - 1)
            * settings.fluid_density * (settings.cell_size / settings.time_step)**2)
```

The kernel is written as pull streaming: each cell reads from its neighbours, which fits your `arriving` scratch array and lets every `prange` thread write only its own cells. Bounce-back becomes “read my own opposite amount instead”, so solid cells never need updating.

## 5. Code C · next steps in your syntax

Eight small steps take `kernels.py` from stub to a drag number, each with a check that can fail on its own. The code for every step is in variant 4; this section is the order and the checks.

**Decide three things first**

1. **Wind axis: keep z.** settings.py already puts the length on the third index, and in `(19, nx, ny, nz)` that is the contiguous axis.
2. **Smagorinsky default.** `main.py` and `settings.py` say 0.17, the pseudocode says 0.1. Eddy viscosity scales with C², so 0.17 adds 2.9 times more. Pick one on purpose.
3. **Drag timing.** Sum the force right after the mix, not after streaming (notes in variant 2).

**Develop on a small tunnel**

```python
small = Settings(cell_size=0.05, domain_length=4.0, domain_width=1.2, domain_height=1.2)  # 24 × 24 × 80 cells


def diagnostics(populations, cell_type):   # add to simulation.py
    fluid = cell_type == 0
    density = populations.sum(axis=0)
    velocity = np.stack([np.tensordot(direction_arrows[:, a], populations, axes=(0, 0))
                         for a in range(3)]) / density
    speed = np.sqrt((velocity ** 2).sum(axis=0))
    return {
        'has_nan': bool(np.isnan(density[fluid]).any()),
        'density_min_max': (float(density[fluid].min()), float(density[fluid].max())),  # healthy 0.97 to 1.03
        'speed_max': float(speed[fluid].max()),                                         # healthy below 0.15
    }
```

**Steps**

1. **Start state.** Add `equilibrium` to lattice.py and `initialise` to simulation.py. Your `np.empty` buffers hold garbage until then.
   - Check: `diagnostics` shows density 1.0 everywhere and no NaN.
2. **Stream only.** In `one_time_step`, remove the `continue` stub inside the direction loop. Keep the pull loop and write `populations_next[i, x, y, z] = arriving[i]`.
   - Check: put 1.0 in `populations_now[1, 10, 10, 10]` (direction +x). After one step it sits at `populations_next[1, 11, 10, 10]`. Total mass stays constant for 100 steps.
3. **Measure and mix with constant τ.** Add the A and B blocks and set `effective_relaxation_time = relaxation_time`. Leave B2 out.
   - Check: empty tunnel, uniform start. After 200 steps density is still 1.0 and `uz` is still 0.05.
4. **Boundaries.** Add `mirror_x`, `mirror_y` and `apply_boundaries`.
   - Check: empty tunnel, 2 flow-throughs. Density stays inside 0.99–1.01 and `uz` stays close to 0.05 away from the floor.
5. **Solid.** Put a box or sphere into `cell_type` in `build_geometry`.
   - Check: set `populations_now` to NaN inside the solid before step 1 of the run. No NaN may reach the fluid, because the pull loop never reads solid cells.
6. **Smagorinsky.** Add the B2 block back.
   - Check: `smagorinsky_constant=0` reproduces step 5 (`np.allclose`). With 0.1 and τ₀ ≈ 0.50001, density stays inside 0.97–1.03 for one flow-through.
7. **Drag.** Add `force_per_slice`, `measure_drag` and results.py. Test with a sphere of 0.2 m diameter (10 cells).
   - Check: C\_d ≈ 0.47, so C\_dA ≈ 0.0148 m² and `force_per_slice.sum()` ≈ 0.046. Within ±30 % is a good first result on this coarse grid.
8. **Scale up.** Time one step on the full 150 × 150 × 500 grid and multiply by 60,000.
   - Check: two buffers need about 1.7 GB (0.86 GB each, float32). The full run is 6.75 · 10¹¹ cell updates.

**Small things to fix on the way**

- `fastmath=True` lets numba assume there is no NaN or inf, so an `np.isnan` test inside the kernel can be optimised away. Use `diagnostics` outside the kernel, or drop `fastmath` while debugging.
- Use `round(...)` instead of `int(...)` for `total_steps`, so a value like 59,999.99999 cannot lose a step.
- The comment on `smagorinsky_constant` in settings.py ends in a stray `as_integer_ratio`.

**Later, not now**

- Moving floor that slides at `wind_speed`.
- Zou–He inlet instead of the fixed equilibrium.
- The closed-form τ\_eff from variant 2.
- Output: ρ and u are not stored, so compute them from the populations for plots and save slices only.

## 6. Compact combined version

One loop does everything: each step turns the 19 air amounts per cell into new ones with seven rules, and a few formulas decide how sticky, how turbulent and how large the results come out. Symbols are those of variant 2; names are those of your code.

**Data you hold**

| Name | Shape | dtype | Meaning |
| --- | --- | --- | --- |
| `populations_now`, `populations_next` | `(19, nx, ny, nz)` | float32 | air amount per direction per cell; 0.86 GB each at 150 × 150 × 500 |
| `cell_type` | `(nx, ny, nz)` | uint8 | 0 fluid, 1 solid (floor and rider) |
| `direction_arrows` | `(19, 3)` | int8 | arrow c\_i of each direction |
| `direction_weights` | `(19,)` | float32 | weight w\_i |
| `opposite_directions`, `mirror_x`, `mirror_y` | `(19,)` | int | index of the reversed or mirrored direction |
| `force_per_slice` | `(nx,)` | float64 | push on the model per x-slice, lattice units |
| `settings.*` | scalars | float, int | every chosen and derived number |

Density, velocity and stress are never stored. They live in the kernel as scalars: `density`, `ux`, `uy`, `uz`, `pxx` … `pyz`.

**One step, seven rules.** Your kernel pulls first, so inside it the order is 5, 1, 2, 3, 4, 7. One full cycle is the same.

**1 · Look.** Add up the 19 amounts: the total is how much air is there, the lean is where it flows.

```latex
\rho=\sum_i f_i, \qquad \mathbf{u}=\tfrac{1}{\rho}\sum_i f_i\,\mathbf{c}_i
```

*Impact:* healthy density is 0.97–1.03 and speed stays below 0.15. Outside that, the lattice speed is too high.

*Code:* `density` and `ux, uy, uz`, summed from `arriving[19]`.

**2 · Settle.** Work out what calm air with this density and velocity would look like.

```latex
f_i^{eq}=w_i\,\rho\left[1+3(\mathbf{c}_i\cdot\mathbf{u})+\tfrac{9}{2}(\mathbf{c}_i\cdot\mathbf{u})^{2}-\tfrac{3}{2}\,\mathbf{u}\cdot\mathbf{u}\right]
```

*Impact:* the error grows with u², which is why `lattice_speed` stays at or below 0.1 (Mach 0.087 at 0.05).

*Code:* `balanced[19]`, built with `direction_weights[i]`.

**3 · Sticky and turbulent.** The distance from settled air measures how hard the air is sheared, and that sets the extra viscosity.

```latex
\begin{aligned}
\Pi_{ab}&=\sum_i c_{ia}c_{ib}\,(f_i-f_i^{eq}), \qquad |S|=\frac{3}{2\rho\,\tau_0}\sqrt{2\,\Pi_{ab}\Pi_{ab}} \\
\nu_t&=C_s^{2}\,|S|, \qquad \tau_{eff}=3\,(\nu_{lb}+\nu_t)+\tfrac{1}{2}
\end{aligned}
```

*Impact:* air is almost not sticky at this Reynolds number: τ₀ = 0.500011, only 1.1 · 10⁻⁵ above the stability limit of 0.5. This rule lifts τ\_eff where the air shears, and C\_s² sets by how much: 0.17 instead of 0.1 gives 2.9 times more.

*Code:* `pxx` … `pyz`, `strain_magnitude`, `turbulent_viscosity`, `effective_relaxation_time`, with `smagorinsky_constant`.

**4 · Mix.** Move every amount a fraction 1 / τ\_eff of the way toward settled.

```latex
f_i^{*}=f_i-\frac{f_i-f_i^{eq}}{\tau_{eff}}
```

*Impact:* a τ\_eff near 0.5 means almost no viscosity and an unstable run; larger values smooth the flow.

*Code:* `populations_next[i, x, y, z] = arriving[i] - (arriving[i] - balanced[i]) / effective_relaxation_time`

**5 · Move and bounce.** Each amount shifts one cell along its arrow. Next to a solid it turns around instead.

```latex
f_i(\mathbf{x},t+1)=\begin{cases} f_i^{*}(\mathbf{x}-\mathbf{c}_i,\,t) & \text{neighbour is fluid} \\ f_{\bar i}^{*}(\mathbf{x},\,t) & \text{neighbour is solid} \end{cases}
```

*Impact:* the wall sits halfway between two cells, so a feature thinner than about 4 cells blurs. That is the smallest-part rule behind `cell_size`.

*Code:* `cell_type[sx, sy, sz] == 1` picks `populations_now[opposite_directions[i], x, y, z]`, otherwise `populations_now[i, sx, sy, sz]`.

**6 · Edges.** Inlet: fixed wind. Outlet: copy the layer in front. Sides and ceiling: mirror, so air slides. Floor: solid layer.

*Impact:* a blockage under 5 % (0.4 / 9 = 4.4 %) and a far outlet keep the walls out of the drag. With 3 m in front and 7 m behind, trust A-versus-B comparisons, not the absolute number.

*Code:* `apply_boundaries(populations_next)` after the kernel. The inlet layer at z = 0 is set once in `initialise`.

**7 · Push.** Every amount that hits the rider hands it twice its momentum. Add up the part along the wind, then convert.

```latex
F_{lb}=\sum_{\text{links}}2\,f_i^{*}\,c_{i,z}, \qquad F=F_{lb}\,\rho_{phys}\frac{\Delta x^{4}}{\Delta t^{2}}, \qquad C_dA=\frac{2F}{\rho_{phys}U^{2}}, \qquad P=\tfrac{1}{2}\rho_{phys}\,C_dA\,U^{3}
```

*Impact:* `settings.force_scale` is 19.2 N per lattice unit here. So C\_dA = 0.30 m² means F\_lb ≈ 0.94, F = 18 N and P = 180 W at 10 m/s.

*Code:* `slice_force += 2.0 * after * direction_arrows[i, 2]`, taken right after rule 4. Then `force_per_slice.sum()` and `to_real_units(settings, np.mean(drag_samples))`.

**Numbers that tell you something is wrong**

| Quantity | Healthy | If outside |
| --- | --- | --- |
| density | 0.97–1.03 | Mach too high: lower `lattice_speed` |
| speed | below 0.15 | same |
| `relaxation_time` | above 0.5 | negative viscosity, the run explodes |
| C\_dA of a rider | 0.20–0.25 m² time trial, 0.30–0.35 road, 0.40+ upright | check geometry and units |
