import os
import html
import warnings

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from IPython.display import HTML

if 'Computational_Silver_Nanoparticle_Exercise_Data' in os.listdir('.'):
    from Computational_Silver_Nanoparticle_Exercise_Data.viewer.x3d_HTML_writer import write_x3d_html
else:
    try:
        from viewer.x3d_HTML_writer import write_x3d_html
    except Exception:
        from x3d_HTML_writer import write_x3d_html

def view_x3d(atoms,notebook_name=None,colours={},transparencies={},show_unit_cell=False):
    """View atoms inline in a jupyter notbook. This command
    should only be used within a jupyter/ipython notebook.

    Args:
        atoms - ase.Atoms, atoms to be rendered"""

    output = StringIO()
    write_x3d_html(atoms, output, notebook_name=notebook_name, colours=colours, transparencies=transparencies, show_unit_cell=show_unit_cell)
    data = output.getvalue()
    output.close()

    # Wrapped in an iframe so multiple viewers in one notebook don't clash
    # over the fixed element IDs / global JS functions in viewer_construct.html
    # (Colab isolated each output in its own iframe automatically; JupyterLab does not).
    # IPython nudges towards IFrame() for iframe content, but that class embeds a
    # src URL, not arbitrary HTML via srcdoc, so it doesn't fit here; suppress the nag.
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='Consider using IPython.display.IFrame instead')
        return HTML('<iframe srcdoc="' + html.escape(data, quote=True) +
                    '" style="width:100%;height:700px;border:0"></iframe>')