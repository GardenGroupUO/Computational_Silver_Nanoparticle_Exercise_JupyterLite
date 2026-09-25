# Kernel choice: Pyodide vs. xeus-python

Investigated switching the whole project from the `jupyterlite-pyodide-kernel` scaffold to
`jupyterlite-xeus` + xeus-python, prompted by wanting to drop the per-notebook `%pip install ase`
setup cells (xeus-python bundles packages into the environment at CI build time instead).

**Decision: stayed on Pyodide.** Component-speed benchmarks below show no meaningful difference
between the two kernels, and Pyodide is the one that already exactly matches the environment
(Python 3.12.7, NumPy 2.0.2) the rest of this project's numeric behaviour was validated against.
This is kept as a documented fallback in case that changes (e.g. Pyodide hits a hard blocker later).

## Benchmark results

Same code run three ways: native (this machine), Pyodide kernel (`jupyter-lite build`, confirmed
Python 3.12.7 / NumPy 2.0.2 — matches the tested environment exactly), and xeus-python (Python
3.13.1 / NumPy 2.5.3, via the `environment.yml` in `xeus-python-prototype/`). All three produced
identical step counts / pair counts, confirming numeric correctness, not just speed.

`gupta_numpy.py`-style relaxation (`benchmark_gupta.ipynb`, vectorised NumPy):

| atoms | native | Pyodide | xeus-python |
|---|---|---|---|
| 147 | 0.14s | 0.27s (1.9x) | 0.41s (2.9x) |
| 309 | 0.63s | 1.16s (1.9x) | 1.07s (1.7x) |
| 561 | 3.07s | 4.77s (1.6x) | 4.15s (1.4x) |

Pure-Python O(N²) nested loop (`benchmark_looploop.ipynb`, stand-in for the un-vectorised
neighbour search in `Silver_Prism_Animation/surface_finder.py`):

| n | native | Pyodide | xeus-python |
|---|---|---|---|
| 2000 | 0.27s | 0.53s (2.0x) | 0.49s (1.8x) |
| 4000 | 1.03s | 2.07s (2.0x) | 1.96s (1.9x) |
| 6000 | 2.37s | 4.67s (2.0x) | 4.50s (1.9x) |

xeus-python is ~4-7% faster on the pure-Python-loop case and roughly a wash (sometimes slower,
sometimes faster, no consistent direction) on vectorised NumPy. Not enough to justify the switch.

## What was confirmed about xeus-python along the way

- `jupyterlite-xeus`'s `environment.yml` supports a `pip:` section for pure-Python packages not on
  the `emscripten-forge-4x` wasm channel. `ase==3.22.0`, `termcolor`, `tqdm` all install this way;
  `numpy`, `scipy`, `pandas` come from `emscripten-forge-4x`/`conda-forge` directly. See
  `xeus-python-prototype/environment.yml` — this exact file was built successfully end to end
  (`jupyter lite build`, requires `micromamba` on `PATH`).
- Confirmed working at runtime in a real browser: `import ase`, `input()`, and the
  `HTML('<iframe srcdoc="...">')` trick from the main `CLAUDE.md` (used by the x3d viewers) —
  all needed to reproduce. `pandas`/`termcolor`/`tqdm` imports were *not* independently re-tested
  at runtime, only confirmed to package successfully (same pip mechanism as `ase`, which was
  runtime-tested).
- Organisms (Part 4.1) isn't on PyPI. `pip:` accepts `git+https://...` for pure-Python packages,
  so `git+https://github.com/GardenGroupUO/Organisms.git` (after the lazy-asap3 patch) should work
  the same way as `ase` — **untested**.
- The embedded/sandboxed browser pane used during this investigation cannot register Service
  Workers at all (confirmed with a trivial test script, unrelated to this project). xeus-python's
  kernel registration explicitly waits on the Service Worker
  ([jupyterlite/xeus#363](https://github.com/jupyterlite/xeus/pull/363)), so its kernel option
  doesn't appear there — this is a pane-specific limitation, not a build problem; it worked
  immediately in a real browser. The Pyodide kernel's launcher tile isn't blocked by this, but
  *cross-file* access (importing a sibling `.py` file into a notebook) also needs the Service
  Worker under both kernels — inline code in the benchmark notebooks to sidestep this while working
  in that pane.
- `jupyterlite-xeus` pulls in `jupyterlite-core>=0.7`, which conflicts with the `<0.7` pin the main
  scaffold uses for `jupyterlite-pyodide-kernel` (chosen to match Pyodide 0.27.6, close to the
  0.27.7 this project's numeric benchmarks were run against). The two kernels can't currently
  coexist in one build with these pins.

## If this needs revisiting

`xeus-python-prototype/environment.yml` is a known-working starting point. Re-run with
`jupyter lite build` from a venv with `jupyterlite-xeus` installed, and `micromamba` on `PATH`
(a standalone binary works fine, no system install needed:
`curl -Ls https://micro.mamba.pm/api/micromamba/<platform>/latest | tar -xvj bin/micromamba`).
Before switching for real: re-run this project's actual numeric validation (gupta_numpy vs. asap3
agreement, GA generation timing) under Python 3.13/NumPy 2.5.3, since those were only validated
under Python 3.12/NumPy 2.0.2 so far — this benchmark only checked raw speed, not full pipeline
correctness beyond the two microbenchmarks above.
