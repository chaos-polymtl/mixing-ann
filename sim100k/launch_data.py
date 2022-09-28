import sys
import os
sys.path.insert(1, os.getcwd())
import MixerSim as MS

MS.get_torque_and_write_data(first_mixer=0, last_mixer=99999)
