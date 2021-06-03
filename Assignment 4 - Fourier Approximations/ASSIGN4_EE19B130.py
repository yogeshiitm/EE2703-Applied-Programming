"""
    EE2703 Applied Programming Lab - 2021
    Assignment 4: Fourier Approximation
    Name - Yogesh Agarwala
    Roll - EE19B130
"""


import numpy as np
import math
from scipy.integrate import quad
import matplotlib.pyplot as plt
import timeit


############################################## Q1. Defining Functions ####################################################


#The functions e^x and cos(cos(x)) are defined as:
def exp(x):
    return np.exp(x)

def coscos(x):
    return np.cos(np.cos(x))


#Function Plots
# for e^x
x1 = np.linspace(-2*np.pi,4*np.pi,300)
x2 = np.linspace(0,2*np.pi,100)
tiled = np.tile(x2,3)
exp_x = exp(x1)
#Since exp(x) grows rapidly, we use semilogy for that plot.
plt.semilogy(x1,exp_x,'-r',label='True value')
plt.semilogy(x1,exp(tiled),'-b',label='Expected by fourier series')
plt.grid(True)
plt.ylabel(r'$e^{x}\rightarrow$',fontsize=15)
plt.xlabel(r'x$\rightarrow$',fontsize=15)
plt.title('Semilog plot of $e^{x}$',fontsize=15)
plt.legend(loc='upper right')
plt.show()

# for cos(cos(x))
x1 = np.linspace(-2*np.pi,4*np.pi,300)
coscos_x = coscos(x1)
plt.plot(x1,coscos_x,'r')
plt.grid(True)
plt.xlabel(r'x$\rightarrow$',fontsize=15)
plt.ylabel(r'$\cos(\cos(x))\rightarrow$',fontsize=15)
plt.title('Plot of $\cos(\cos(x))$',fontsize=15)
plt.show()


################### Q2. Finding the Fourier series coefficients: Integration approach #####################################3


# this function returns the first n fourier coefficients of the input function
func_dict = {'exp(x)':exp,'cos(cos(x))': coscos}
def find_coeff(n,label):
    coeff = np.zeros(n)
    func = func_dict[label]
    u = lambda x,k: func(x)*np.cos(k*x)
    v = lambda x,k: func(x)*np.sin(k*x)
    coeff[0]= quad(func,0,2*np.pi)[0]/(2*np.pi)
    for i in range(1,n,2):
        coeff[i] = quad(u,0,2*np.pi,args=((i+1)/2))[0]/np.pi
    for i in range(2,n,2):
        coeff[i] = quad(v,0,2*np.pi,args=(i/2))[0]/np.pi
    return coeff


#calculating first 51 fourier coefficients for the two functions
coeff_coscos = find_coeff(51,'cos(cos(x))')
coeff_exp = find_coeff(51,'exp(x)')


############################ Q3. Semilog and Loglog plot for both functions ###############################################


# (a) For e^x
# semilogy plot
plt.semilogy(range(51),np.abs(coeff_exp),'ro')
plt.grid(True)
plt.xlabel(r'n$\rightarrow$',fontsize=15)
plt.ylabel(r'Coefficient Magnitude$\rightarrow$',fontsize=15)
plt.title('Semilog Plot of coefficients for $e^{x}$',fontsize=15)
plt.show()
# loglog plot
plt.loglog(range(51),np.abs(coeff_exp),'ro')
plt.grid(True)
plt.xlabel(r'n$\rightarrow$',fontsize=15)
plt.ylabel(r'Coefficient Magnitude$\rightarrow$',fontsize=15)
plt.title('Loglog Plot of coefficients of $e^{x}$',fontsize=15)
plt.show()


# (b) For cos(cos(x))
# semilogy plot
plt.semilogy(range(51),abs(coeff_coscos),'ro')
plt.grid(True)
plt.xlabel(r'n$\rightarrow$',fontsize=15)
plt.ylabel(r'Coefficient Magnitude$\rightarrow$',fontsize=15)
plt.title('Semilog Plot of coefficients for $cos(cos(x))$',fontsize=15)
plt.show()
# loglog plot
plt.loglog(range(51),abs(coeff_coscos),'ro')
plt.grid(True)
plt.xlabel(r'n$\rightarrow$',fontsize=15)
plt.ylabel(r'Coefficient Magnitude$\rightarrow$',fontsize=15)
plt.title('Loglog Plot of coefficients of $cos(cos(x))$',fontsize=15)
plt.show()


################## Q4. Finding the Fourier series coefficients: Least Squares approach ###################################

x = np.linspace(0,2*np.pi,401)
x = x[:-1]
y = np.linspace(0,2*np.pi,400)

# We want to solve the matrix equation "Ac = b" where c are the fourier coefficients.
"""A"""
A = np.zeros((400,51))
A[:,0] = 1
for i in range(1,26):
    A[:,2*i-1] = np.cos(i*x)
    A[:,2*i] = np.sin(i*x) 
"""b"""
b_exp = exp(x)  
b_coscos = coscos(x)
"""c"""
c_exp = np.linalg.lstsq(A,b_exp, rcond=None)[0]
c_coscos = np.linalg.lstsq(A,b_coscos,rcond=None)[0]


