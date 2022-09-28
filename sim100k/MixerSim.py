from jinja2 import Template
from pyDOE import *
import os
import numpy as np
np.random.seed(0)
import sys
import math
from subprocess import Popen, PIPE
import warnings
warnings.filterwarnings("error")
warnings.filterwarnings('ignore', category=PendingDeprecationWarning)

# ----------------------------------------------------------------------------
# Fonctions python permettant le lancement des simulations des mélangeurs
# - generate_data_folders
# - launch_gmsh
# - launch_job
# - launch_local
# - get_torque_and_write_data
# ______________
# Valérie Bibeau, Polytechnique Montréal, 2020

def generate_data_folders(TD, HT, TC, DW, WHub, E, theta, Re, initial_Re, ne):
    """
    Generate the folders of the geometries

    Args:
        TD (list): min, max (geometric ratio)
        HT (list): min, max (geometric ratio)
        TC (list): min, max (geometric ratio)
        DW (list): min, max (geometric ratio)
        WHub (list): min, max (pourcentage of W for the Hub)
        E (list): min, max (pourcentage of W for the thickness of the blades)
        theta (list): min, max (angle of the blades)
        Re (list): min, max
        initial_Re (int): For initial condition in Lethe
    """
    # Create LHS
    k = lhs(8, samples=ne, criterion='center')

    # Get current path
    path = os.getcwd()

    progress = 1
    no_folders = ne

    for j in np.arange(ne):
        rTD = k[j][0]*(TD[1] - TD[0]) + TD[0]
        rHT = k[j][1]*(HT[1] - HT[0]) + HT[0]
        rTC = k[j][2]*(TC[1] - TC[0]) + TC[0]
        rDW = k[j][3]*(DW[1] - DW[0]) + DW[0]
        rWHub = k[j][4]*(WHub[1] - WHub[0]) + WHub[0]
        rE = k[j][5]*(E[1] - E[0]) + E[0]
        rtheta = k[j][6]*(theta[1] - theta[0]) + theta[0]
        rRe = k[j][7]*(Re[1] - Re[0]) + Re[0]

        # Open the geometry file
        fic_geo = open("mixer.geo","r")
        cte_geo = fic_geo.read()
        # Insert the geometry
        template = Template(cte_geo)
        geometries = template.render(ratioTD = rTD,
                                     ratioHT = rHT,
                                     ratioTC = rTC,
                                     ratioDW = rDW,
                                     ratioDW_Hub = rWHub*rDW,
                                     p_thick = rE,
                                     theta = rtheta,
                                     min_mesh_length = "{{min_mesh_length}}",
                                     max_mesh_length = "{{max_mesh_length}}")
        fic_geo.close()

        # Open the parameter file
        fic_prm = open("mixer.prm","r")
        cte_prm = fic_prm.read()
        # Insert the parameters
        template_prm = Template(cte_prm)
        if rRe > initial_Re:
            parameters = template_prm.render(viscosity = (1/rTD)**2/rRe,
                                             initial_viscosity = (1/rTD)**2/initial_Re)
        else:
            parameters = template_prm.render(viscosity = (1/rTD)**2/rRe,
                                             initial_viscosity = (1/rTD)**2/rRe)
        fic_prm.close()

        # Create the folder of the geometry
        newPath = path + '/mixer_' + str(int(j))
        os.mkdir(newPath)

        # Copy the prm and geo file
        os.system('cp mixer.prm ' + newPath)
        os.system('cp mixer.geo ' + newPath)

        # Go into the folder
        os.chdir(newPath)

        # Write the prm and geo file
        wr_geo = open("mixer.geo","w")
        wr_geo.write(geometries)
        wr_geo.close()
        # Write the prm file
        wr_prm = open("mixer.prm","w")
        wr_prm.write(parameters)
        wr_prm.close()

        # Write the tag file
        fic_tag = open("mixer.txt","w")
        fic_tag.write("T/D\t%f\t" % rTD)
        fic_tag.write("H/T\t%f\t" % rHT)
        fic_tag.write("T/C\t%f\t" % rTC)
        fic_tag.write("D/W\t%f\t" % rDW)
        fic_tag.write("D/W_Hub\t%f\t" % (rWHub*rDW))
        fic_tag.write("E/W\t%f\t" % rE)
        fic_tag.write("theta\t%f\t" % rtheta)
        fic_tag.write("Re\t%f\t" % rRe)
        fic_tag.close()

        os.chdir("../")

        pourcentage = progress/no_folders
        sys.stdout.write("\rProgress: " + "{:.2%}".format(pourcentage))
        sys.stdout.flush()
        progress += 1

    sys.stdout.write("\n")

def get_torque_and_write_data(first_mixer, last_mixer):
    """
    Get torque from simulation and write the data set

    Args:
        first_mixer (int): First mixer to simulate
        last_mixer (int): Last mixer to simulate
    """
    this_path = os.getcwd()
    
    database_name = 'mixer_database_' + str(int(first_mixer)) + '-' + str(int(last_mixer))

    progress = 1

    open(database_name + ".txt", "w").close()
    fic_data = open(database_name + ".txt", "a")
    for mixer in np.linspace(first_mixer, last_mixer, (last_mixer-first_mixer)+1, dtype=int):
        geo_path = this_path + '/mixer_' + str(mixer)
        os.chdir(geo_path)

        fic_data.write('mixer_' + str(mixer) + '\t')

        fic_tag = open("mixer.txt","r")
        geo_info = fic_tag.read()
        fic_data.write(geo_info)
        geo_info = geo_info.split("\t")
        D = geo_info[1] # Impeller diameter
        fic_tag.close()

        try:
            with open("torque.00.dat","r") as fic_torque:
                lines = fic_torque.readlines()
            fic_torque.close()
        
            get_torque = lines[-1]
            get_torque = get_torque.split(" ")
            torque = get_torque[3]

            # Calculate power number
            D = 1/float(D)
            torque = float(torque)
            Np = 2*math.pi*torque/D/D/D/D/D

            fic_data.write("Np\t%f\n" % Np)

        except:
            fic_data.write("!SIMULATION FAILED!\n")
        
        pourcentage = progress/((last_mixer-first_mixer)+1)
        sys.stdout.write("\rProgress: " + "{:.2%}".format(pourcentage))
        sys.stdout.flush()
        progress += 1

    os.chdir('../../')

    fic_data.close()
    sys.stdout.write("\n")
