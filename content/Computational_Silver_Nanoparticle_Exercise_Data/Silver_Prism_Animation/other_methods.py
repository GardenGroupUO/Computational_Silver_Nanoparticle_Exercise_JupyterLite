import numpy as np

def get_unit_vector(vector):
	unit_vector = vector/np.linalg.norm(vector)
	return unit_vector

def determine_where_to_place_capping_Br(add_capping_to_which_surface_atom,system,full_neighbourlist):

	fn_neighbours = full_neighbourlist[add_capping_to_which_surface_atom]
	sn_neighbours = [full_neighbourlist[snn_index] for snn_index in fn_neighbours]
	sn_neighbours = [j for sub in sn_neighbours for j in sub]
	all_close_neighbours = set(fn_neighbours + sn_neighbours)
	if add_capping_to_which_surface_atom in all_close_neighbours:
		all_close_neighbours.remove(add_capping_to_which_surface_atom)

	binding_atom_position = system[add_capping_to_which_surface_atom].position

	all_close_neighbours_positions = [system[index].position for index in all_close_neighbours]

	vectors_from_bonding_atom = [(binding_atom_position - all_close_neighbours_position) for all_close_neighbours_position in all_close_neighbours_positions]
	unit_vectors_from_bonding_atom = [get_unit_vector(vector_from_bonding_atom) for vector_from_bonding_atom in vectors_from_bonding_atom]
	distances_of_vectors_from_bonding_atom = [np.linalg.norm(vector_from_bonding_atom) for vector_from_bonding_atom in vectors_from_bonding_atom]
	total_distances = sum(distances_of_vectors_from_bonding_atom)
	normalised_distances_vectors_from_bonding_atom = [(distance_of_vector_from_bonding_atom/total_distances) for distance_of_vector_from_bonding_atom in distances_of_vectors_from_bonding_atom]

	vector_to_point_in = sum([(1/(normalised_distance**2.0))*unit_vector for normalised_distance, unit_vector in zip(normalised_distances_vectors_from_bonding_atom,unit_vectors_from_bonding_atom)])
	unit_vector_to_point_in = get_unit_vector(vector_to_point_in)

	cap_position = binding_atom_position + unit_vector_to_point_in*2.5

	return cap_position