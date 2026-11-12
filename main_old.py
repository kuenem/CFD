import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--wind_speed", type=float, default=10.0, help="m/s RANGE ~ 0.1-100")
    parser.add_argument("--fluid_density", type=float, default=1.2, help="kg/m^3 RANGE ~ 1.2 @ 20°C - 1.3 @ cold or mountains for air, 998 or ~1000 for water")
    parser.add_argument("--fluid_kinematic_viscosity", type=float, default=1.5e-5, help="m^2/s RANGE ~ 1.5e-5 for air @ 20°C, 1e-6 for water")
    parser.add_argument("--cell_size", type=float, default=0.02, help="m RANGE ~ 0.001 - 0.5 RULE: Whole body >= 40 cells, smallest important feature >= 4 cells ")
    parser.add_argument("--domain_length", type=float, default=10.0, help="m IDEAL 3-5 length before and ~10 after the object")
    parser.add_argument("--domain_width", type=float, default=3.0, help="m model frontal area / tunnel cross section under 5%")
    parser.add_argument("--domain_height", type=float, default=3.0, help="m model frontal area / tunnel cross section under 5%")
    parser.add_argument("--lattice_speed", type=float, default=0.05, help="m/s RANGE 0.01 to 0.1 SMALLER = more accurate; #Steps ~ 1/lattice_speed")
    parser.add_argument("--smagorinsky_constant", type=float, default=0.17, help="RANGE 0.1-0.24; Lower = less artificial damping but less stable.")
    parser.add_argument("--flow_throughs_to_simulate", type=int, default=6, help="RANGE 5-10")
  