#Runtime is calculated for comparison with the least squares method.
"""integration approach"""
start = timeit.default_timer()
coeff_exp = find_coeff(51,'exp(x)')
elapsed = timeit.default_timer() - start
print('Runtime with integration approach = ',elapsed)

"""linear square approach"""
start = timeit.default_timer()
for i in range(1,26):
    A[:,2*i-1] = np.cos(i*x)
    A[:,2*i] = np.sin(i*x) 
b_exp = exp(x)  
c_exp = np.linalg.lstsq(A,b_exp, rcond=None)[0]
elapsed = timeit.default_timer() - start
print('Runtime with least square approach = ', elapsed)


############## Q5. Plots comparing the coefficients by "Integration" and "Least Square" approaches #######################


# (a) For $e^x$
# semilogy plot
plt.semilogy(range(51),np.abs(coeff_exp),'ro',label='True Value (Integration)')
plt.semilogy(range(51),np.abs(c_exp),'go',label='Predicted Value (Least Squares)')
plt.grid(True)
plt.xlabel(r'n$\rightarrow$',fontsize=15)
plt.ylabel(r'$Coefficient\rightarrow$',fontsize=15)
plt.title('Semilog Plot of coefficients for $e^{x}$',fontsize=15)
plt.legend(loc='upper right')
plt.show()
# loglog plot
plt.loglog(range(51),np.abs(coeff_exp),'ro',label = 'True Value (Integration)')
plt.loglog(range(51),np.abs(c_exp),'go',label='Predicted Value (Least Squares)')
plt.grid(True)
plt.xlabel(r'n$\rightarrow$',fontsize=15)
plt.ylabel(r'$Coefficient\rightarrow$',fontsize=15)
plt.title('Loglog Plot of coefficients of $e^{x}$',fontsize=15)
plt.legend(loc='lower left')
plt.show()


# (b) For $cos(cos(x))$
# semilogy plot
plt.semilogy(range(51),abs(coeff_coscos),'ro',label='True Value (Integration)')
plt.semilogy(range(51),abs(c_coscos),'go',label="Predicted Value (Least Squares)")
plt.grid(True)
plt.xlabel(r'n$\rightarrow$',fontsize=15)
plt.ylabel(r'$Coefficient\rightarrow$',fontsize=15)
plt.title('Semilog Plot of coefficients for $cos(cos(x))$',fontsize=15)
plt.legend(loc='upper right')
plt.show()
# loglog plot 
plt.loglog(range(51),abs(coeff_coscos),'ro',label='True Value (Integration)')
plt.loglog(range(51),abs(c_coscos),'go',label="Predicted Value (Least Squares)")
plt.grid(True)
plt.xlabel(r'n$\rightarrow$',fontsize=15)
plt.ylabel(r'Coefficient$\rightarrow$',fontsize=15)
plt.title('Loglog Plot of coefficients of $cos(cos(x))$',fontsize=15)
plt.legend(loc='upper right')
plt.show()


################# Q6. Calculating the deviation b/w Least square and direct integration cofficients #########################


deviation_exp = abs(coeff_exp - c_exp)
deviation_coscos = abs(coeff_coscos - c_coscos)

max_dev_exp = np.max(deviation_exp)
max_dev_coscos = np.max(deviation_coscos)
print("Largest deviation b/w the two sets of coefficients of e^x =", max_dev_exp)
print("Largest deviation b/w the two sets of coefficients of cos(cos(x)) =", max_dev_coscos)


########### Q7. Plots comparing the function values obtained by the "least squares" method with the "true" value #################


# (a) For $e^x$
# Ac from the estimated values of c represents the function values
"""true"""
x1 = np.linspace(-2*np.pi,4*np.pi,300)
x2 = np.linspace(0,2*np.pi,100)
tiled = np.tile(x2,3)
"""predicted"""
x3 = np.linspace(0,2*np.pi,401)
x3 = x3[:-1]
predicted_exp = np.matmul(A,c_exp)

plt.plot(x1,exp_x,'-r',label='True value')
plt.semilogy(x1,exp(tiled),'-b',label='Expected by fourier series')
plt.plot(x3,predicted_exp,'go',label="Predicted value")
plt.grid(True)
plt.xlabel(r'n$\rightarrow$',fontsize=15)
plt.ylabel(r'$f(x)\rightarrow$',fontsize=15)
plt.title('Plot of $cos(cos(x))$ and its Fourier approximation',fontsize=15)
plt.legend(loc='upper right')
plt.show()


# (b) For $cos(cos(x))$
# Ac from the estimated values of c represents the function values
"""true"""
x1 = np.linspace(-2*np.pi,4*np.pi,300)
coscos_x = coscos(x1)
"""predicted"""
x2 = np.linspace(0,2*np.pi,401)
x2 = x2[:-1]
predicted_coscos = np.matmul(A,c_coscos)

plt.plot(x1,coscos_x,'-r',label='True value')
plt.plot(x2,predicted_coscos,'go',label="Predicted value")
plt.grid(True)
plt.xlabel(r'n$\rightarrow$',fontsize=15)
plt.ylabel(r'$f(x)\rightarrow$',fontsize=15)
plt.title('Plot of $cos(cos(x))$ and its Fourier approximation',fontsize=15)
plt.legend(loc='upper right')
plt.show()