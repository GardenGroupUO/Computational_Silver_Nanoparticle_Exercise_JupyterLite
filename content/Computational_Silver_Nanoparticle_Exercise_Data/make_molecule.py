from ase.build import molecule

def make_molecule(molecule_name):
	atoms = molecule(molecule_name)
	if molecule_name == 'H2O':
		atoms.rotate(90,'z')
		atoms.rotate(90,'x')
	elif molecule_name == 'NaCl':
		atoms.rotate(90,'y')
	elif molecule_name == 'CH3SiH3':
		atoms.rotate(90,'y')
	return atoms