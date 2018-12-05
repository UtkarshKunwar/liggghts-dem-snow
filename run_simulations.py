import os, sys, subprocess
import numpy as np
import math
import glob

from liggghts_skeleton import *

# Prints usage of the script
def print_usage():
    print("Usage:\n\tpython3 run_simulations.py <Length of slope (mm)> <Width of slope (mm)> <Start Angle> <End Angle> <Steps>")
    sys.exit(1)

if len(sys.argv) < 6:
    print_usage()

# Converting to SI
slope_length = float(sys.argv[1]) / 1000.0
slope_width = float(sys.argv[2]) / 1000.0
start_angle = float(sys.argv[3])
end_angle = float(sys.argv[4])
angle_steps = float(sys.argv[5])

# Constants for the script
PREFIX = '/home/utkarsh/wd/'
POST_DIR = PREFIX + 'post/slope/'
SCRIPT_DIR = PREFIX + 'scripts/slope/'
NUMBER_OF_PROCESSES = 20

# Array of angles for which the simulations are to be run.
angles = np.linspace(start_angle, end_angle, int(((end_angle - start_angle) / angle_steps) + 1))

# Defining the domain of the system.
region_bounds = [
    0.0, 2 * slope_length,
    0.0, slope_width,
    0.0, 2.5 * slope_length
]

# Calculating the minimum insertion height of the pack of particles.
min_insertion_z = region_bounds[5] - (slope_length * math.tan(math.radians(end_angle)))

# Writes the LIGGGHTS script to file.
def write_script_to_file(script_path, angle):
    script_file_path = script_path + '/in.slope'
    with open(script_file_path, 'w') as script_file:
        script_file.write(script_part_1)

        # Creating Domain
        script_file.write(
            script_part_2.format(
                region_bounds[0], region_bounds[1],
                region_bounds[2], region_bounds[3],
                region_bounds[4], region_bounds[5],
            )
        )

        script_file.write(script_part_3)

        # Creating fixed boundaries of the domain
        script_file.write(
            script_part_4.format(
                region_bounds[0], region_bounds[1],
                region_bounds[2], region_bounds[3],
                region_bounds[4], region_bounds[5],
            )
        )

        # Creating insertion region for the particles
        initial_insertion_z = slope_length * math.tan(math.radians(angle))
        insertion_x = slope_length / 2.0
        insertion_y = slope_width
        final_insertion_z = initial_insertion_z + min_insertion_z
        insertion_bounds = [
            region_bounds[0], slope_length / 2.0,
            region_bounds[2], slope_width,
            initial_insertion_z, final_insertion_z
        ]
        script_file.write(
            script_part_5.format(
                insertion_bounds[0], insertion_bounds[1],
                insertion_bounds[2], insertion_bounds[3],
                insertion_bounds[4], insertion_bounds[5],
            )
        )

        script_file.write(script_part_6)

        # Adding STL mesh file path
        stl_file_path = script_path + '/slope.stl'
        script_file.write(script_part_7.format(stl_file_path))
        script_file.write(script_part_8)
        script_file.write(script_part_9.format(post_path, post_path))
        script_file.write(script_part_10)

# Generates SCAD file using SolidPython which is converted to STL by OpenSCAD
def write_mesh_file(script_path):
    scad_file_path = script_path + '/slope.scad'
    stl_file_path = script_path + '/slope.stl'

    # Creates SCAD file for OpenSCAD
    with open(scad_file_path, 'w') as scad_file:
        subprocess.call(['python3', '/home/utkarsh/wd/utils/make_slope.py', str(slope_length * 1000), str(slope_width * 1000), str(angle)], stdout=scad_file)

    # OpenSCAD converts SCAD file to STL
    subprocess.call(['wine64', '/home/utkarsh/openscad/openscad.exe', scad_file_path, '-o', stl_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Runs LIGGGHTS for the specified conditions
def run_liggghts(script_path):
    os.chdir(script_path)
    script_file = script_path + '/in.slope'
    subprocess.call(['mpirun', '-np', str(NUMBER_OF_PROCESSES), 'lmp_auto', '-i', script_file])

# Post processes the .atom files to .vtk format for visualising in ParaView
def post_process(post_path):
    os.chdir(post_path)
    subprocess.call(['lpp'] + glob.glob('*.atom'))

# Executes the simulations one by one.
for angle in angles:
    print('''================================
    Running for angle = {}
================================'''.format(angle))
    dir_name = 'L' + str(slope_length * 1000) + '_W' + str(slope_width * 1000) + '_A' + str(angle)
    script_path = SCRIPT_DIR + dir_name
    post_path = POST_DIR + dir_name
    if not os.path.exists(script_path):
        os.makedirs(script_path)
    if not os.path.exists(post_path):
        os.makedirs(post_path)

    # Writing LIGGGHTS script file
    write_script_to_file(script_path, angle)

    # Generate STL mesh file
    write_mesh_file(script_path)

    # Run the simulation using OpenMPI
    run_liggghts(script_path)

    # Post processing to create VTK format for visualising in ParaView
    post_process(post_path)

print("All simulations completed.")
