import os
import time
from ase.optimize import FIRE

if 'Computational_Silver_Nanoparticle_Exercise_Data' in os.listdir('.'):
    from Computational_Silver_Nanoparticle_Exercise_Data.Set_of_RunMinimisation_Files.gupta_numpy import Gupta
else:
    try:
        from Set_of_RunMinimisation_Files.gupta_numpy import Gupta
    except Exception:
        from gupta_numpy import Gupta

def Minimisation_Function(cluster, collection, cluster_name):
    cluster.pbc = False
    Gupta_parameters = {'Cu': [10.960, 2.2780, 0.0855, 1.224, 2.556]}
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
