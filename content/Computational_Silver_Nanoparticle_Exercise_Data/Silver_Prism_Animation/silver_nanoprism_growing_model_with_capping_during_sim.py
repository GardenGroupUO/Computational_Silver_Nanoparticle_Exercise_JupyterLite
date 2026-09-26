import os
import numpy as np
from copy import deepcopy

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

from random import uniform, randrange, choice, shuffle

def silver_nanoprism_growing_model(path_to_input,chance_of_creating_new_100_surface_111_surface_bromine_capping,max_no_of_atoms_added_in_simulation=1000):

	if not (sum(chance_of_creating_new_100_surface_111_surface_bromine_capping) == 1.0):
		raise Exception('chance_of_creating_new_100_surface_111_surface_bromine_capping must be between 0.0 and 1.0. You gave chance_of_creating_new_100_surface_111_surface_bromine_capping='+str(chance_of_creating_new_100_surface_111_surface_bromine_capping))

	# determine the barriers in chance between making 111 surfaces, 100 surfaces, or capping with a bromine.
	barrier_100_111 = chance_of_creating_new_100_surface_111_surface_bromine_capping[0]
	barrier_111_cap = chance_of_creating_new_100_surface_111_surface_bromine_capping[0] + chance_of_creating_new_100_surface_111_surface_bromine_capping[1]

	# read in the initial nanoparticle system
	system = read(path_to_input)
	system.set_tags(0)

	# Other initial variables
	traj_path = '.'.join(path_to_input.split('.')[:-1:])+'_animation.traj'
	nanoparticle_symbol = system[0].symbol
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
	surface_neighbourlist_excluding_capping = deepcopy(surface_neighbourlist)
	print('getting triangle surfaces')
	triangles = get_three_fold_sites(surface_neighbourlist_excluding_capping)
	print('getting square surfaces')
	squares, nearly_squares = get_four_fold_sites(surface_neighbourlist_excluding_capping,system,cutoff)
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
	surface_data.append(surface_neighbourlist_excluding_capping.copy())
	all_squares = []
	all_squares.append(list(squares))
	all_squ_pos_new_atoms_indices = []
	all_squ_pos_new_atoms_indices.append(list(squ_pos_new_atoms_indices)) 

	# This list records which atoms have been capped
	atoms_to_not_add_new_atoms_to = []

	for counter in range(1,max_no_of_atoms_added_in_simulation+1):
		# Determine when the simulation is over
		any_sites_available = len(squ_pos_new_atoms) + len(tri_pos_new_atoms)
		if any_sites_available == 0:
			break
		if (chance_of_creating_new_100_surface_111_surface_bromine_capping) == 0 and (len(squ_pos_new_atoms) == 0):
			break
		any_square_sites_available = len(squ_pos_new_atoms)
		any_triangle_sites_available = len(tri_pos_new_atoms)

		# Determine what we are doing, adding an atom to a 100 surface (square), to a 111 surface (triangle), or capping.
		add_atom_to_square_surface = False
		add_atom_to_triangle_surface = False
		perform_capping = False	

		while True:
			square_triangle_or_cap = uniform(0, 1)
			if square_triangle_or_cap <= barrier_100_111:
				if any_square_sites_available == 0:
					continue
				add_atom_to_square_surface = True
				break
			elif barrier_100_111 < square_triangle_or_cap <= barrier_111_cap:
				if any_triangle_sites_available == 0:
					continue
				add_atom_to_triangle_surface = True
				break
			else:
				if any_sites_available == 0:
					continue
				perform_capping = True
				break

		# Set up system based on if we are adding an atom to a 100 (square) or 111 (triangle) surface, or capping.
		if add_atom_to_square_surface:
			positions_to_add = squ_pos_new_atoms
			positions_to_add_index = squ_pos_new_atoms_indices
			symbol = nanoparticle_symbol
			cap = False
		elif add_atom_to_triangle_surface:
			positions_to_add = tri_pos_new_atoms
			positions_to_add_index = tri_pos_new_atoms_indices
			symbol = nanoparticle_symbol
			cap = False
		elif perform_capping:
			#import pdb; pdb.set_trace()
			while True:
				add_capping_to_which_surface_atom = choice(list(surface_neighbourlist_excluding_capping.keys()))
				no_of_neighbours = len(full_neighbourlist[add_capping_to_which_surface_atom])

				has_squ_surface = False
				for squ_indices in squ_pos_new_atoms_indices:
					if add_capping_to_which_surface_atom in squ_indices:
						has_squ_surface = True
						break
				if has_squ_surface:
					if no_of_neighbours <= 8:
						break

				has_tri_surface = False
				for tri_indices in tri_pos_new_atoms_indices:
					if add_capping_to_which_surface_atom in tri_indices:
						has_tri_surface = True
						break
				if has_tri_surface:
					if no_of_neighbours <= 9:
						break
				
			atoms_to_not_add_new_atoms_to.append(add_capping_to_which_surface_atom)
			cap = True

		print('----------------------------------')
		if add_atom_to_square_surface:
			print('Adding atom '+str(counter)+' ('+str(symbol)+') to square site.')
		elif add_atom_to_triangle_surface:
			print('Adding atom '+str(counter)+' ('+str(symbol)+') to triangle site.')
		elif perform_capping:
			print('Adding Capping Agent.')
		print('squares: '+str(len(squ_pos_new_atoms)))
		print('triangles: '+str(len(tri_pos_new_atoms)))

		if not cap:
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
			# atom, instead of end_of_system individual get_distance() calls.
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
				import pdb; pdb.set_trace()
				return traj_path
				

			# Determine if any surface atoms that neighbour the newly added neighbour have now become bulk atoms. 
			# <- NEIGHBOUR LIST OF ONLY THE SURFACE
			#print('Getting surface neighbour lists')
			surface_atoms_turned_bulk = []
			for index in full_neighbourlist.get(end_of_system):
				if len(full_neighbourlist.get(index)) == 12:
					# This atom is now a bulk atom, so remove it from surface_neighbourlist and surface_neighbourlist_excluding_capping
					surface_neighbourlist_excluding_capping.remove(index)
					surface_neighbourlist.remove(index)
					surface_atoms_turned_bulk.append(index)
				else:
					# Add that this newly added atom neighbours the index atom in the surface_neighbourlist_excluding_capping
					surface_neighbourlist.set(index,end_of_system)
					surface_neighbourlist_excluding_capping.set(index,end_of_system)
			surface_data.append(surface_neighbourlist_excluding_capping.copy()) # add this to the history of the surface information for debugging if needed

			# We now want to determine the new places that atoms could be added to the surface
			# I.e. find all the new square and triangle surfaces created by adding this atom to the nanoparticle.
			# This involves finding all the square and triangle surfaces involving this new atom and its neighbours
			indices_to_explore = surface_neighbourlist_excluding_capping[end_of_system] + [end_of_system]
			#print('getting triangle surfaces')
			triangles = get_applied_three_fold_sites(surface_neighbourlist_excluding_capping,triangles,surface_atoms_turned_bulk,indices_to_explore)
			#print('getting square surfaces')
			squares, nearly_squares = get_applied_four_fold_sites(surface_neighbourlist_excluding_capping,system,cutoff,   squares,nearly_squares,   surface_atoms_turned_bulk,indices_to_explore)
			all_squares.append(list(squares)) # add the squares to the history of squares if needed for debugging. 
			#print('getting new possible positions')
			tri_pos_new_atoms, tri_pos_new_atoms_indices, nearly_squ_pos_new_atoms, nearly_squ_pos_new_atoms_indices, squ_pos_new_atoms, squ_pos_new_atoms_indices = update_positions_for_new_atoms(system,triangles,squares,nearly_squares,      tri_pos_new_atoms,tri_pos_new_atoms_indices,nearly_squ_pos_new_atoms,nearly_squ_pos_new_atoms_indices,squ_pos_new_atoms,squ_pos_new_atoms_indices,      surface_atoms_turned_bulk,indices_to_explore)
			all_squ_pos_new_atoms_indices.append(list(squ_pos_new_atoms_indices)) # add the nearly_squares to the history of nearly_squares if needed for debugging. 

			# Tag all the square surfaces. 
			tags = system.get_tags() #get_chemical_symbols()
			for index in range(len(tags)):
				tags[index] = 0 #'Ag'
			for indices in squares: #squ_pos_new_atoms_indices:
				for index in indices:
					tags[index] = 1 #'Fe'
			system.set_tags(tags) #set_chemical_symbols(tags)

		else:
			#import pdb; pdb.set_trace()
			cap_position = determine_where_to_place_capping_Br(add_capping_to_which_surface_atom,system,full_neighbourlist)

			# Create the new atom and place it in the nanoparticle system. 
			atom = Atom(symbol='Br',position=cap_position,tag=counter)		
			system.append(atom)

			for bromine_index in atoms_to_not_add_new_atoms_to:
				#print('CAPPING')
				#print('##########')
				for index in range(len(triangles)-1,-1,-1):
					if bromine_index in triangles[index]:
						#print('Removing '+str(triangles[index]))
						del triangles[index]
				#print('##########')
				for index in range(len(squares)-1,-1,-1):
					if bromine_index in squares[index]:
						#print('Removing '+str(squares[index]))
						del squares[index]
				#print('##########')
				for index in range(len(nearly_squares)-1,-1,-1):
					if bromine_index in nearly_squares[index]:
						#print('Removing '+str(nearly_squares[index]))
						del nearly_squares[index]

				#print('##########')
				for index in range(len(tri_pos_new_atoms_indices)-1,-1,-1):
					if bromine_index in tri_pos_new_atoms_indices[index]:
						#print('Removing '+str(tri_pos_new_atoms[index]))
						#print('Removing '+str(tri_pos_new_atoms_indices[index]))
						del tri_pos_new_atoms[index]
						del tri_pos_new_atoms_indices[index]
				#print('##########')
				for index in range(len(squ_pos_new_atoms_indices)-1,-1,-1):
					if bromine_index in squ_pos_new_atoms_indices[index]:
						#print('Removing '+str(squ_pos_new_atoms[index]))
						#print('Removing '+str(squ_pos_new_atoms_indices[index]))
						del squ_pos_new_atoms[index]
						del squ_pos_new_atoms_indices[index]
				#print('##########')
				for index in range(len(nearly_squ_pos_new_atoms_indices)-1,-1,-1):
					if bromine_index in nearly_squ_pos_new_atoms_indices[index]:
						#print('Removing '+str(nearly_squ_pos_new_atoms[index]))
						#print('Removing '+str(nearly_squ_pos_new_atoms_indices[index]))
						del nearly_squ_pos_new_atoms[index]
						del nearly_squ_pos_new_atoms_indices[index]
				#print('##########')
				if bromine_index in surface_neighbourlist_excluding_capping.keys():
					surface_neighbourlist_excluding_capping.remove(bromine_index)

		# Write data to the trajectory file. 
		#print('Adding image to Traj')
		with Trajectory(traj_path,'a') as traj_file:
			traj_file.write(system.copy())

	print('----------------------------------')
	print('Adding atom '+str(counter))
	print('squares: '+str(len(squ_pos_new_atoms)))
	print('triangles: '+str(len(tri_pos_new_atoms)))
	print('----------------------------------')
	print('The simulation has now finished')
	print('----------------------------------')
	rest_of_atoms_to_cap = list(set(surface_neighbourlist.keys()) ^ set(atoms_to_not_add_new_atoms_to))

	shuffle(rest_of_atoms_to_cap)
	for index in rest_of_atoms_to_cap:

		cap_position = determine_where_to_place_capping_Br(index,system,full_neighbourlist)

		# Create the new atom and place it in the nanoparticle system. 
		atom = Atom(symbol='Br',position=cap_position,tag=counter)		
		system.append(atom)


		with Trajectory(traj_path,'a') as traj_file:
			traj_file.write(system.copy())

	return traj_path



