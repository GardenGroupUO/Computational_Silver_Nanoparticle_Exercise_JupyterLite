"""Link static/custom.css and static/custom.js into the built site.

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
"""
import shutil
import sys
from pathlib import Path

APPS = ["lab", "notebooks", "tree"]
ASSETS = ["custom.css", "custom.js"]
TAGS = {
    "custom.css": '<link rel="stylesheet" href="./custom.css">',
    "custom.js": '<script defer src="./custom.js"></script>',
}


def main(dist_dir):
    dist_dir = Path(dist_dir)
    static_dir = Path(__file__).parent.parent / "static"

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
