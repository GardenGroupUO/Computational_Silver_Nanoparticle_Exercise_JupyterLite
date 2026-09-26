import os
import html
import warnings

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from IPython.display import HTML

if 'Computational_Silver_Nanoparticle_Exercise_Data' in os.listdir('.'):
    from Computational_Silver_Nanoparticle_Exercise_Data.movie_viewer.x3d_HTML_movie_writer import write_x3d_movie_html
else:
    try:
        from movie_viewer.x3d_HTML_movie_writer import write_x3d_movie_html
    except Exception:
        from x3d_HTML_movie_writer import write_x3d_movie_html

def view_x3d_movie(images,notebook_name=None,colours=[]):
    """View images inline in a jupyter notbook. This command
    should only be used within a jupyter/ipython notebook.
    """

    output = StringIO()
    write_x3d_movie_html(images, output, notebook_name=notebook_name, colours=colours)
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
