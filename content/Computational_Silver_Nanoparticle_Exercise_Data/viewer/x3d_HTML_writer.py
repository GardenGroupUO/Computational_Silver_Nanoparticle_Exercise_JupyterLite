import os, math
from ase.data import covalent_radii
from ase.data.colors import jmol_colors
import numpy as np

def write_x3d_html(atoms, output, notebook_name=None, colours={}, transparencies={}, show_unit_cell=False):
    x3d_obj = X3D(atoms, notebook_name=notebook_name, colours=colours, transparencies=transparencies, show_unit_cell=show_unit_cell)
    x3d_obj.write(output)

def get_unit_vector(vector):
    unit_vector = vector / np.linalg.norm(vector)
    return unit_vector

class X3D:
    """Class to write either X3D (readable by open-source rendering
    programs such as Blender) or X3DOM html, readable by modern web
    browsers.
    """

    def __init__(self, atoms, notebook_name=None, colours={}, transparencies={}, show_unit_cell=False):
        self._atoms = atoms
        self._notebook_name = notebook_name
        self._colours = colours
        self._transparencies = transparencies
        self._show_unit_cell = show_unit_cell

    def write(self, fileobj):
        viewer_construct_filename = os.path.realpath(__file__).replace('/x3d_HTML_writer.py','')+'/'+'viewer_construct.html'
        with open(viewer_construct_filename,'r') as viewer_construct:
            for line in viewer_construct:
                if '################### Atoms Go In Here ###################' in line:
                    elements = {}
                    print('<!-- ------------------------------- -->', file=fileobj)
                    print('<!-- Adding atoms here -->', file=fileobj)
                    print('<!-- ------------------------------- -->', file=fileobj)
                    for atom in self._atoms:
                        for indent, line in self.atom_lines(atom, elements,self._colours,self._transparencies):
                            print('    '*(3+indent)+line, file=fileobj)
                    print('<!-- ------------------------------- -->', file=fileobj)
                elif '################# Unit Cell Go In Here #################' in line:
                    if self._show_unit_cell:
                        print('<!-- ------------------------------- -->', file=fileobj)
                        print('<!-- Adding unit cell here -->', file=fileobj)
                        print('<!-- ------------------------------- -->', file=fileobj)
                        lines = self.get_unit_cell(self._atoms)
                        for indent, line in lines:
                            print('    '*(2+indent)+line, file=fileobj)
                        print('<!-- ------------------------------- -->', file=fileobj)
                elif '################### Viewpoint Go In Here ###################' in line:
                    (x_centre, y_centre, z_centre), height_above_molecule = self.get_camera_position(self._atoms,fieldOfView=0.5)
                    centreofrotation = str(x_centre)+' '+str(y_centre)+' '+str(z_centre)
                    line = '<Viewpoint id="front_1"  position="%.5f %.5f %.5f"'%(x_centre, y_centre, z_centre+height_above_molecule)+' orientation="0.0 0.0 1.0 0.0" centerOfRotation="'+centreofrotation+'" centerOfRotation_original="'+centreofrotation+'" clicked_last="true" description="camera"></Viewpoint>' 
                    print('    '*2+line, file=fileobj)
                    line = '<Viewpoint id="front_2"  position="%.5f %.5f %.5f"'%(x_centre, y_centre, z_centre+height_above_molecule)+' orientation="0.0 0.0 1.0 0.0" centerOfRotation="'+centreofrotation+'" description="camera"></Viewpoint>' 
                    print('    '*2+line, file=fileobj)
                    line = '<Viewpoint id="x_view_1" position="%.5f %.5f %.5f"'%(x_centre+height_above_molecule, y_centre, z_centre)+' orientation="0.0 1.0 0.0 1.57079632679" centerOfRotation="'+centreofrotation+'" centerOfRotation_original="'+centreofrotation+'" clicked_last="false" description="camera"></Viewpoint>'
                    print('    '*2+line, file=fileobj)
                    line = '<Viewpoint id="x_view_2" position="%.5f %.5f %.5f"'%(x_centre+height_above_molecule, y_centre, z_centre)+' orientation="0.0 1.0 0.0 1.57079632679" centerOfRotation="'+centreofrotation+'" description="camera"></Viewpoint>'
                    print('    '*2+line, file=fileobj)
                    line = '<Viewpoint id="y_view_1" position="%.5f %.5f %.5f"'%(x_centre, y_centre+height_above_molecule, z_centre)+' orientation="-1.0 0.0 0.0 1.57079632679" centerOfRotation="'+centreofrotation+'" centerOfRotation_original="'+centreofrotation+'" clicked_last="false" description="camera"></Viewpoint>' 
                    print('    '*2+line, file=fileobj)
                    line = '<Viewpoint id="y_view_2" position="%.5f %.5f %.5f"'%(x_centre, y_centre+height_above_molecule, z_centre)+' orientation="-1.0 0.0 0.0 1.57079632679" centerOfRotation="'+centreofrotation+'" description="camera"></Viewpoint>' 
                    print('    '*2+line, file=fileobj)
                elif '################### Group Go In Here ###################' in line:
                    line = '<Group id="Chemical_Group" onclick="handleGroupClick(event)" no_of_atoms='+str(len(self._atoms))+'>'
                    print('    '*2+line, file=fileobj)
                elif '################### Screenshot Name Go In Here ###################' in line:
                    if self._notebook_name == None:
                        line = 'newScreenshotDownloadLink.download = "screenshot.png";'
                    else:
                        line = 'newScreenshotDownloadLink.download = "Image_from_'+str(self._notebook_name)+'.png";'
                    print('    '*3+line, file=fileobj)
                elif '################### Transparancy Button Go In Here ###################' in line:
                    if not self._transparencies == {}:
                        line = '<br><br>\n'
                        line += '<button style="font-family: Arial, Helvetica;" onclick="turn_on_off_transparancy();">Turn On/Off Transparancy</button>'
                        print('    '*1+line, file=fileobj)
                elif '################### Unit Cell Button Go In Here ###################' in line:
                    if self._show_unit_cell:
                        line = '<br><br>\n'
                        line += '<button style="font-family: Arial, Helvetica;" onclick="turn_on_off_unit_cell();">Turn On/Off Unit Cell</button>'
                        print('    '*1+line, file=fileobj)
                else:
                    print(line.rstrip(), file=fileobj)
                
    def atom_lines(self,atom,elements,colours={},transparencies={}):
        """Generates a segment of X3D lines representing an atom."""
        x, y, z = atom.position
        symbol = atom.symbol
        no_of_elements_currently = elements.get(symbol, 0) + 1
        elements[symbol] = no_of_elements_currently
        atom_id = symbol+str(no_of_elements_currently)
        lines = [(0, '<Transform id="transform_'+str(atom.index)+'" translation="%.2f %.2f %.2f">' % (x, y, z))]
        lines += [(1, '<Shape DEF="'+str(atom.index)+'">')]
        lines += [(2, '<Appearance DEF="'+str(atom.index)+'">')]
        colour = colours.get(atom.index,jmol_colors[atom.number])
        color_string = 'diffuseColor="%.3f %.3f %.3f"' % tuple(colour)
        colour_original = 'originalColor="%.3f %.3f %.3f"' % tuple(colour)
        transparency = 'transparency='+str(transparencies.get(atom.index,0.0))
        transparency_original = 'transparency_original='+str(transparencies.get(atom.index,0.0))
        lines += [(3, '<Material id="'+str(atom.index)+'" name="'+str(atom_id)+'"'+color_string+' '+colour_original+' '+transparency+' '+transparency_original+' specularColor="0.5 0.5 0.5"></Material>')]
        lines += [(2, '</Appearance>')]
        lines += [(2, '<Sphere DEF="'+str(atom.index)+'" radius="%.2f"> </Sphere>' % covalent_radii[atom.number])] # onclick="changeColor();"
        lines += [(1, '</Shape>')]
        lines += [(0, '</Transform>')]
        return lines

    def get_unit_cell(self,atoms):
        cell = atoms.get_cell()
        scaled_unit_cell_lines = []
        scaled_unit_cell_lines.append(((0,0,0),(1,0,0))) # Origin to x
        scaled_unit_cell_lines.append(((0,0,0),(0,1,0))) # Origin to y
        scaled_unit_cell_lines.append(((0,0,0),(0,0,1))) # Origin to z

        scaled_unit_cell_lines.append(((1,0,0),(1,1,0))) # x to xy
        scaled_unit_cell_lines.append(((1,0,0),(1,0,1))) # x to xz

        scaled_unit_cell_lines.append(((0,1,0),(1,1,0))) # y to xy
        scaled_unit_cell_lines.append(((0,1,0),(0,1,1))) # x to yz

        scaled_unit_cell_lines.append(((0,0,1),(1,0,1))) # z to xz
        scaled_unit_cell_lines.append(((0,0,1),(0,1,1))) # z to yz

        scaled_unit_cell_lines.append(((1,1,0),(1,1,1))) # xy to xyz
        scaled_unit_cell_lines.append(((1,0,1),(1,1,1))) # xz to xyz
        scaled_unit_cell_lines.append(((0,1,1),(1,1,1))) # yz to xyz

        unit_cell_lines = []
        for start_pos, end_pos in scaled_unit_cell_lines:
            start_pos = cell.cartesian_positions(start_pos)
            end_pos   = cell.cartesian_positions(end_pos)
            unit_cell_lines.append((start_pos,end_pos))

        lines = []
        lines += [(0,'<Switch whichChoice="0" id="switcher">')]
        lines += [(0,'<Group id="Unit_Cell">')]
        for index in range(len(unit_cell_lines)):
            start_pos, end_pos = unit_cell_lines[index]
            direct_from_start_to_end = end_pos - start_pos
            vector_direction = get_unit_vector(direct_from_start_to_end)
            initial_vector_pointing = np.array((0,1,0))
            to_rotate_about = np.cross(initial_vector_pointing,vector_direction)
            angle_to_rotate_by = np.arccos(np.dot(initial_vector_pointing,vector_direction))

            translation_details = ','.join([str(x) for x in ((end_pos + start_pos)/2.0)])
            rotation_details = ','.join([str(x) for x in get_unit_vector(to_rotate_about)])+','+str(angle_to_rotate_by)
            line_length = np.linalg.norm(direct_from_start_to_end)
            #print('trans: '+str(translation_details)+'     rot: '+str(rotation_details)+'   len: '+str(line_length))

            lines += [(0,'<Transform translation="'+translation_details+'" rotation="'+rotation_details+'">')]
            lines += [(1,'<Shape>')]
            lines += [(2,'<Appearance>')]
            lines += [(3,'<Material diffuseColor="#000000"></Material>' )] # id="unit_cell_'+str(index)+'" # transparency=0.0
            lines += [(2,'</Appearance>')]
            lines += [(2,'<Cylinder DEF="cylinder" radius="0.05" height="'+str(line_length)+'"></Cylinder>')]
            lines += [(1,'</Shape>')]
            lines += [(0,'</Transform>')]
            #import pdb; pdb.set_trace()
        lines += [(0,'</Group>')]
        lines += [(0,'</Switch>')]
        #import pdb; pdb.set_trace()
        return lines

    def get_camera_position(self,atoms,fieldOfView=0.925025):
        x_points_of_view = []
        y_points_of_view = []
        z_points_of_view = []
        for atom in atoms:
            x_pos, y_pos, z_pos = atom.position
            atom_radius = covalent_radii[atom.number]
            x_points_of_view += [x_pos-atom_radius,x_pos+atom_radius]
            y_points_of_view += [y_pos-atom_radius,y_pos+atom_radius]
            z_points_of_view += [z_pos-atom_radius,z_pos+atom_radius]
        x_most_left = min(x_points_of_view)
        x_most_right = max(x_points_of_view)
        y_most_up = min(y_points_of_view)
        y_most_down = max(y_points_of_view)
        z_most_in = min(z_points_of_view)
        z_most_out = max(z_points_of_view)

        x_centre = (x_most_right+x_most_left)/2.0
        y_centre = (y_most_up+y_most_down)/2.0
        z_centre = (z_most_in+z_most_out)/2.0

        # fieldOfView=0.925025 radians, which is 53 degrees, based on normal field of view (https://en.wikipedia.org/wiki/Normal_lens) -->
        # but you can change this if you want
        # This has also been specifed in viewer_constract.html in Viewpoint
        radius=x_most_right-x_centre
        height_above_molecule = radius/math.tan(fieldOfView/2.0) 

        centre_position = (x_centre, y_centre, z_centre)
        return centre_position, height_above_molecule