from parcels import Grid, Particle, JITParticle
from parcels import AdvectionRK4, AdvectionEE, AdvectionRK45
from argparse import ArgumentParser
import numpy as np
import math
import pytest
from datetime import timedelta as delta


method = {'RK4': AdvectionRK4, 'EE': AdvectionEE, 'RK45': AdvectionRK45}


def ground_truth(lon, lat):
    day = 11.6
    r = 1 / (day * 86400)
    beta = 2e-11
    a = 2000000
    e_s = r / (beta * a)
    psi = (1 - np.exp(-lon * math.pi / 180 / e_s) - lon *
           math.pi / 180) * math.pi * np.sin(math.pi ** 2 * lat / 180)
    return psi


def stommel_grid(xdim=200, ydim=200):
    """Simulate a periodic current along a western boundary, with significantly
    larger velocities along the western edge than the rest of the region

    The original test description can be found in: N. Fabbroni, 2009,
    Numerical Simulation of Passive tracers dispersion in the sea,
    Ph.D. dissertation, University of Bologna
    http://amsdottorato.unibo.it/1733/1/Fabbroni_Nicoletta_Tesi.pdf
    """
    # Set NEMO grid variables
    depth = np.zeros(1, dtype=np.float32)
    time = np.linspace(0., 100000. * 86400., 2, dtype=np.float64)

    # Coordinates of the test grid (on A-grid in deg)
    lon = np.linspace(0, 60, xdim, dtype=np.float32)
    lat = np.linspace(0, 60, ydim, dtype=np.float32)

    # Define arrays U (zonal), V (meridional), W (vertical) and P (sea
    # surface height) all on A-grid
    U = np.zeros((lon.size, lat.size, time.size), dtype=np.float32)
    V = np.zeros((lon.size, lat.size, time.size), dtype=np.float32)

    # Some constants
    day = 11.6
    r = 1 / (day * 86400)
    beta = 2e-11
    a = 2000000
    e_s = r / (beta * a)

    [x, y] = np.mgrid[:lon.size, :lat.size]
    for t in range(time.size):
        for i in range(lon.size):
            for j in range(lat.size):
                U[i, j, t] = -(1 - math.exp(-lon[i] * math.pi / 180 / e_s) -
                               lon[i] * math.pi / 180) * math.pi ** 2 *\
                    math.cos(math.pi ** 2 * lat[j] / 180)
                V[i, j, t] = (math.exp(-lon[i] * math.pi / 180 / e_s) / e_s -
                              1) * math.pi * math.sin(math.pi ** 2 * lat[j] / 180)

    return Grid.from_data(U, lon, lat, V, lon, lat, depth, time)


def stommel_example(grid, npart=1, mode='jit', verbose=False,
                    method=AdvectionRK4):
    """Configuration of a particle set that follows two moving eddies

    :arg grid: :class NEMOGrid: that defines the flow field
    :arg npart: Number of particles to intialise"""

    # Determine particle class according to mode
    ParticleClass = JITParticle if mode == 'jit' else Particle
    pset = grid.ParticleSet(size=npart, pclass=ParticleClass,
                            start=(10., 50.), finish=(7., 30.))

    if verbose:
        print("Initial particle positions:\n%s" % pset)

    # Execute for 25 days, with 5min timesteps and hourly output
    endtime = delta(days=25)
    dt = delta(minutes=5)
    interval = delta(hours=12)
    print("Stommel: Advecting %d particles for %s" % (npart, endtime))
    pset.execute(method, endtime=endtime, dt=dt, interval=interval,
                 output_file=pset.ParticleFile(name="StommelParticle"))

    if verbose:
        print("Final particle positions:\n%s" % pset)

    return pset


@pytest.mark.xfail(reason="Stommel test criteria not yet adjusted")
@pytest.mark.parametrize('mode', ['scipy', 'jit'])
def test_stommel_grid(mode):
    grid = stommel_grid()
    pset = stommel_example(grid, 3, mode=mode)
    assert(3. < pset[0].lon < 3.5 and 4.75 < pset[0].lat < 5.25)
    assert(7.4 < pset[1].lon < 8. and 40. < pset[1].lat < 40.6)
    assert(4. < pset[2].lon < 4.3 and 26.7 < pset[2].lat < 27.)


if __name__ == "__main__":
    p = ArgumentParser(description="""
Example of particle advection in the steady-state solution of the Stommel equation""")
    p.add_argument('mode', choices=('scipy', 'jit'), nargs='?', default='jit',
                   help='Execution mode for performing computation')
    p.add_argument('-p', '--particles', type=int, default=1,
                   help='Number of particles to advect')
    p.add_argument('-v', '--verbose', action='store_true', default=False,
                   help='Print particle information before and after execution')
    p.add_argument('--profiling', action='store_true', default=False,
                   help='Print profiling information after run')
    p.add_argument('-g', '--grid', type=int, nargs=2, default=None,
                   help='Generate grid file with given dimensions')
    p.add_argument('-m', '--method', choices=('RK4', 'EE', 'RK45'), default='RK4',
                   help='Numerical method used for advection')
    args = p.parse_args()
    filename = 'stommel'

    # Generate grid files according to given dimensions
    if args.grid is not None:
        grid = stommel_grid(args.grid[0], args.grid[1])
        grid.write(filename)

    # Open grid files
    grid = Grid.from_nemo(filename)

    if args.profiling:
        from cProfile import runctx
        from pstats import Stats
        runctx("stommel_example(grid, args.particles, mode=args.mode, \
                              verbose=args.verbose)",
               globals(), locals(), "Profile.prof")
        Stats("Profile.prof").strip_dirs().sort_stats("time").print_stats(10)
    else:
        stommel_example(grid, args.particles, mode=args.mode,
                        verbose=args.verbose, method=method[args.method])
