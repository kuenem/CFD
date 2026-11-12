from dataclasses import dataclass, field


@dataclass
class Settings:
    # ---- values you choose (SI units) ----
    # Defaults and RANGE comments live in main.py (argparse), so there is
    # only one place to change them.
    wind_speed: float = 10.0 # m/s RANGE ~ 0.1-100
    fluid_density: float = 1.2 # kg/m^3 RANGE ~ 1.2 @ 20°C - 1.3 @ cold or mountains for air, 998 or ~1000 for water
    fluid_kinematic_viscosity: float = 1.5e-5 # m^2/s RANGE ~ 1.5e-5 for air @ 20°C, 1e-6 for water
    cell_size: float = 0.02 # m RANGE ~ 0.001 - 0.5 RULE: Whole body >= 40 cells, smallest important feature >= 4 cells 
    # Wind tunnel dimensions
    domain_length: float = 10.0  # m IDEAL 3-5 length before and ~10 after the object
    domain_width: float = 3.0 # m model frontal area / tunnel cross section under 5%
    domain_height: float = 3.0 # m model frontal area / tunnel cross section under 5%
    characteristic_length: float = 1.8
    # Lattice Mach number = lattice_speed / sqrt(1/3) = 0.087 KEEP Mach under 0.1 max. 0.3
    lattice_speed: float = 0.05 # RANGE 0.01 to 0.1 SMALLER = more accurate; #Steps ~ 1/lattice_speed
    smagorinsky_constant: float = 0.17 # RANGE 0.1-0.24; Lower = less artificial damping but less stable.as_integer_ratio
    # One flow-through = air travels through the whole tunnel once.
    flow_throughs_to_simulate: int = 6 # A few to wash out the start up last to average RANGE 5-10

    # ---- derived values (filled in automatically, never set by hand) ----
    time_step: float = field(init=False)
    lattice_viscosity: float = field(init=False)
    speed_of_sound_squared: float = field(init=False)
    relaxation_time: float = field(init=False)
    reynolds_number: float = field(init=False)
    steps_per_flow_through: float = field(init=False)
    total_steps: int = field(init=False)
    nx: int = field(init=False)
    ny: int = field(init=False)
    nz: int = field(init=False)

    def __post_init__(self):
        # Runs right after the chosen values are set, so a Settings object
        # can never exist with missing or outdated derived values.
        self.derive_values()

    def derive_values(self):
        self.time_step = self.lattice_speed * self.cell_size / self.wind_speed # seconds per loop
        self.lattice_viscosity = self.fluid_kinematic_viscosity * self.time_step / (self.cell_size * self.cell_size) # lattice units
        self.speed_of_sound_squared = 1.0 / 3.0 # D3Q19 fixed value
        self.relaxation_time = self.lattice_viscosity / self.speed_of_sound_squared + 0.5 # Chapman-Enskog expansion, must be > 0.5 for stability
        self.reynolds_number = self.wind_speed * self.characteristic_length / self.fluid_kinematic_viscosity # dimensionless, for reference only
        self.steps_per_flow_through = round(self.domain_length / self.cell_size) / self.lattice_speed # dimensionless
        self.total_steps = int(self.steps_per_flow_through * self.flow_throughs_to_simulate) # number of loops to run

        self.nx = round(self.domain_width / self.cell_size)
        self.ny = round(self.domain_height / self.cell_size)
        self.nz = round(self.domain_length / self.cell_size)
