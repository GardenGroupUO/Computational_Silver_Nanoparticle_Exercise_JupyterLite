import numpy as np
from tqdm import tqdm

from ase.build import fcc100, fcc111
from ase.lattice.cubic import FaceCenteredCubic

from ase.calculators.emt import EMT
from ase.optimize import FIRE

def get_energy_of_bulk_model(element):
    '''
    energies = []
    lattice_params = np.arange(3.2,4.5,0.05)
    print('Getting Bulk Energy. This may take a minute.')
    print('Scanning across lattice constants')
    pbar = tqdm(lattice_params,unit='LC')
    for lc in pbar:
        pbar.set_description("Processing Lattice Constant (LC) = %.2f A" % lc)
        bulk = FaceCenteredCubic(size=(6,6,6),symbol=element,pbc=(1,1,1),latticeconstant=lc)
        bulk.set_calculator(EMT())
        e_atoms = bulk.get_potential_energy()
        energies.append(e_atoms)
    print()
    lowest_energy, lattice_constant = min(zip(energies,lattice_params))
    print()
    E_BM = lowest_energy/len(bulk)
    return E_BM, lattice_constant
    '''
    EMT_data = {'Al': (-4.218638796183743, 3.9943), 'Cu': (-6.079527211932282, 3.5898), 'Ag': (-0.31696368735072156, 4.0636), 'Au': (-0.11675697957541331, 4.0562), 'Ni': (-11.497147666585278, 3.4871), 'Pd': (-0.2332085339018164, 3.8787), 'Pt': (-0.1291913694828537, 3.9218)}
    if element not in EMT_data:
        raise Exception('Error, you need to enter one of the following elements and try again: '+str(list(EMT_data.keys())))
    E_BM, lattice_constant = EMT_data[element]
    return E_BM, lattice_constant

def get_square_surface_model(element,lattice_constant):
    x_number_of_atoms = 6
    y_number_of_atoms = 6
    z_number_of_atoms = 4
    slab = fcc100(element,size=(x_number_of_atoms,y_number_of_atoms,z_number_of_atoms),a=lattice_constant)
    slab.center(vacuum=10.0,axis=2,about=None)
    slab.set_calculator(EMT())
    dyn = FIRE(slab,logfile=None)
    dyn.run(fmax=0.01)
    return slab, x_number_of_atoms, y_number_of_atoms, z_number_of_atoms

def get_energy_of_square_surface_model(element,lattice_constant):
    slab, x_number_of_atoms, y_number_of_atoms, z_number_of_atoms = get_square_surface_model(element,lattice_constant)
    E_SM = slab.get_potential_energy()
    return E_SM, x_number_of_atoms*y_number_of_atoms*2, x_number_of_atoms*y_number_of_atoms*z_number_of_atoms, slab

def get_triangle_surface_model(element,lattice_constant):
    x_number_of_atoms = 6
    y_number_of_atoms = 6
    z_number_of_atoms = 4
    slab = fcc111(element,size=(x_number_of_atoms,y_number_of_atoms,4),a=lattice_constant)
    slab.center(vacuum=10.0,axis=2,about=None)
    slab.set_calculator(EMT())
    dyn = FIRE(slab,logfile=None)
    dyn.run(fmax=0.01)
    return slab, x_number_of_atoms, y_number_of_atoms, z_number_of_atoms

def get_energy_of_triangle_surface_model(element,lattice_constant):
    slab, x_number_of_atoms, y_number_of_atoms, z_number_of_atoms = get_triangle_surface_model(element,lattice_constant)
    E_SM = slab.get_potential_energy()
    return E_SM, x_number_of_atoms*y_number_of_atoms*2, x_number_of_atoms*y_number_of_atoms*z_number_of_atoms, slab

# -------------------------------------------------------------------------

