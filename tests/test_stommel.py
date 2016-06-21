from parcels import Grid, Particle, JITParticle
from parcels import AdvectionRK4, AdvectionEE, AdvectionRK45
from argparse import ArgumentParser
import numpy as np
import math
import pytest
from datetime import timedelta as delta


method = {'RK4': AdvectionRK4, 'EE': AdvectionEE, 'RK45': AdvectionRK45}


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

    # Some constants
    A = 100
    eps = 0.05
    a = 10000
    b = 10000

    # Coordinates of the test grid (on A-grid in deg)
    lon = np.linspace(0, a, xdim, dtype=np.float32)
    lat = np.linspace(0, b, ydim, dtype=np.float32)

    # Define arrays U (zonal), V (meridional), W (vertical) and P (sea
    # surface height) all on A-grid
    U = np.zeros((lon.size, lat.size, time.size), dtype=np.float32)
    V = np.zeros((lon.size, lat.size, time.size), dtype=np.float32)
    P = np.zeros((lon.size, lat.size, time.size), dtype=np.float32)

    [x, y] = np.mgrid[:lon.size, :lat.size]
    l1 = (-1 + math.sqrt(1 + 4 * math.pi**2 * eps**2)) / (2 * eps)
    l2 = (-1 - math.sqrt(1 + 4 * math.pi**2 * eps**2)) / (2 * eps)
    c1 = (1 - math.exp(l2)) / (math.exp(l2) - math.exp(l1))
    c2 = -(1 + c1)
    for t in range(time.size):
        for i in range(lon.size):
            for j in range(lat.size):
                xi = lon[i] / a
                yi = lat[j] / b
                P[i, j, t] = A * (c1*math.exp(l1*xi) + c2*math.exp(l2*xi) + 1) * math.sin(math.pi * yi)
        for i in range(lon.size-2):
            for j in range(lat.size):
                V[i+1, j, t] = (P[i+2, j, t] - P[i, j, t]) / (2 * a / xdim)
        for i in range(lon.size):
            for j in range(lat.size-2):
                U[i, j+1, t] = -(P[i, j+2, t] - P[i, j, t]) / (2 * b / ydim)

    return Grid.from_data(U, lon, lat, V, lon, lat, depth, time, field_data={'P': P}, mesh='flat')


def stommel_example(npart=1, mode='jit', verbose=False,
                    method=AdvectionRK4):
    """Configuration of a particle set that follows two moving eddies

    :arg npart: Number of particles to intialise"""

    grid = stommel_grid()
    filename = 'stommel'
    grid.write(filename)

    # Determine particle class according to mode
    ParticleClass = JITParticle if mode == 'jit' else Particle
    pset = grid.ParticleSet(size=npart, pclass=ParticleClass,
                            start=(100, 5000), finish=(100, 5000))

    if verbose:
        print("Initial particle positions:\n%s" % pset)

    # Execute for 30 days, with 5min timesteps and hourly output
    endtime = delta(days=50)
    dt = delta(minutes=5)
    interval = delta(hours=12)
    print("Stommel: Advecting %d particles for %s" % (npart, endtime))
    pset.execute(method, endtime=endtime, dt=dt, interval=interval,
                 output_file=pset.ParticleFile(name="StommelParticle"), show_movie=True)

    if verbose:
        print("Final particle positions:\n%s" % pset)

    return pset


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
    p.add_argument('-m', '--method', choices=('RK4', 'EE', 'RK45'), default='RK4',
                   help='Numerical method used for advection')
    args = p.parse_args()

    stommel_example(args.particles, mode=args.mode,
                    verbose=args.verbose, method=method[args.method])
