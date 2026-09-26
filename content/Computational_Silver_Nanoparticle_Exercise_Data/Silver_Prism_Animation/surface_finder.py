import numpy as np
from ase.visualize import view

class doubledict:
	def __init__(self):
		self.dictionary = {}
	def __setitem__(self,key,value):
		index1 = key[0]; index2 = key[1]
		if index1 < index2:
			self.dictionary[(index1,index2)] = value
		else:
			self.dictionary[(index2,index1)] = value
	def __getitem__(self,key):
		return self.dictionary[key]
	def copy(self):
		new_doubledict = doubledict()
		new_doubledict.dictionary = self.dictionary.copy()
		return new_doubledict

class neighbourlist:
	def __init__(self):
		self.dictionary = {}
		#self.surface_atoms = {}

	def __len__(self):
		return len(self.dictionary)
	def set(self,index1,index2):
		self.dictionary.setdefault(index1,[]).append(index2)
		self.dictionary.setdefault(index2,[]).append(index1)
	def keys(self):
		return self.dictionary.keys()
	def __setitem__(self,index1,index2):
		self.set(index1,index2)
	def get(self,key):
		return self.dictionary[key]
	def __getitem__(self,key):
		return self.get(key)
	def items(self):
		return [(k,v) for k,v in self.dictionary.items()]
	def keys(self):
		return self.dictionary.keys()
	def copy(self):
		new_neighbourlist = neighbourlist()
		new_neighbourlist.dictionary = self.dictionary.copy()
		return new_neighbourlist
	def remove(self,index):
		for index2 in self.dictionary[index]:
			self.dictionary[index2].remove(index)
		del self.dictionary[index]
	'''
	def set_is_surface(self,index):
		if not len(full_neighbourlist.get(index)) == 12:
			self.surface_atoms[index] = True
		else:
			self.surface_atoms[index] = False
	'''

def get_unit_vector(non_normalised_vector):
	return non_normalised_vector/np.linalg.norm(non_normalised_vector)

def get_distance(positions_1,positions_2):
	diff = positions_1-positions_2
	#import pdb; pdb.set_trace()
	distance = (np.dot(diff,diff)) ** 0.5
	return distance

def get_surface_atoms(cluster,distances_between_atoms,full_neighbourlist,cutoff=3.0,last_index=False):

	surface_atoms = []
	for index in range(len(cluster)):
		if not len(full_neighbourlist.get(index)) == 12:
			#cluster[index].tag = 1
			surface_atoms.append(index)
		else:
			pass
			#cluster[index].tag = 0

	surface_neighbourlist = neighbourlist()
	for i1 in range(len(surface_atoms)):
		index1 = surface_atoms[i1]
		for i2 in range(i1+1,len(surface_atoms)):
			index2 = surface_atoms[i2]
			distance = distances_between_atoms[(index1,index2)]
			if distance <= cutoff:
				surface_neighbourlist.set(index1,index2)

	return surface_neighbourlist
