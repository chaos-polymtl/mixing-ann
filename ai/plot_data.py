import MixerNN as MNN
import matplotlib.pyplot as plt
import numpy as np
from tensorflow import keras
import math

# ------------------------------------------------------------------------------------------
# http://downloads.hindawi.com/journals/ijce/2012/106496.pdf

# b: Height of impeller blade
# C: Clearance between bottom and impeller
# D: Vessel diameter
# d: Impeller diameter
# f: Friction factor
# H: Liquid depth
# hb: Baffle lenght
# NP: Power number
# NP0: Power number in unbaffled condition
# NPMax: Power number in fully baffed condition
# n: Impeller rotational speed
# nb: Number of baffle plates
# np: Number of blades
# Red: Reynolds number
# ReG: Modifed Reynolds number
# T: Shaft torque
# theta: Angle of impeller blade
# mu: Viscosity
# rho: Density

def correlation(b, d, H, Red, theta):
    # Constants
    D = 1
    n_blades = 4

    # Variables
    eta = 0.711*(0.157 + (n_blades*np.log(D/d))**0.611)/(n_blades**0.52*(1 - (d/D)**2))
    beta = 2*np.log(D/d)/((D/d) - (d/D))
    gamma = (eta*np.log(D/d)/((beta*D/d)**5))**(1/3)
    X = gamma*n_blades**0.7*b*(np.sin(theta)**1.6/H)

    Ct = ((1.96*X**1.19)**-7.8 + (0.25)**-7.8)**(-1/7.8)
    Ctr = 23.8*(d/D)**-3.24*(b*np.sin(theta)/D)**-1.18*X**-0.74
    Cl = 0.215*eta*n_blades*(d/H)*(1 - (d/D)**2) + 1.83*(b*np.sin(theta)/H)*(n_blades/2*np.sin(theta))**(1/3)
    m = ((0.71*X**0.373)**-7.8 + (0.333)**-7.8)**(-1/7.8)

    ff = 0.0151*(d/D)*Ct**0.308
    ReG = (math.pi*eta*np.log(D/d)/(4*d/beta*D))*Red

    f = Cl/ReG + Ct*(((Ctr/ReG) + ReG)**-1 + (ff/Ct)**(1/m))**m

    NP0 = ((1.2*math.pi**4*beta**2)/(8*d**3/(D**2*H)))*f

    return NP0
# ------------------------------------------------------------------------------------------

# Read the data
data = MNN.read_mixerdata('mixer_database_0-99999.txt',19)

# Set the features and the target values for the training and testing set
target_index = [0, 1, 2, 3, 5, 6, 7]
X_train, X_test, y_train, y_test, scaler_X, scaler_y = MNN.initial_setup(data, 0.001, target_index, 8, 42)

model = keras.models.load_model('optimum_mixer_model')

test_predictions = model.predict(X_test)

mape = MNN.mean_absolute_percentage_error(y_true=scaler_y.inverse_transform(y_test), 
                                          y_pred=scaler_y.inverse_transform(test_predictions))
print(mape)

a = plt.axes(aspect='equal')
plt.scatter(scaler_y.inverse_transform(y_test), scaler_y.inverse_transform(test_predictions),
            facecolors='none', edgecolors='b', label='ANN')
X_corr = scaler_X.inverse_transform(X_test)
d = X_corr[:,0]**-1
H = X_corr[:,1]**1
b = d / X_corr[:,3]
Red = X_corr[:,-1]
theta = X_corr[:,-2]
NP0 = correlation(b, d, H, Red, theta)
plt.scatter(scaler_y.inverse_transform(y_test), NP0,
            facecolors='none', edgecolors='r', label='Correlation')
lims = [0,60]
plt.plot(lims,lims,'-k')
plt.xlabel('True Values [Np]')
plt.ylabel('Predictions [Np]')
plt.legend()
plt.show()

error = scaler_y.inverse_transform(test_predictions) - scaler_y.inverse_transform(y_test)
plt.hist(error, bins=25)
plt.xlabel('Prediction Error [Np]')
plt.ylabel('Count')
plt.show()
