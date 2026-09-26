import os

import numpy as np
from ase import Atom
from ase.io import read, write, Trajectory
from ase.visualize import view

try:
	from surface_finder import doubledict, neighbourlist
	from surface_finder import get_surface_atoms, get_distance

	from three_and_four_fold_sites import get_three_fold_sites, get_four_fold_sites
	from three_and_four_fold_sites import get_applied_three_fold_sites, get_applied_four_fold_sites
	from three_and_four_fold_sites import get_positions_for_new_atoms, update_positions_for_new_atoms, same_position, same_positions

	from other_methods import determine_where_to_place_capping_Br
except Exception as ee:
	from Computational_Silver_Nanoparticle_Exercise_Data.Silver_Prism_Animation.surface_finder import doubledict, neighbourlist
	from Computational_Silver_Nanoparticle_Exercise_Data.Silver_Prism_Animation.surface_finder import get_surface_atoms, get_distance

	from Computational_Silver_Nanoparticle_Exercise_Data.Silver_Prism_Animation.three_and_four_fold_sites import get_three_fold_sites, get_four_fold_sites
	from Computational_Silver_Nanoparticle_Exercise_Data.Silver_Prism_Animation.three_and_four_fold_sites import get_applied_three_fold_sites, get_applied_four_fold_sites
	from Computational_Silver_Nanoparticle_Exercise_Data.Silver_Prism_Animation.three_and_four_fold_sites import get_positions_for_new_atoms, update_positions_for_new_atoms, same_position, same_positions

	from Computational_Silver_Nanoparticle_Exercise_Data.Silver_Prism_Animation.other_methods import determine_where_to_place_capping_Br

from random import uniform, randrange, shuffle