def eV_per_atom_into_J_per_m_squared(eV_per_atom,slab,surface_atoms):

    eV_to_J = 1.60218e-19

    #Calculating surface area of non-orthogonal surface unit cell

    cell_vecs=slab.get_cell()
    vec1=cell_vecs[0]
    vec2=cell_vecs[1]

    b=vec1[0]
    h=vec2[1]

    surface_area = (b * h /surface_atoms) * 1e-20 ## in m^2

    J_per_m_squared = eV_per_atom * (eV_to_J / surface_area)  ### J m^-2
    return J_per_m_squared

# -------------------------------------------------------------------------
# Obtain information about lattice constaces

def rounding(number):
    return round(number,7)

def get_lattice_contant_and_energy_of_bulk_model_from_lattice_curve(element,lc_low=3.0,lc_high=5.0):
    energies_and_lcs = []
    lc_interval = 0.0001
    print('Getting Bulk Energy for '+str(element)+'. This may take a minute.')
    print('Scanning across lattice constants')
    current_lc_low = lc_low
    current_lc_high = lc_high
    current_lc_interval = 0.1
    counter = 0
    while current_lc_interval >= lc_interval:
        print('Measuring between '+str(current_lc_low)+' A and '+str(current_lc_high)+' A at intervals of '+str(current_lc_interval)+' A.')
        lattice_params = np.arange(current_lc_low,current_lc_high+current_lc_interval,current_lc_interval)
        pbar = tqdm(lattice_params,unit='LC')
        for lc in pbar:
            lc = rounding(lc)
            pbar.set_description("Processing Lattice Constant (LC) = "+str(lc)+" A")
            bulk = FaceCenteredCubic(size=(6,6,6),symbol=element,pbc=(1,1,1),latticeconstant=lc)
            bulk.set_calculator(EMT())
            e_atoms = bulk.get_potential_energy()
            energies_and_lcs.append((e_atoms,lc))
        lowest_energy, current_lattice_constant = min(energies_and_lcs)
        current_lc_low = rounding(current_lattice_constant - current_lc_interval)
        current_lc_high = rounding(current_lattice_constant + current_lc_interval)
        current_lc_interval = rounding(current_lc_interval/10.0)
        counter += 1
    E_BM, lattice_constant = min(energies_and_lcs)

    energies_and_lcs.sort(key=lambda x:x[1])
    #energies, lattice_params = zip(*energies_and_lcs)
    energies =       [i[0] for i in energies_and_lcs]
    lattice_params = [i[1] for i in energies_and_lcs]

    bulk = FaceCenteredCubic(size=(6,6,6),symbol=element,pbc=(1,1,1),latticeconstant=lattice_constant)
    no_of_bulk = len(bulk)
    energies_per_atom = [energy/no_of_bulk for energy in energies]
    with open('Lattice_curve_'+str(element)+'.txt','w') as Lattice_CurveTXT:
        Lattice_CurveTXT.write(str(lattice_params)+'\n')
        Lattice_CurveTXT.write(str(energies_per_atom)+'\n')
    return E_BM, lattice_constant
    
import matplotlib.pyplot as plt
def make_LatticeCurve_plot(element):
    filename = make_plot(element)
    plt.savefig(filename+'.png')
    plt.clf()
    plt.cla()

def take_a_look_at_LatticeCurve(element):
    make_plot(element)
    plt.show()
    plt.clf()
    plt.cla()

def make_plot(element):
    filename = 'Lattice_curve_'+str(element)
    with open(filename+'.txt','r') as Lattice_CurveTXT:
        lattice_params    = eval(Lattice_CurveTXT.readline().rstrip())
        energies_per_atom = eval(Lattice_CurveTXT.readline().rstrip())
    plt.plot(lattice_params, energies_per_atom, color='green', linestyle='dashed', linewidth = 3, marker='o', markerfacecolor='blue', markersize=6)
    plt.xlabel('lattice constant (A)')
    plt.ylabel('Energy per atom (eV/Atom)')
    return filename