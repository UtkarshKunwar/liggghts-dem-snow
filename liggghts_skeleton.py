script_part_1 = '''# Initialisation
atom_style   sphere
atom_modify  map array
boundary     f f f
newton       off
communicate   single vel yes
units        si

# Domain region
'''

# Domain to be defined here
script_part_2 = '''region       reg block {} {} {} {} {} {} units box
'''
#script_part_2 = '''region       reg block {:.4f} {:.4f} {:.4f} {:.4f} {:.4f} {:.4f} units box
#'''


script_part_3 = '''create_box   1 reg
neighbor     0.002 bin
neigh_modify delay 0

#Material properties required for pair style
fix          m1 all property/global youngsModulus peratomtype 5.0e6
fix          m2 all property/global poissonsRatio peratomtype 0.325
fix          m3 all property/global coefficientRestitution peratomtypepair 1 0.89
fix          m4 all property/global coefficientFriction peratomtypepair 1 0.1
pair_style   gran model hertz tangential history
pair_coeff    * *

# Timestep
timestep     0.00001

# Gravity
fix          gravi all gravity 9.81 vector 0.0 0.0 -1.0

# Walls/Boundaries
'''

# Boundaries to be inserted here
script_part_4 = '''fix          xwalls1 all wall/gran model hertz tangential history primitive type 1 xplane {}
fix          xwalls2 all wall/gran model hertz tangential history primitive type 1 xplane {}
fix          ywalls1 all wall/gran model hertz tangential history primitive type 1 yplane {}
fix          ywalls2 all wall/gran model hertz tangential history primitive type 1 yplane {}
fix          zwalls1 all wall/gran model hertz tangential history primitive type 1 zplane {}
fix          zwalls2 all wall/gran model hertz tangential history primitive type 1 zplane {}
'''

# Region of insertion to be inserted here
script_part_5 = '''region       bc block {} {} {} {} {} {} units box
'''

script_part_6 = '''# Particle distributions
fix          pts1 all particletemplate/sphere 12345787 atom_type 1 density constant 500 radius constant 0.005
fix          pdd1 all particledistribution/discrete 17903  1 pts1 1.0
fix          ins all insert/pack seed 123457 distributiontemplate pdd1 vel constant 0. 0. -0.5 &
             insert_every once overlapcheck yes all_in yes particles_in_region 20000 region bc
'''

# STL mesh file to be inserted here
script_part_7 = '''fix          cad all mesh/surface file {} heal auto_remove_duplicates type 1 scale 0.001
'''

script_part_8 = '''fix          granwalls all wall/gran model hertz tangential history mesh n_meshes 1 meshes cad
#apply nve integration to all particles
fix          integr all nve/sphere
#output settings, include total thermal energy
compute         rke all erotate/sphere
thermo_style    custom step atoms ke vol time cpu
thermo          1000
thermo_modify   lost ignore norm no
compute_modify  thermo_temp dynamic yes
'''

# Files to be dumped here
script_part_9 = '''dump            dumpstl all stl 100000 {}/dumpstl*.stl
dump            dmp all custom 1000 {}/dump*.atom id type x y z vx vy vz fx fy fz omegax omegay omegaz
'''
script_part_10 = '''# Insert particles and run
run             150000
'''