def silver_nanoprism_growing_model(path_to_input,change_of_creating_new_100_surface,max_no_of_atoms_added_in_simulation=1000,cap_at_end_of_simulation=False):

	if not (0.0 <= change_of_creating_new_100_surface <= 1.0):
		raise Exception('change_of_creating_new_100_surface must be between 0.0 and 1.0. You gave change_of_creating_new_100_surface='+str(change_of_creating_new_100_surface))

	# read in the initial nanoparticle system
	system = read(path_to_input)
	system.set_tags(0)

	# Other initial variables
	traj_path = '.'.join(path_to_input.split('.')[:-1:])+'_animation.traj'
	symbol = system[0].symbol
	cutoff = 3.0
	cluster_positions = system.get_positions()

	# Make the initial nrighbourhood matrix
	print('making initial distance matrix')
	print('making initial full neighbours matrix')
	distances_between_atoms = doubledict()
	full_neighbourlist = neighbourlist()
	n_atoms = len(cluster_positions)
	for index1 in range(n_atoms):
		# Vectorised: one NumPy call per row instead of one per pair, to
		# avoid N^2 individual get_distance() calls on large seeds.
		if index1+1 < n_atoms:
			row_distances = np.linalg.norm(cluster_positions[index1+1:]-cluster_positions[index1],axis=1)
			for offset in range(len(row_distances)):
				index2 = index1+1+offset
				distance = row_distances[offset]
				distances_between_atoms[(index1,index2)] = distance
				if distance <= cutoff:
					full_neighbourlist.set(index1,index2)

	# Get the neighbourhoods of only surface atoms, as well as the triangles, squares, and nearly squares
	# Also get the position of where to place the next atom on the surface
	print('Getting surface neighbour lists')
	surface_neighbourlist = get_surface_atoms(system,distances_between_atoms,full_neighbourlist,cutoff,last_index=True)
	print('getting triangle surfaces')
	triangles = get_three_fold_sites(surface_neighbourlist)
	print('getting square surfaces')
	squares, nearly_squares = get_four_fold_sites(surface_neighbourlist,system,cutoff)
	print('getting new possible positions')
	tri_pos_new_atoms, tri_pos_new_atoms_indices, nearly_squ_pos_new_atoms, nearly_squ_pos_new_atoms_indices, squ_pos_new_atoms, squ_pos_new_atoms_indices = get_positions_for_new_atoms(system,triangles,squares,nearly_squares)

	#Tag which atoms are squares for my interest. For debugging
	tags = system.get_tags() #get_chemical_symbols()
	for index in range(len(tags)):
		tags[index] = 0 # 'Ag'
	for indices in squares:
		for index in indices:
			tags[index] = 1 # 'Fe'
	system.set_tags(tags) #set_chemical_symbols(tags)

	# Create a new trajectory file to save simulation to
	if os.path.exists(traj_path):
		os.remove(traj_path)
	with Trajectory(traj_path,'a') as traj_file:
		traj_file.write(system.copy())

	# Make a note of history of surface data, including 100 surfaces. For debugging
	surface_data = []
	surface_data.append(surface_neighbourlist.copy())
	all_squares = []
	all_squares.append(list(squares))
	all_squ_pos_new_atoms_indices = []
	all_squ_pos_new_atoms_indices.append(list(squ_pos_new_atoms_indices)) 

	for counter in range(1,max_no_of_atoms_added_in_simulation+1):
		print('----------------------------------')
		print('Adding atom '+str(counter))

		# Set up system based on if we are adding an atom to a 100 (square) or 111 (triangle) surface. 
		square_or_triangle = uniform(0, 1)
		if square_or_triangle <= change_of_creating_new_100_surface:
			positions_to_add = squ_pos_new_atoms
			positions_to_add_index = squ_pos_new_atoms_indices
		else:
			positions_to_add = tri_pos_new_atoms
			positions_to_add_index = tri_pos_new_atoms_indices

		# Print details
		print('squares: '+str(len(squ_pos_new_atoms)))
		print('triangles: '+str(len(tri_pos_new_atoms)))
		if len(squ_pos_new_atoms) == 0:
			break

		# Determine which site to add an atom to.
		random_number = randrange(0, len(positions_to_add), 1)
		random_position = positions_to_add[random_number].copy()
		index_set_to_check = tuple(positions_to_add_index[random_number])

		# Remove this position from the list, as we are now adding an atom to this position
		del positions_to_add[random_number]
		del positions_to_add_index[random_number]

		# If this position is found in the squ_pos_new_atoms and tri_pos_new_atoms lists, 
		# remove them to prevent another atom being added to this site, as we are adding an atom to this site now.  
		if any(same_positions(random_position,system.positions)):
			for index in range(len(squ_pos_new_atoms)-1,-1,-1):
				check_position = squ_pos_new_atoms[index]
				if same_position(random_position,check_position):
					del squ_pos_new_atoms[index]
					del squ_pos_new_atoms_indices[index]
			for index in range(len(tri_pos_new_atoms)-1,-1,-1):
				check_position = tri_pos_new_atoms[index]
				if same_position(random_position,check_position):
					del tri_pos_new_atoms[index]
					del tri_pos_new_atoms_indices[index]

		# remove the index_set_to_check from the triangles, nearly_squares, and squares lists.
		if len(index_set_to_check) == 3:
			if index_set_to_check in triangles:
				triangles.remove(index_set_to_check)
			if index_set_to_check in nearly_squares:
				nearly_squares.remove(index_set_to_check)
		elif len(index_set_to_check) == 4:
			if index_set_to_check in squares:
				squares.remove(index_set_to_check)
		
		# Create the new atom and place it in the nanoparticle system. 
		atom = Atom(symbol=symbol,position=random_position,tag=counter)
		system.append(atom)

		# Add this atom to the full_neighbourlist <- FULL NEIGHBOUR LIST
		cluster_positions = system.get_positions()
		#print('making initial full neighbours matrix')
		end_of_system = len(cluster_positions)-1
		# Vectorised: one NumPy call for the new atom against every existing
		# atom, instead of end_of_system individual get_distance() calls --
		# this loop runs once per atom added, so its per-call overhead was
		# the main cost driver on large seeds (it grows with particle size).
		new_atom_distances = np.linalg.norm(cluster_positions[:end_of_system]-cluster_positions[end_of_system],axis=1)
		for index in range(end_of_system):
			distance = new_atom_distances[index]
			distances_between_atoms[(index,end_of_system)] = distance
			if distance <= cutoff:
				full_neighbourlist.set(index,end_of_system)

		# Check that this newly added atom was placed in a position that it has neighbours.
		# If it does not, we dont want that to happen, all our atoms added should have at least one neighbour
		# If something has gone wrong, this exception should tell us by having a fit. 
		try:
			len(full_neighbourlist.get(end_of_system))
		except:
			print('check')
			dists = []
			end_of_system = len(cluster_positions)-1
			for index in range(end_of_system):
				distance = get_distance(cluster_positions[index],cluster_positions[end_of_system])
				dists.append(distance)
			print(min(dists))
			return traj_path
			import pdb; pdb.set_trace()

		# Determine if any surface atoms that neighbour the newly added neighbour have now become bulk atoms. 
		# <- NEIGHBOUR LIST OF ONLY THE SURFACE
		#print('Getting surface neighbour lists')
		surface_atoms_turned_bulk = []
		for index in full_neighbourlist.get(end_of_system):
			if len(full_neighbourlist.get(index)) == 12:
				surface_neighbourlist.remove(index)
				surface_atoms_turned_bulk.append(index)
			else:
				surface_neighbourlist.set(index,end_of_system)
		surface_data.append(surface_neighbourlist.copy())

		# We now want to determine the new places that atoms could be added to the surface
		# I.e. find all the new square and triangle surfaces created by adding this atom to the nanoparticle.
		# This involves finding all the square and triangle surfaces involving this new atom and its neighbours
		indices_to_explore = surface_neighbourlist[end_of_system] + [end_of_system]
		#print('getting triangle surfaces')
		triangles = get_applied_three_fold_sites(surface_neighbourlist,triangles,surface_atoms_turned_bulk,indices_to_explore)
		#print('getting square surfaces')
		squares, nearly_squares = get_applied_four_fold_sites(surface_neighbourlist,system,cutoff,   squares,nearly_squares,   surface_atoms_turned_bulk,indices_to_explore)
		all_squares.append(list(squares))
		#print('getting new possible positions')
		tri_pos_new_atoms, tri_pos_new_atoms_indices, nearly_squ_pos_new_atoms, nearly_squ_pos_new_atoms_indices, squ_pos_new_atoms, squ_pos_new_atoms_indices = update_positions_for_new_atoms(system,triangles,squares,nearly_squares,      tri_pos_new_atoms,tri_pos_new_atoms_indices,nearly_squ_pos_new_atoms,nearly_squ_pos_new_atoms_indices,squ_pos_new_atoms,squ_pos_new_atoms_indices,      surface_atoms_turned_bulk,indices_to_explore)
		all_squ_pos_new_atoms_indices.append(list(squ_pos_new_atoms_indices))

		# Tag all the square surfaces. 
		tags = system.get_tags() #get_chemical_symbols()
		for index in range(len(tags)):
			tags[index] = 0 #'Ag'
		for indices in squares: #squ_pos_new_atoms_indices:
			for index in indices:
				tags[index] = 1 #'Fe'
		system.set_tags(tags) #set_chemical_symbols(tags)

		# Write data to the trajectory file. 
		#print('Adding image to Traj')
		with Trajectory(traj_path,'a') as traj_file:
			traj_file.write(system.copy())

	# Adding Bromines as capping agents
	if cap_at_end_of_simulation:
		rest_of_atoms_to_cap = list(set(surface_neighbourlist.keys()))
		shuffle(rest_of_atoms_to_cap)
		for index in rest_of_atoms_to_cap:
			cap_position = determine_where_to_place_capping_Br(index,system,full_neighbourlist)
			# Create the new atom and place it in the nanoparticle system. 
			atom = Atom(symbol='Br',position=cap_position,tag=counter)		
			system.append(atom)
			# Write data to the trajectory file. 
			with Trajectory(traj_path,'a') as traj_file:
				traj_file.write(system.copy())

	print('----------------------------------')
	print('The simulation has now finished')
	print('----------------------------------')
	return traj_path






