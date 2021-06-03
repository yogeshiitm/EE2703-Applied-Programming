"""
    EE2703 Applied Programming Lab - 2021
    Assignment 5 - The Resistor Problem
    Name - Yogesh Agarwala
    Roll - EE19B130

    To check the code run $python assign5.py <Nx> <Ny> <Radius> <Niter>
    if <Nx> <Ny> <Radius> <Niter> arguments are not provided then the code 
    will run on the default values Nx = 25, Ny = 25, radius = 8, Niter = 1500
"""

import numpy as np
import pylab
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.pyplot as plt
import sys


############################# Taking arguments from the user through commandline ##########################
if(len(sys.argv)==5):
    Nx, Ny, radius, Niter = [int(x) for x in sys.argv[1:5] ]

#default arguments
else:
    Nx = 25
    Ny = 25
    radius = 8
    Niter = 1500


############################# Allocate the potential array and initialize it ##############################
phi=np.zeros((Nx,Ny),dtype = float)
x,y=np.linspace(-0.5,0.5,num=Nx,dtype=float),np.linspace(-0.5,0.5,num=Ny,dtype=float)
Y,X=np.meshgrid(y,x,sparse=False)
phi[np.where(X**2+Y**2<(0.35)**2)]=1.0

#plot potential
plt.xlabel(r"X$\rightarrow$")
plt.ylabel(r"Y$\rightarrow$")
plt.title("Figure 1: Contour plot of the potential")
plt.contourf(X,Y,phi,cmap='Blues')
plt.colorbar()
plt.show()


###################################### Performing the iteration ###########################################
ii = np.where(X**2+Y**2<(0.35)**2)
phi[ii] = 1.0

err = np.zeros(Niter,dtype = float)
for k in range(Niter):
    oldphi = phi.copy()
    #updating potential
    phi[1:-1,1:-1] = 0.25*(phi[1:-1,0:-2] + phi[1:-1,2:] + phi[0:-2,1:-1] + phi[2:,1:-1])
    #applying boudary conditions
    phi[:,0]=phi[:,1]
    phi[:,Nx-1]=phi[:,Nx-2]
    phi[0,:]=phi[1,:]
    phi[Ny-1,:]=0

    phi[ii]=1.0
    err[k] = np.max(np.abs(phi-oldphi))


############################################# Plotting Errors ##############################################
#plotting error on semilog
plt.title("Figure 2: Semilog Error Plot")
plt.xlabel(r"Iteration$\rightarrow$")
plt.ylabel(r"Error$\rightarrow$")
plt.semilogy(range(Niter),err)
plt.show()

#plotting error on loglog
plt.title("Figure 3: Loglog Error Plot")
plt.xlabel(r"Iteration$\rightarrow$")
plt.ylabel(r"Error$\rightarrow$")
plt.loglog((np.asarray(range(Niter))+1),err)
plt.loglog((np.asarray(range(Niter))+1)[::50],err[::50],'ro')
plt.legend(["Real","Every 50th Value"])
plt.show()


######################################## Fitting the Errors ##############################################
def GetFit(y,Niter,lastn=0):
    log_err = np.log(err)[-lastn:]
    X = np.vstack([(np.arange(Niter)+1)[-lastn:],np.ones(log_err.shape)]).T
    log_err = np.reshape(log_err,(1,log_err.shape[0])).T
    return np.linalg.lstsq(X, log_err,rcond=-1)[0]


b,a = GetFit(err,Niter)
b_,a_ = GetFit(err,Niter,500)

x = np.asarray(range(Niter))+1
plt.title("Figure 4: Best Fit for Error on semilog scale")
plt.xlabel(r"Iteration$\rightarrow$")
plt.ylabel(r"Error$\rightarrow$")
plt.semilogy(x,err)
plt.semilogy(x[::100],np.exp(a+b*np.asarray(range(Niter)))[::100],'ro')
plt.semilogy(x[::100],np.exp(a_+b_*np.asarray(range(Niter)))[::100],'bo')
plt.legend(["Errors","Fit1","Fit2"])
plt.show()

plt.title("Figure 5: Best Fit for Error on loglog scale")
plt.xlabel(r"Iteration$\rightarrow$")
plt.ylabel(r"Error$\rightarrow$")
plt.loglog(x,err)
plt.loglog(x[::100],np.exp(a+b*np.asarray(range(Niter)))[::100],'ro')
plt.loglog(x[::100],np.exp(a_+b_*np.asarray(range(Niter)))[::100],'bo')
plt.legend(["Errors","Fit1","Fit2"])
plt.show()


################################### Plotting Maximum Possible Error ######################################
def NetError(a,b,Niter):
    return -a/b*np.exp(b*(Niter+0.5))

#plotting cumulative error
iter=np.arange(100,1501,100)
plt.grid(True)
plt.title('Figure 6: Plot of Cumulative Error values on loglog scale')
plt.loglog(iter,np.abs(NetError(a_,b_,iter)),'ro')
plt.xlabel(r"Iteration$\rightarrow$")
plt.ylabel(r"Net Maximum Error$\rightarrow$")
plt.show()


########################################## Surface Plot of Potential #####################################
fig1=plt.figure(4)
ax=p3.Axes3D(fig1)
plt.title('Figure 7: Surface Plot of Potential')
surf = ax.plot_surface(Y, X, phi.T, rstride=1, cstride=1, cmap=plt.cm.jet)
plt.show()


###################################### Contour Plot of the Potential ####################################
plt.title("Figure 8: Contour plot of the Potential")
plt.xlabel(r"X$\rightarrow$")
plt.ylabel(r"Y$\rightarrow$")
x_c,y_c=np.where(X**2+Y**2<(0.35)**2)
plt.plot((x_c-Nx/2)/Nx,(y_c-Ny/2)/Ny,'ro')
plt.contourf(Y,X[::-1],phi)
plt.colorbar()
plt.show()


########################################### Vector Plot of Currents #######################################
#finding Current density
Jx,Jy = (1/2*(phi[1:-1,0:-2]-phi[1:-1,2:]),1/2*(phi[:-2,1:-1]-phi[2:,1:-1]))

plt.title("Figure 9: Vector plot of Currents")
plt.quiver(Y[1:-1,1:-1],-X[1:-1,1:-1],-Jx[:,::-1],-Jy)
x_c,y_c=np.where(X**2+Y**2<(0.35)**2)
plt.plot((x_c-Nx/2)/Nx,(y_c-Ny/2)/Ny,'ro')
plt.show()