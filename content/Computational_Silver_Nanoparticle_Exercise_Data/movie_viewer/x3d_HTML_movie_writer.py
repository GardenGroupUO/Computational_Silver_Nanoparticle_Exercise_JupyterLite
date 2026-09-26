import os, math
from ase.data import covalent_radii
from ase.data.colors import jmol_colors
import numpy as np

def write_x3d_movie_html(images, output, notebook_name=None, colours=[]):
    x3d_obj = X3D_Movie(images, notebook_name=notebook_name, colours=colours)
    x3d_obj.write(output)

def get_unit_vector(vector):
    unit_vector = vector / np.linalg.norm(vector)
    return unit_vector

class X3D_Movie:
    """Class to write either X3D (readable by open-source rendering
    programs such as Blender) or X3DOM html, readable by modern web
    browsers.
    """

    def __init__(self, images, notebook_name=None, colours=[]):
        self._images = images
        self._notebook_name = notebook_name
        self._colours = colours

    def write(self, fileobj):
        viewer_construct_filename = os.path.realpath(__file__).replace('/x3d_HTML_movie_writer.py','')+'/'+'viewer_construct.html'
        with open(viewer_construct_filename,'r') as viewer_construct:
            for line in viewer_construct:
                if '################### Atoms Go In Here ###################' in line:
                    elements = {}
                    print('<!-- ------------------------------- -->', file=fileobj)
                    print('<!-- Adding atoms here -->', file=fileobj)
                    print('<!-- ------------------------------- -->', file=fileobj)
                    for indent, line in self.images_lines(self._images, elements,self._colours):
                        print('    '*(3+indent)+line, file=fileobj)
                    print('<!-- ------------------------------- -->', file=fileobj)
                elif '################### Viewpoint Go In Here ###################' in line:
                    (x_centre, y_centre, z_centre), height_above_molecule = self.get_camera_position(self._images,fieldOfView=0.5)
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
                    # line = '<Group id="Chemical_Group" onclick="handleGroupClick(event)" last_image=1721 no_of_atoms='+str(len(self._images[-1]))+'>'
                    # frame_atom_counts records the actual cumulative atom count at each
                    # frame, so the viewer can show/hide the right atoms even when frames
                    # don't each add exactly one atom (e.g. a downsampled trajectory).
                    frame_atom_counts = ','.join(str(len(image)) for image in self._images)
                    line = '<Group id="Chemical_Group" onclick="handleGroupClick(event)" run_animation="False" no_of_atoms_of_0_image='+str(len(self._images[0]))+' current_image_no=0 final_image_no='+str(len(self._images)-1)+' frame_atom_counts="'+frame_atom_counts+'">'
                    print('    '*2+line, file=fileobj)
                    #line = '<Switch whichChoice="0" id="switcher">'
                    #print('    '*2+line, file=fileobj)
                elif '################### Screenshot Name Go In Here ###################' in line:
                    if self._notebook_name == None:
                        line = 'newScreenshotDownloadLink.download = "screenshot.png";'
                    else:
                        line = 'newScreenshotDownloadLink.download = "Image_from_'+str(self._notebook_name)+'.png";'
                    print('    '*3+line, file=fileobj)
                elif '################### Video Button Go In Here ###################' in line:
                    #line = '<div style="margin-left: 550px">'
                    #print('    '*2+line, file=fileobj)
                    #line = '    <b>Visible node</b><br>'
                    #print('    '*2+line, file=fileobj)
                    start = 0; end = len(self._images)-1
                    line = '    '+str(start)+' <input type="range" id="video_slider" min="'+str(start)+'" max="'+str(end)+'" step="1" value="0" oninput="pause_slider_before_click();" onchange="move_slider_manually(this.value)"></input>'+str(end)+''
                    print('    '*2+line, file=fileobj)
                    line = '    <br><br>'
                    print('    '*2+line, file=fileobj)
                    line = '    <span id="visNode" style="color:#00CC00">Showing initial image</span>'
                    print('    '*2+line, file=fileobj)
                    #line = '</div>'
                    #print('    '*2+line, file=fileobj)
                elif '################### External JS scripts Go In Here ###################' in line:
                    js_files = ['js/dependencies/'+jsfile for jsfile in ['gifshot.min.js']]#,'prism.min.js','esprima.min.js','escodegen.min.js','lodash.min.js','classList.js']]
                    for indent, line in self.add_external_JS_scripts(js_files):
                        print('    '*(indent)+line, file=fileobj)
                else:
                    print(line.rstrip(), file=fileobj)

    def images_lines(self,images,elements,all_colours=[]):
        initial_atom_size = len(images[0])
        lines = []
        for atom in images[0]:
            for indent, line in self.atom_lines(atom, elements,initial_transparancy=0.0): #,all_colours):
                lines.append((indent, line))
        # Each frame can add more than one atom (e.g. a downsampled trajectory
        # where frames are several growth steps apart), so emit every atom
        # that's new since the previous frame, not just one.
        previous_atom_count = initial_atom_size
        for index in range(1,len(images)):
            system = images[index]
            current_atom_count = len(system)
            for new_atom_index in range(previous_atom_count,current_atom_count):
                atom = system[new_atom_index]
                for indent, line in self.atom_lines(atom, elements,initial_transparancy=1.0): #,all_colours):
                    lines.append((indent, line))
            previous_atom_count = current_atom_count
        return lines

    def atom_lines(self,atom,elements,colours={},initial_transparancy=1.0):
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
        transparency = 'transparency='+str(initial_transparancy)
        lines += [(3, '<Material id="'+str(atom.index)+'" name="'+str(atom_id)+'" '+color_string+' '+colour_original+' '+transparency+' specularColor="0.5 0.5 0.5"></Material>')]
        lines += [(2, '</Appearance>')]
        lines += [(2, '<Sphere DEF="'+str(atom.index)+'" radius="%.2f"> </Sphere>' % covalent_radii[atom.number])] # onclick="changeColor();"
        lines += [(1, '</Shape>')]
        lines += [(0, '</Transform>')]
        return lines

    def get_camera_position(self,images,fieldOfView=0.925025):
        x_points_of_view = []
        y_points_of_view = []
        z_points_of_view = []
        for atom in images[-1]:
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

    def add_external_JS_scripts(self,js_files):
        lines = []
        for js_file in js_files:
            lines.append((0,'<!-- Script from '+str(js_files)+'-->'))
            lines.append((0,'<script>'))
            google_path = 'Computational_Silver_Nanoparticle_Exercise_Data/movie_viewer/'+js_file
            if os.path.exists(js_file):
                path_to_js = js_file
            elif os.path.exists(google_path):
                path_to_js = google_path
            else:
                exit('Error, can not file js file')
            with open(path_to_js,'r') as js_FILE:
                for js_line in js_FILE:
                    #indentation = len(js_line) - len(js_line.lstrip())
                    #import pdb; pdb.set_trace()
                    lines.append((0,js_line.lstrip().rstrip()))
            lines.append((0,'</script>'))
            lines.append((0,'<!-- Script from '+str(js_files)+'-->'))
            lines.append((0,''))
        return lines