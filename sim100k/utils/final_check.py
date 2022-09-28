import os
import numpy as np
import glob

# First and last mixer
print('First mixer to relaunch job :')
first_mixer = int(input())
print('Last mixer to relaunch job :')
last_mixer = int(input())

this_path = os.getcwd() + '/..'
for mixer in np.linspace(first_mixer, last_mixer, (last_mixer-first_mixer)+1, dtype=int):
    geo_path = this_path + '/mixer_' + str(mixer)
    os.chdir(geo_path)
    
    files_out = glob.glob('mixer_' + str(mixer) + '-*.out')
    id_files_out = [int(file.split('-')[1].split('.')[0]) for file in files_out]
    id_files_out.sort()
    last_file_out = id_files_out[-1]
    
    with open('mixer_' + str(mixer) + '-' + str(last_file_out) + '.out') as f:
        output = f.readlines()
        
    i = -1
    is_finished = False
    while i > -10:
        if output[i].rstrip('\n') == '+---------------------------------+-----------+------------+------------+':
            is_finished = True
            break
        else:
            i -= 1
    
    if os.path.isfile('torque.00.dat') and not is_finished:
        print(mixer)
        os.system('cp ../utils/relaunch_lethe.sh .')
        os.system('cp ../utils/relaunch_lethe.py .')
        os.system('sbatch -J ' + 'mixer_' + str(mixer) + ' relaunch_lethe.sh')

os.chdir('../utils')
