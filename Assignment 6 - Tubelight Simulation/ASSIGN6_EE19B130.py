"""
    EE2703 Applied Programming Lab - 2019
    Assignment 6 - Tubelight Simulation
    Name - Yogesh Agarwala
    Roll - EE19B130
"""

import numpy as np
import pandas as pd
import sys
from pylab import *

"""
    Taking arguments from the user through commandline
    and if the arguments are not provided then the code 
    will run on the default values
"""
#command line input
if(len(sys.argv)==7):
    n,M,nk,u0,p,Msig = [int(x) for x in sys.argv[1:7] ]

#default arguments
else:
    n= 100
    M=5
    nk=500
    u0=7
    p=0.5
    Msig=1


"""
    Simulate a tubelight and return the electron positions 
    and velocities, and positions of photon emissions.
"""
def simulateTubelight(n,M,nk,u0,p,Msig):

    xx = zeros(n*M)
    u = zeros(n*M)
    dx = zeros(n*M)

    I = []
    X = []
    V = []

    for k in range(nk):

        # add new electrons
        m=int(randn()*Msig+M)
        jj = where(xx==0)
        xx[jj[0][:m]]=1

        # find electron indices
        ii = where(xx>0)

        # add to history lists
        X.extend(xx[ii].tolist())
        V.extend(u[ii].tolist())

        # update positions and speed
        dx[ii] = u[ii]+0.5
        xx[ii]+=dx[ii]
        u[ii]+=1

        # anode check
        kk = where(xx>=n)
        xx[kk]=0
        u[kk]=0

        # ionization check
        kk = where(u>=u0)[0]
        ll=where(rand(len(kk))<=p)
        kl=kk[ll]

        # ionize
        dt = rand(len(kl))
        xx[kl]=xx[kl]-dx[kl]+((u[kl]-1)*dt+0.5*dt*dt)
        u[kl]=0

        # add emissions
        I.extend(xx[kl].tolist())
        
    return X,V,I



"""
    Plot histograms for X and I, and a phase space using X and V.
    Returns the emission intensities and locations of histogram bins.
"""
def plotGraphs(X,V,I):
    
    # electron density
    figure()
    hist(X,bins=n,cumulative=False)
    title("Electron density")
    xlabel("$x$")
    ylabel("Number of electrons")
    show()

    # emission instensity
    figure()
    ints,bins,trash = hist(I,bins=n)
    title("Emission Intensity")
    xlabel("$x$")
    ylabel("I")
    show()

    # electron phase space
    figure()
    scatter(X,V,marker='x')
    title("Electron Phase Space")
    xlabel("$x$")
    ylabel("$v$")
    show()
    
    return ints,bins


"""
Running the simulation
"""
X,V,I = simulateTubelight(n,M,nk,u0,p,Msig)
ints, bins = plotGraphs(X,V,I)

# Tabulate emission counts
xpos=0.5*(bins[0:-1]+bins[1:])
M = np.c_[xpos,ints]
df = pd.DataFrame(M,columns=['xpos','count'])
print("Intensity Data:")
print(df.to_string(index=False))