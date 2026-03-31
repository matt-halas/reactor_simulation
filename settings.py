# Number of cells in the reactor
N_X = 10
N_Y = 10
# Size of cells (in m)
CELL_SIZE = 0.001
# GUI scale
GUI_SCALE = 30000
# Increase cross section (probability of collision) to speed up simulation
CROSS_SECTION_AMP = 1

# Cross section data taken from https://wwwndc.jaea.go.jp/j5fig/findex.html
# Moderator macroscopic cross section in cm^-1
CROSS_SECTION = CROSS_SECTION_AMP * 0.1

# Energy of new neutrons created by the source
NEUTRON_SOURCE_ENERGY = 10

# Average number of neutrons released per fission (assume constant) "Table 3.4 pg. 82"
NEUTRONS_PER_FISSION = 2.418

# Fuel microscopic cross section in cm^2 at 0.0253eV
U235_MIC_ABS_CS = CROSS_SECTION_AMP * 684e-24
U238_MIC_ABS_CS = CROSS_SECTION_AMP * 2.7e-24
# Fission to absorption ratio for U235
U235_ALPHA = 0.8556
# Density of UO2 fuel is 10.97 g/cm^3, molar mass of 270.03 g/mol
# 6.022e23 atoms per mol, 2.446e22 atoms/cm^3
N_FUEL = 2.446e22
FUEL_ENRICHMENT = 0.0072  # Natural uranium
U235_MAC_ABS_CS = U235_MIC_ABS_CS * N_FUEL * FUEL_ENRICHMENT
U238_MAC_ABS_CS = U238_MIC_ABS_CS * N_FUEL * (1 - FUEL_ENRICHMENT)
FUEL_MAC_ABS_CS = U235_MAC_ABS_CS + U238_MAC_ABS_CS

# Fission to absorption ratio for natural uranium
FUEL_ALPHA = (U235_ALPHA * U235_MAC_ABS_CS) / (U235_MAC_ABS_CS + U238_MAC_ABS_CS)


# Mass of moderator atoms
M_MOD = 1
# Time step length
TIME_STEP = 1e-7
