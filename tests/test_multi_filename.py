from parcels import Grid
from argparse import ArgumentParser
import pytest
import numpy as np


def simple_grid(xdim=200, ydim=350, ndays=25, startday=0):
    """Generate a simple uniform grid where flow accellerates with time.
    Each file is one time slice
    """
    # Set NEMO grid variables
    depth = np.zeros(1, dtype=np.float32)
    time = np.arange(startday * 86400., (startday + ndays) * 86400., 86400., dtype=np.float64)

    # Coordinates of the test grid (on A-grid in deg)
    lon = np.linspace(0, 4, xdim, dtype=np.float32)
    lat = np.linspace(45, 52, ydim, dtype=np.float32)

    # Define arrays U (zonal), V (meridional), W (vertical) and P (sea
    # surface height) all on A-grid
    U = np.zeros((lon.size, lat.size, time.size), dtype=np.float32)
    V = np.zeros((lon.size, lat.size, time.size), dtype=np.float32)
    P = np.zeros((lon.size, lat.size, time.size), dtype=np.float32)

    for t in range(time.size):
        U[:, :, t] = time[t] / 86400.

    return Grid.from_data(U, lon, lat, V, lon, lat,
                          depth, time, field_data={'P': P})


@pytest.mark.parametrize('mode', ['scipy', 'jit'])
def multi_filename(mode):

    numfiles = 6
    for t in range(numfiles):
        filename = 'multi_filename'+str(t)
        grid = simple_grid(ndays=1, startday=t)
        grid.write(filename)

    filenames = {'U': "multi_filename*U.nc", 'V': "multi_filename*V.nc"}
    variables = {'U': 'vozocrtx', 'V': 'vomecrty'}
    dimensions = {'lat': 'y', 'lon': 'x',
                  'time': 'time_counter'}

    grid.from_netcdf(filenames, variables, dimensions)
    print('Grid.time as returned by .from_netcdf %s' % grid.time)
    print ''
    assert(grid.time.size == numfiles)


if __name__ == "__main__":
    p = ArgumentParser(description="""Example of bug in multi-filename parsing""")
    p.add_argument('mode', choices=('scipy', 'jit'), nargs='?', default='jit',
                   help='Execution mode for performing RK4 computation')
    args = p.parse_args()
    multi_filename(args.mode)
