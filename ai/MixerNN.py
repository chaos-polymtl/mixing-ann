# ============================================================================
# Neural Network functions using TensorFlow
# Goal : Predict the number of power of the impeller of a mixer.
# Author : Valérie Bibeau, Polytechnique Montréal, 2020
# ============================================================================

# ----------------------------------------------------------------------------
# Arrays for data
import numpy as np
# To normalize data
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
# NN
import numpy as np
np.random.seed(1)               # for reproducibility
import tensorflow
tensorflow.random.set_seed(2)   # for reproducibility
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# ----------------------------------------------------------------------------
def read_mixerdata(file_name, col):
    """Read the data of the mixers

    Args:
        file_name (string): Name of the file that contains the data

    Returns:
        data (array): Mixers' dataset
    """
    dataset = open(file_name,'r')
    mixer = dataset.readlines()
    for m in np.arange(0, len(mixer), dtype=int):
        x = np.array([])
        features = mixer[m].split('\t')
        if features[-1] != '!SIMULATION FAILED!\n':
            for f in np.arange(2,col,2):
                x = np.insert(x, len(x), float(features[f]))
            if m == 0:
                data = x
            else:
                data = np.vstack((data, x))
    return data

def initial_setup(data, test_size, target_index, output_index, random_state):
    """Set up the training and testing set

    Args:
        data (array): Mixers' dataset
        test_size (float): Fraction of the training set that will be tested
        target_index (array): Index of the features that will be preserved
        output_index (int): Index of the output
        random_state (int): Random number to split the training and testing set

    Returns:
        X and y: Features and target values of the training and testing set
    """
    # Separate features from target values
    X = data[:,target_index]
    y = data[:,output_index]
    y = np.reshape(y, (-1, 1))
    # Normalizing features
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    scaler_X.fit(X)
    scaler_y.fit(y)
    Xscale = scaler_X.transform(X)
    yscale = scaler_y.transform(y)
    # Split the data into training and testing
    X_train, X_test, y_train, y_test = train_test_split(Xscale, yscale, 
                                                        test_size=test_size,
                                                        random_state=random_state)
    return X_train, X_test, y_train, y_test, scaler_X, scaler_y

def fit_model(X_train, y_train, no_features, batch_size, l2, epochs, val_frac, architecture, units, layers, activation, verbose):
    """Neural Network architecture/model to train the mixers

    Args:
        X_train and y_train: Features and target values of the training set
        no_features (int): Number of features
        batch_size (float): Number of inputs that is being used for training and updating the weights
        l2 (float): Regularization constant
        epochs (int): Number of iterations
        val_frac (float): Fraction of the training that will serve the validation of the model
        architecture (string): Type of the architecture
        units (int): Number of units of the first hidden layer
        layers (int): Number of layers in the NN
        verbose (int)

    Returns:
        history: History of the algorithme
    """
    keras.backend.clear_session()
    # Optimizer
    opt = keras.optimizers.Adamax()
    # Initializer
    ini = keras.initializers.GlorotUniform()
    # Regularizer
    reg = keras.regularizers.l2(l2)
    # Architecture of the Neural Network
    if architecture == 'deep':
        model = Sequential()
        model.add(Dense(units, input_dim=no_features, kernel_initializer=ini, kernel_regularizer=reg, activation=activation))
        l = 1
        while l < layers:
            model.add(Dense(units, kernel_initializer=ini, kernel_regularizer=reg, activation=activation))
            l = l + 1
        model.add(Dense(1, kernel_initializer=ini, kernel_regularizer=reg, activation='linear'))
    elif architecture == 'cascade':
        model = Sequential()
        model.add(Dense(units, input_dim=no_features, kernel_initializer=ini, kernel_regularizer=reg, activation=activation))
        l = 1
        while l < layers and units >= 2:
            units = units/2
            model.add(Dense(units, kernel_initializer=ini, kernel_regularizer=reg, activation=activation))
            l = l + 1
        model.add(Dense(1, kernel_initializer=ini, kernel_regularizer=reg, activation='linear'))        
    # Compile
    model.compile(loss='mse', optimizer=opt, metrics=['mse','mae','mape'])
    model.summary()
    # TensorBoard
    #early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=100)
    # Fit
    history = model.fit(X_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=val_frac, verbose=verbose)
    return history, model, model.count_params()

def mean_absolute_percentage_error(y_true, y_pred):
    """Mean Absolute Percentage Error

    Args:
        y_true (array): True values
        y_pred (array): Predicted values

    Returns:
        mape
    """
    diff = np.abs((y_true - y_pred) / y_true)
    mape = np.mean(diff) * 100
    return mape