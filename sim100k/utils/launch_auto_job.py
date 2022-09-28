import os
import numpy as np

# Get number of running and pending jobs
cmd = "squeue -u bibeauv -h -t pending,running -r | wc -l"
running_jobs = int(os.popen(cmd).read())

# Get last mixer being launched
with open('last_mixer.txt', 'r') as f:
    last_job = f.readlines()

# Mixers to launch
max_jobs = 1000
first_mixer = int(last_job[0])+1
last_mixer = (max_jobs - running_jobs) + first_mixer-1

this_path = os.getcwd() + '/..'
for mixer in np.linspace(first_mixer, last_mixer, (last_mixer-first_mixer)+1, dtype=int):
    geo_path = this_path + '/mixer_' + str(mixer)
    os.chdir(geo_path)

    os.system('cp ../launch_lethe.py .')
    os.system('cp ../launch_lethe.sh .')
    os.system('sbatch -J ' + 'mixer_' + str(mixer) + ' launch_lethe.sh')

os.chdir('../utils')

# Change first and last mixer being launched
with open('last_mixer.txt', 'w') as f:
    f.write(str(last_mixer))

with open('first_mixer.txt', 'w') as f:
    f.write(str(first_mixer))
