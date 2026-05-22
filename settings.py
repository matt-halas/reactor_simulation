# Number of cells in the reactor
N_X = 10
N_Y = 10
# Size of cells (in m)
CELL_SIZE = 0.001
# GUI scale
GUI_SCALE = 4000
# Increase cross section (probability of collision) to speed up simulation
CROSS_SECTION_AMP = 1

# Cross section data taken from https://wwwndc.jaea.go.jp/j5fig/findex.html

### Moderator constants ###
# Moderator macroscopic cross section in cm^-1
CROSS_SECTION = CROSS_SECTION_AMP * 0.1
MOD_MAC_SCT_CS = 3.443
MOD_MAC_ABS_CS = 0.0222

# RMS speed of hydrogen atoms in water. Will transfer some energy to neutrons.
MODERATOR_RMS = 2000

# Energy of new neutrons created by the source
NEUTRON_SOURCE_ENERGY = 10

# Average number of neutrons released per fission (assume constant) "Table 3.4 pg. 82"
NEUTRONS_PER_FISSION = 2.418

# Density of UO2 fuel is 10.97 g/cm^3, molar mass of 270.03 g/mol
# 6.022e23 atoms per mol, 2.446e22 atoms/cm^3
N_FUEL = 2.446e22
DEFAULT_FUEL_ENRICHMENT = 0.72  # Natural uranium (%)

# Mass of moderator atoms
M_MOD = 1
# Time step length
TIME_STEP = 1e-7
