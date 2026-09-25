# JupyterLite port of the Computational Silver Nanoparticle Exercise

## Goal

Build a fully browser-based version (JupyterLite, Pyodide kernel, no Google account) of the Colab
notebooks in `GardenGroupUO/Computational_Silver_Nanoparticle_Exercise`. This lives in a **new
repository**. The original Colab repos are the work of a former student and must not be modified
as part of this project. The README of the new repo should credit the original repos and authors.

Source repos (read-only references):

- Notebooks: https://github.com/GardenGroupUO/Computational_Silver_Nanoparticle_Exercise
- Helper code and data: https://github.com/GardenGroupUO/Computational_Silver_Nanoparticle_Exercise_Data
- Genetic algorithm (Part 4.1): https://github.com/GardenGroupUO/Organisms

## Working agreement

The user reviews and suggests edits locally before anything is pushed. Make changes in small,
reviewable steps, explain what changed, and do not push without being asked. Serve the site locally
so the user can check each notebook in a real browser; rendering of the 3D viewers in particular
has not been verified yet.

## What has already been tested (Pyodide 0.27.7 under Node.js, Python 3.12, NumPy 2.0.2)

- Parts 1–3 only need ASE. `ase==3.22.0` (pure-Python wheel) installs and runs unchanged.
  All helper functions give the same results as native Python, roughly 1.5–2.5x slower.
- ASAP (`asap3`) is only used in Part 4.1, for the Gupta potential in
  `Set_of_RunMinimisation_Files/RunMinimisation_Ag.py`. It cannot run in the browser.
- Replacement: `gupta_numpy.py`, a pure-NumPy Gupta calculator. It matches ASAP to ~1e-15 eV in
  energies and forces and relaxes to identical structures. Use it via `RunMinimisation_Ag_numpy.py`.
  ASE's built-in EMT was benchmarked as an alternative and is ~6x slower in the GA; do not use it.
- Organisms runs without ASAP once the two top-level `asap3` imports in
  `Organisms/GA/SCM_Scripts/{T,A}_SCM_Methods.py` are made lazy (`organisms_lazy_asap3.patch`).
  The notebook's settings (energy predation, energy fitness) never use CNA/SCM. Must set
  `no_of_cpus = 1` (no multiprocessing in the browser; Organisms has a serial branch).
  A 5-generation GA ran successfully in Pyodide (~89 s). Full 30 generations is estimated at
  ~7 min in a browser; consider reducing generations (to be decided with the user).
- Growth models from the `mid1` seed (Parts 3.1, 3.2): originally 145 s natively.
  `data_repo_vectorise_same_position.patch` vectorises `same_position` → ~45 s native, ~80 s Pyodide.
  Apply with `git apply --ignore-whitespace` (source files have CRLF endings). Remaining hotspot:
  O(N²) neighbour search in `Silver_Prism_Animation/surface_finder.py`; replacing it with
  `scipy.spatial.cKDTree` or ASE `NeighborList` should help further (not yet done).
- Known existing bug, deliberately left unchanged so results match the original: in
  `update_positions_for_new_atoms`, `indices_to_remove` are deleted in ascending order, so later
  indices shift. Raise with the user before fixing.
- `input()` (used by `make_nanoparticle()` in Part 2.1) works in the user's other JupyterLite
  project; keep it.

## Files from the assessment (to be added to the new repo)

- `gupta_numpy.py`: NumPy Gupta ASE calculator
- `RunMinimisation_Ag_numpy.py`: drop-in minimiser using it
- `organisms_lazy_asap3.patch`: lazy asap3 imports (+ relaxed `install_requires` in setup.py)
- `data_repo_vectorise_same_position.patch`: vectorised `same_position`

For Organisms, prefer either proposing the lazy-import change upstream (harmless for normal users)
and installing with `micropip.install(..., deps=False)` to skip asap3, or vendoring a patched
pure-Python wheel into the site. Discuss with the user.

## Required changes to the notebooks and helper code

1. **Setup cells**: replace `!pip install` / `!git clone` with `%pip install ase==3.22.0` (plus
   Organisms/termcolor/tqdm for 4.1). Ship only the needed `_Data` files (~1 MB: the `.py` files,
   `viewer/viewer_construct.html`, `movie_viewer/viewer_construct.html`, the `*_initial_seed.xyz`
   files, `molecules/*.xyz`, `movie_viewer/js/dependencies/gifshot.min.js`). Do not ship `Images/`,
   the large `.traj`/`.xyz`/`.state` files, or `.git` (the repo is 118 MB, mostly those).
   Place the `Computational_Silver_Nanoparticle_Exercise_Data` package next to the notebooks; the
   helper code finds it via `os.listdir('.')`.
2. **Path checks**: the `/content/Computational_Silver_Nanoparticle_Exercise_Data` existence checks
   are Colab paths and must be updated or removed.
3. **x3d viewers** (`viewer/x3d_viewer.py`, `movie_viewer/x3d_movie_viewer.py`): each output is a
   full HTML page with fixed element IDs and global JS functions. Colab isolates outputs in iframes;
   JupyterLab does not, so multiple viewers per notebook (Parts 2.3, 3.1) would conflict. Wrap the
   output in an iframe:
   ```python
   import html
   return HTML('<iframe srcdoc="' + html.escape(data, quote=True) +
               '" style="width:100%;height:700px;border:0"></iframe>')
   ```
   The movie viewer loads gifshot etc. from relative `js/...` paths, which will not resolve in a
   srcdoc iframe; inline `gifshot.min.js` into the template to keep GIF export. Both viewers load
   x3dom and jQuery from CDNs (x3dom.org, code.jquery.com), so an internet connection is required.
   The viewers also write a debug `html_file.html` into the package folder; consider removing.
4. **Colab-only content**: drop Part 1.0 "own account" (Drive mounting) and Colab-specific
   instructions/images; JupyterLite saves work in the browser and notebooks can be downloaded.
   In Part 4.1 replace `google.colab.data_table` with plain `display(data)` (pandas is available).
5. **Part 4.1 GA working directory**: the GA writes many files and an SQLite database. Test whether
   this works on JupyterLite's persistent `/drive` filesystem; if it is slow or SQLite locking
   fails, run the GA in an in-memory directory such as `/tmp` and read results from there.
6. The GA wall-time limit (`total_length_of_running_time`) and generation count should be revisited
   for browser speeds.

## Suggested build order

1. Scaffold the JupyterLite site (`jupyterlite-core`, `jupyterlite-pyodide-kernel`), contents
   folder, and a GitHub Actions workflow deploying to GitHub Pages. Check which Pyodide version the
   chosen kernel release bundles (testing was done on 0.27.7).
2. Port Part 1.2 (first notebook with a viewer) end to end, including the iframe fix, to prove the
   pipeline.
3. Port Parts 2.1–3.2, applying the vectorisation patch before the growth-model notebooks.
4. Port Part 4.1 with patched Organisms, NumPy Gupta, `no_of_cpus = 1`; agree generation count.
5. Clean up Colab-only cells, inline gifshot, write README with credits.
