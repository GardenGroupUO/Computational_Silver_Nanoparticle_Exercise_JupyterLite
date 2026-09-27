"""Link static/custom.css and static/custom.js into the built site, and make
sure exposeAppInBrowser survives the build.

Usage: python tools/inject_custom_assets.py _output

Neither is possible through JupyterLite's settings system: there's no
supported way to recolour an icon (the one "theme CSS override" setting only
covers fonts) or to add a button outside a cell, so both are copied into the
built app and linked from index.html directly. Run after `jupyter lite build`.

Ported from the spc-jupyterlite project (static/custom.css there has the full
history/reasoning). Adapted APPS for this project's primary interface: we
serve the Notebook-7-style UI (`notebooks`/`tree`), not full JupyterLab, so
those are the app builds that need the injected assets; `lab` is included too
since it's still built and available as a fallback.

`custom.js` finds the active notebook via `window.jupyterapp`, which only
exists because the project's own `jupyter-lite.json` sets
"exposeAppInBrowser": true. A from-scratch `jupyter lite build` (every CI run;
locally, only after clearing `_output` and `.jupyterlite.doit.db`) drops that
key somewhere in jupyterlite-core's config-merge step -- confirmed missing
from the built jupyter-lite.json even though the merge log claims to have
read the project's file. Cheaper to re-add it after the fact here than to
chase the merge bug upstream; every one of custom.js's features (the run
button, hidden-code cells, the video auto-run) silently does nothing without
it, with no error to notice.
"""
import json
import shutil
import sys
from pathlib import Path

APPS = ["lab", "notebooks", "tree"]
ASSETS = ["custom.css", "custom.js"]
TAGS = {
    "custom.css": '<link rel="stylesheet" href="./custom.css">',
    "custom.js": '<script defer src="./custom.js"></script>',
}


def install_root_redirect(dist_dir, static_dir):
    """Replace the built site's root index.html (JupyterLite's own app
    launcher/chooser page) with a page that redirects straight to Part 1.1.

    Gives students and anyone we share the link with a short URL (just the
    site root) instead of the full notebooks/index.html?path=... form.

    static/index_redirect.html keeps a (invisible, functionally inert)
    <script id="jupyter-config-data"> tag alongside the redirect -- every
    other app page (notebooks/, lab/, tree/) fetches the site root's
    index.html at load time to inherit shared config, and crashes if that
    tag is missing. That was the real, previously-misdiagnosed cause of an
    "every notebook is blank" bug that briefly looked like it was about the
    redirect mechanism itself (windowingMode and cross-origin isolation were
    both investigated and ruled out too, along the way) -- it wasn't; a
    plain link and an auto-redirect fail identically without the tag, and
    both work fine with it.

    The launcher page this replaces is still reachable directly at
    notebooks/, lab/, and tree/ if ever needed.
    """
    target = dist_dir / "index.html"
    target.write_text((static_dir / "index_redirect.html").read_text())
    print(f"installed root redirect at {target}")


def ensure_expose_app_in_browser(dist_dir, apps):
    paths = [dist_dir / "jupyter-lite.json"] + [dist_dir / app / "jupyter-lite.json" for app in apps]
    for path in paths:
        if not path.is_file():
            continue
        config = json.loads(path.read_text())
        jcd = config.setdefault("jupyter-config-data", {})
        if jcd.get("exposeAppInBrowser") is not True:
            jcd["exposeAppInBrowser"] = True
            path.write_text(json.dumps(config))
            print(f"patched exposeAppInBrowser into {path}")


def main(dist_dir):
    dist_dir = Path(dist_dir)
    static_dir = Path(__file__).parent.parent / "static"

    ensure_expose_app_in_browser(dist_dir, APPS)
    install_root_redirect(dist_dir, static_dir)

    for app in APPS:
        app_dir = dist_dir / app
        if not app_dir.is_dir():
            print(f"skipping {app}: {app_dir} does not exist")
            continue

        index_html = app_dir / "index.html"
        html = index_html.read_text()
        changed = False

        for asset in ASSETS:
            shutil.copyfile(static_dir / asset, app_dir / asset)
            tag = TAGS[asset]
            if tag not in html:
                html = html.replace("</head>", f"  {tag}\n  </head>", 1)
                changed = True

        if changed:
            index_html.write_text(html)
        print(f"linked {', '.join(ASSETS)} into {index_html}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "_output")
