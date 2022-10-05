# mixing-ann

This repository includes all the code programs, scripts and files that were used for a project about the development of an Artificial Neural Network trained with data coming from Lethe simulations of pitched blade turbines (PBT) mixers.

It is divided into two folders. The folder _sim100k_ contains the files that served to generate the 100k CFD simulations of mixing systems. The second folder, called _ai_, contains the files that served to pre-process the data and to train the Artificial Neural Network.

## CFD simulations (in folder _sim100k_)

### Setting the Python methods

In this the _MixerSim.py_ file, we define two important methods. The first one is used to create the 100k samples while the second is used to gather the torque and to calcule the power number $N_p$.

#### _generate_data_folders_

This method uses the Latin Hypercube sampling (LHS) method to generate 100k samples of mixing systems. It takes in arguments the range of the features of the mixing systems (the dimensionless geometrical features and the Reynolds number $Re$). The LHS method comes from the [library pyDOE](https://pythonhosted.org/pyDOE/randomized.html). The method creates 100k different folders in which every mixer will be simulated seperately.

Using the [library Jinja2](https://jinja.palletsprojects.com/en/3.1.x/), the _mixer.geo_ template is copied in the folder and the arguments that allows to generate the mesh are replaced by the right geometrical ratios. The same principle is applied to the _mixer.prm_ template. The kinematic viscosity parameter is replaced by the right value in order to respect the Reynolds number.

#### _launch_gmsh_

#### _get_torque_and_write_data_

When all the Lethe simulations are done, this method allows to gather all the torque resulting from the simulations and then to calculate the power number $N_p$ of every 100k mixers. A file of type _.txt_ is generated at the end of the method and will serve as database fed to the ANN.

### Launch simulations on the cluster

In the _sim100k_ folder, some files are used to launch the methods decribed above and the software Lethe strictly on the Digital Alliance of Canada clusters. Every step of the methodology includes two files: one _.sh_ files and one _.py_ file. The _.sh_ file will serve as 

#### _launch_folders.sh_ & _launch_folders.sh_

#### _launch_lethe.sh_ & _launch_lethe.sh_

#### _launch_data.sh_ & _launch_data.sh_

## ANN (in folder _ai_)