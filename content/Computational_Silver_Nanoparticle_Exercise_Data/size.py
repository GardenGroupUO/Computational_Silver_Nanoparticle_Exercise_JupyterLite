import os
from ase.cluster import wulff_construction
'''
if 'Computational_Silver_Nanoparticle_Exercise_Data' in os.listdir('.'):
	from Computational_Silver_Nanoparticle_Exercise_Data.viewer.x3d_viewer import view_x3d
else:
	from viewer.x3d_viewer import view_x3d
'''
surfaces = [(1,0,0),(1,1,1)]
surf_e_100 = 0.9
surf_e_111 = 1.0

def make_nanoparticle(size=None):
	#### Change the size of the cluster below and see the changes ####
	if size==None:
		while True : 
			size = input("What size nanoparticle do you want to make?: ")
			if size.isdigit() :
				size = int(size)
				if 13 <= size :
					if 12 <= size <= 11421 :  	
						print(size)
						break
					else :
						print("The size has to be between 13 and 11421. Try again.")
				else : 
					print("This is not enough atoms to make a nanoparticle. Try again.")
			else : 
				print("You have not entered a valid number. Try again.")
	elif not isinstance(size,int):
		print('Error: You input for size needs to be a int (integer). Change this and try again')
		
	esurf = [surf_e_100,surf_e_111]
	atoms = wulff_construction('Ag',surfaces,esurf,size,'fcc',rounding='above')
	atoms.cell=[0,0,0]
	print('This nanoparticle contains '+str(len(atoms))+' atoms.')
	#view_x3d(atoms)
	return atoms