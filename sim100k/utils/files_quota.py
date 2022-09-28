import os
import numpy as np

# First and last mixer
print('First mixer to clean quota :')
first_mixer = int(input())
print('Last mixer to clean quota :')
last_mixer = int(input())

this_path = os.getcwd() + '/..'
for mixer in np.linspace(first_mixer, last_mixer, (last_mixer-first_mixer)+1, dtype=int):
    geo_path = this_path + '/mixer_' + str(mixer)
    os.chdir(geo_path)

    try:
        os.system('rm launch_lethe.*')
    except:
        continue
    try:
        os.system('rm mixer.msh')
    except:
        continue
    try:
        os.system('rm relaunch_lethe.*')
    except:
        continue