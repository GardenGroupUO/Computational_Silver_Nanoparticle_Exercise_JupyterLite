from ase.cluster import wulff_construction
from ase.data import atomic_numbers
from ase.data.colors import jmol_colors

def faces_of_nanoparticles():

    surfaces = [(1,0,0),(1,1,1)]
    esurf = [1.0,0.9]

    size =200
    atoms = wulff_construction('Ag',surfaces,esurf,size,'fcc',rounding='above')
    atoms.rotate(20,'y')
    atoms.set_cell([0,0,0])

    # ---------------------------------------------------------
    colours = {}
    atoms_100 = [183]
    for n in atoms_100:
        colours[n] = (0,0,0) #(255/255.0, 105/255.0, 180/255.0) #jmol_colors[atomic_numbers['Mn']]

    atoms_100a = [66, 48, 111, 129]
    for n in atoms_100a:
        colours[n] = jmol_colors[atomic_numbers['O']] # 'Fe' 

    '''
    # Second nearest neighbours
    atoms_100b = [65, 110,182, 145]
    for n in atoms_100b:
        colours[n] = jmol_colors[atomic_numbers['P']] # 'Pd'
    '''

    # ---------------------------------------------------------

    atoms_111 = [128]
    for n in atoms_111:
        colours[n] = (0,0,0) # (255/255.0, 105/255.0, 180/255.0) #jmol_colors[atomic_numbers['Mn']]

    atoms_111a = [184, 185, 173, 168, 132, 136]
    for n in atoms_111a:
        colours[n] = (188/255.0, 45/255.0, 255/255.0) #jmol_colors[atomic_numbers['Hf']] # 'Fe'

    '''
    # Second nearest neighbours
    atoms_111b = [189, 147, 131, 115, 169, 196] #[200, 189, 191, 147, 196, 195, 130, 146, 131, 169, 167, 115]
    for n in atoms_111b:
        colours[n] = jmol_colors[atomic_numbers['Th']]  # (17/255.0, 138/255.0, 178/255.0) #jmol_colors[atomic_numbers['Ca']] # 'Mg' 
    '''

    return atoms, colours

# -------------------------------------------

def number_of_neighbouring_atoms():

    surfaces = [(1,0,0),(1,1,1)]
    esurf = [1.0,0.9]

    size =200
    atoms = wulff_construction('Ag',surfaces,esurf,size,'fcc',rounding='above')
    atoms.rotate(20,'y')
    atoms.set_cell([0,0,0])

    colours = {}
    atoms_100 = [183]
    for n in atoms_100:
        colours[n] = (0,0,0) #(255/255.0, 105/255.0, 180/255.0) #jmol_colors[atomic_numbers['Mn']]

    atoms_100a = [66, 48, 111, 129] + [63, 125, 107, 126]
    for n in atoms_100a:
        colours[n] = jmol_colors[atomic_numbers['O']] # 'Fe' 

    # ---------------------------------------------------------

    atoms_111 = [128]
    for n in atoms_111:
        colours[n] = (0,0,0) # (255/255.0, 105/255.0, 180/255.0) #jmol_colors[atomic_numbers['Mn']]

    atoms_111a = [184, 185, 173, 168, 132, 136] + [135, 171, 119]
    for n in atoms_111a:
        colours[n] = (188/255.0, 45/255.0, 255/255.0) #jmol_colors[atomic_numbers['Hf']] # 'Fe'

    transparencies = {}
    for index in range(len(atoms)):
        if index not in atoms_100+atoms_100a+atoms_111+atoms_111a:
            transparencies[index] = 0.9

    return atoms, colours, transparencies

# -------------------------------------------

def number_of_neighbouring_atoms_in_middle_of_nanoparticle():

    surfaces = [(1,0,0),(1,1,1)]
    esurf = [1.0,0.9]

    size =200
    atoms = wulff_construction('Ag',surfaces,esurf,size,'fcc',rounding='above')
    atoms.rotate(20,'y')
    atoms.set_cell([0,0,0])

    atoms_100 = [124]
    atoms_100b = [index for index in range(len(atoms)) if ((atoms.get_distance(index,atoms_100[0]) < 3.0) and not (index == atoms_100[0]))]
    colours = {}
    for n in atoms_100:
        colours[n] = (0,0,0) #jmol_colors[atomic_numbers['Mn']] 
    for n in atoms_100b:
        colours[n] = jmol_colors[atomic_numbers['Au']] # jmol_colors[atomic_numbers['Fe']]
    transparencies = {}
    for index in range(len(atoms)):
        if index not in atoms_100+atoms_100b:
            transparencies[index] = 0.9

    return atoms, colours, transparencies
