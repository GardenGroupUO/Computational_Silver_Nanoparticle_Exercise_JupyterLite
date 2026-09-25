import time
from ase.optimize import FIRE
from gupta_numpy import Gupta

def Minimisation_Function(cluster, collection, cluster_name):
    cluster.pbc = False
    r0 = 4.09 / (2.0 ** 0.5)
    Gupta_parameters = {'Ag': [10.85, 3.18, 0.1031, 1.190, r0]}
    cluster.calc = Gupta(Gupta_parameters, cutoff=1000, debug=False)
    dyn = FIRE(cluster, logfile=None)
    startTime = time.time(); converged = False
    try:
        dyn.run(fmax=0.01, steps=5000)
        converged = dyn.converged()
        if not converged:
            errorMessage = 'The optimisation of cluster ' + str(cluster_name) + ' did not optimise completely.'
            print(errorMessage)
    except Exception:
        print('Local Optimiser Failed for some reason.')
    endTime = time.time()
    Info = {}
    Info['INFO.txt'] = 'No of Force Calls: ' + str(dyn.get_number_of_steps()) + '\n'
    Info['INFO.txt'] += 'Time (s): ' + str(endTime - startTime) + '\n'
    return cluster, converged, Info
