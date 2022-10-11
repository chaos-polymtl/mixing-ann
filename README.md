# mixing-ann

This repository includes all the code programs, scripts and files that were used for a project about the development of an Artificial Neural Network trained with data coming from Lethe simulations of mixers.

It is divided into two folders. The folder `sim100k` contains the files that served to generate the 100k CFD simulations of mixing systems. The second folder, called `ai`, contains the files that served to pre-process the data and to train the Artificial Neural Network.

## 💻 CFD simulations (in folder `sim100k`)

### Setting the Python methods

In the `MixerSim.py` file, we define three important methods. The first one is used to create the 100k samples, the second to generate the mesh and the third to gather the torque and to calculate the power number $N_p$.

1. `generate_data_folders`

This method uses the Latin Hypercube sampling (LHS) method to generate 100k samples of mixing systems. It takes in arguments the range of the features of the mixing systems (the dimensionless geometrical features and the Reynolds number $Re$). The LHS method comes from the library [pyDOE](https://pythonhosted.org/pyDOE/randomized.html). The method creates 100k different folders in which every mixers will be simulated seperately.

Using the library [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/), we copy the `mixer.geo` template in the folder and we replace the arguments that generates the mesh by the right geometrical ratios. We apply the same principle to the `mixer.prm` template. We replace the kinematic viscosity parameter by the right value in order to respect the Reynolds number.

2. `launch_gmsh`

With the same library Jinja2, this methods specifies the minimum and maximum characteristic length of the tetrahedral element of the mesh. It then launches the software [Gmsh](https://gmsh.info/) to generate the mesh of the mixing vessel. This method is usefull to perform a mesh sensitivity analysis.

3. `get_torque_and_write_data`

When all the Lethe simulations are done, this method gathers all the torque resulting from the simulations and then calculates the power number $N_p$ of every 100k mixers. At the end of its execution, the method generates a file of type `.txt` that will serve as the database fed to the ANN.

### Launch simulations on the cluster

In the `sim100k` folder, some files are used to launch the methods decribed above and the software Lethe strictly on the Digital Alliance of Canada clusters. Every step of the methodology includes two files: one `.sh` file and one `.py` file. The `.sh` file will serve as the `sbatch` script to queue a job on the cluster and the `.py` file will serve as a script that execute the different methods.

1. Launching the folders

The `launch_folders.sh` is the `sbatch` command that submits the `launch_folders.py` script as a job. It executes the `generate_data_folders` method to create the 100k folders containing 100k different mixing configurations.

2. Launching Lethe

The `launch_lethe.sh` is the `sbatch` command that submits the `launch_lethe.py` script as a job. It executes the `launch_gmsh` method to generate the mesh of the mixer using Gmsh. Then, it runs the Lethe executable `gls_navier_stokes_3d` build on the cluster.

3. Launching the gathering of the data

The `launch_data.sh` is the `sbatch` command that submits the `launch_data.py` as a job. It executes the `get_torque_and_write_data` to gather the features, the torque and ultimately the power number of every simulations in the final database.

## 🌐 ANN (in folder `ai`)

### Setting the Python methods

In the `MixerNN.py` file, three important methods are implemented. The first one reads the database, the second normalizes the data and the third trains the ANN.

- `read_mixerdata`

This method reads the `mixer_database_0-99999.txt` file that contains the features (inputs) and the power number (output) of the 100k mixers simulations and stores them into variables.

- `initial_setup`

This method creates a tensor $X$ of dimension $n \times d$ where $n$ is the number of mixing samples and $d$ is the number of features, which is seven (six geometrical ratios and one Reynolds number). It also creates a second tensor $y$ of dimension $n \times 1$ containing the outputs $N_p$ of every mixing samples.

Then, we use the [MinMax](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html) method from sklearn to scale the features and the outputs in the interval of 0 to 1 to avoid any bias during the training.

Finaly, we seperate the samples into two sets: training and testing. We use the [`train_test_split`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html) function from sklearn to perform the split.

- `fit_model`

Firstly, the method creates the architecture of the ANN using the [Tensorflow](https://www.tensorflow.org/?gclid=Cj0KCQjw-fmZBhDtARIsAH6H8qikMT8INmX_rvf5a83jC6K4WxbQN0EwutTxOsleIzC-3XyXXSMzGlYaAiK9EALw_wcB) and [Keras](https://keras.io/) libraries. It builds a deep network according to the arguments of the method that specifies its hyperparameters, such as the number of layers, the number of neurons, the batch size, the number of epochs and the activation function.

Secondly, the method compiles the ANN using the training set. In the method, we return the model and also the history of the ANN. This allows to catch the evolution of the loss function.

### Grid search

The `grid_search.py` script performs a grid search with cross validation ([GridSeachCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html) from sklearn) to find the best hyperparameters of the ANN.

### Optimum training

 We train the ANN with all the training set using the `optimum.py` script. It does the training using the hyperparameters determined by the grid search and returns the mean squared error (MSE), the mean absolute error (MAE) and the mean absolute percentage error (MAPE) of the ANN. Also, the final model is saved in the `optimum_mixer_model` folder.

### Comparison

The first script (`compare.py`) generates power curves of $N_p$ versus $Re$ for a given geometry with different models. It compares the predictions of $N_p$ made by the ANN, the correlation of [Hiraoka et al.](https://downloads.hindawi.com/journals/ijce/2012/106496.pdf) and Lethe simulations. The data of the simulations are stored in `Np-Re1_0-20.txt` and `Np-Re2_0-20.txt`. The first set of simulations used a coarser mesh while the second used a finer mesh.

The second script (`plot_data.py`) predicts $N_p$ with the ANN and the correlation for multiple different geometrical configurations of the testing set. It utimately plots the comparison between the $N_p$ predictions and the real values coming from the database.