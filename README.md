# Computational Silver Nanoparticle Exercise — JupyterLite Edition

A fully browser-based version of the Garden Group's Computational Silver
Nanoparticle Exercise. Runs entirely client-side on
[JupyterLite](https://jupyterlite.readthedocs.io/) with a Pyodide kernel —
no Google account, no server, no install. Just open the site and go.

**[Start here → Part 1.1: Getting Started](https://gardengroupuo.github.io/Computational_Silver_Nanoparticle_Exercise_JupyterLite/notebooks/index.html?path=Part_1.1_Getting_Started.ipynb)**

## Credits

This is a port of the original Google Colab exercise, adapted to run without
Colab or a Google account. All exercise content, chemistry, and code are the
work of the original authors — this repository only changes *how* it runs.

- **Notebooks:** [GardenGroupUO/Computational_Silver_Nanoparticle_Exercise](https://github.com/GardenGroupUO/Computational_Silver_Nanoparticle_Exercise)
- **Helper code and data:** [GardenGroupUO/Computational_Silver_Nanoparticle_Exercise_Data](https://github.com/GardenGroupUO/Computational_Silver_Nanoparticle_Exercise_Data)
- **Genetic algorithm (Part 4.1):** [GardenGroupUO/Organisms](https://github.com/GardenGroupUO/Organisms), by Dr. Geoffrey R. Weal and Dr. Anna L. Garden

Both are from the [Garden Group](https://blogs.otago.ac.nz/annagarden/),
Department of Chemistry, University of Otago. The original notebooks and
exercise repositories are unmodified by this project and remain the
authoritative source.

## What's different here

- Runs on GitHub Pages via JupyterLite instead of Google Colab — no sign-in.
- `asap3` (native code, can't run in a browser) is replaced in Part 4.1 with
  a pure-NumPy Gupta potential calculator that matches it to ~1e-15 eV.
- The genetic algorithm package (`Organisms`) runs with its `asap3` imports
  made lazy, so it installs and runs without that dependency.
- A handful of Colab-only cells (Drive mounting, `google.colab.data_table`)
  are replaced with browser-native equivalents.
- Videos and 3D structure viewers are adapted to load automatically and to
  coexist on the same page (Colab isolates each output in its own iframe;
  JupyterLab does not, so this needed some extra care for notebooks with
  more than one viewer).

See `DEVELOPMENT_NOTES.md` for the full technical detail behind these changes.

## Running locally

```bash
pip install jupyterlite-core jupyterlite-pyodide-kernel
jupyter lite build --contents content --output-dir _output
python -m http.server 8000 --directory _output
```

Then open `http://localhost:8000` in a browser.

## Contents

- `content/` — the notebooks (`Part_1.1` through `Part_4.1`) and the
  `Computational_Silver_Nanoparticle_Exercise_Data` package they import from.
- `static/` — small site customisations (run buttons, hidden setup cells,
  auto-loading videos) injected into the built site.
- `tools/` — build helper scripts.
