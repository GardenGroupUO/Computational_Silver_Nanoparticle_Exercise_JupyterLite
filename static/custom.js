// Add a Colab-style "Run" button to every code cell's prompt gutter ([ ]:),
// always visible regardless of window width, and swap it for a colourful
// spinner while that cell is executing. See custom.css for why this lives
// here instead of in JupyterLab's built-in (and width-sensitive) per-cell
// toolbar.
//
// There's no extension API for this in a static JupyterLite build, so it
// works directly against the DOM. JupyterLab rewrites a prompt's entire
// content on every state change ("[ ]:" -> "[*]:" -> "[1]:"), which wipes
// out anything we've inserted into it -- so rather than attaching once and
// tracking that with a marker attribute (which goes stale the moment
// JupyterLab wipes the element but leaves the attribute), `sync()` re-checks
// and re-inserts the right element on every mutation, keyed off the prompt's
// own current text. Each click resolves its own cell's *current* index at
// click time -- never a cached one -- via `window.jupyterapp`, which
// JupyterLite exposes globally because jupyter-lite.json sets
// "exposeAppInBrowser": true.
(function () {
  const RUN_ICON =
    '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">' +
    '<path fill="currentColor" d="M8 5v14l11-7z"/></svg>';

  const CHECK_ICON =
    '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">' +
    '<path fill="currentColor" d="M9 16.17 4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>';

  function findNotebookPanel(cellNode) {
    const app = window.jupyterapp;
    if (!app) return null;
    const current = app.shell.currentWidget;
    if (current && current.content && Array.isArray(current.content.widgets)) {
      if (current.content.widgets.some((w) => w.node === cellNode || w.node.contains(cellNode))) {
        return current;
      }
    }
    // fall back to scanning every open document if the click didn't happen
    // in the front-most tab
    const iter = app.shell.widgets ? app.shell.widgets('main') : [];
    for (const w of iter) {
      if (w.content && Array.isArray(w.content.widgets)) {
        if (w.content.widgets.some((cw) => cw.node === cellNode || cw.node.contains(cellNode))) {
          return w;
        }
      }
    }
    return null;
  }

  function runCell(promptNode) {
    const cellNode = promptNode.closest('.jp-Cell');
    if (!cellNode) return;
    const panel = findNotebookPanel(cellNode);
    if (!panel) return;
    const index = panel.content.widgets.findIndex((w) => w.node === cellNode);
    if (index === -1) return;
    panel.content.activeCellIndex = index;
    window.jupyterapp.commands.execute('notebook:run-cell-and-select-next');
  }

  function makeButton(prompt) {
    const btn = document.createElement('button');
    btn.className = 'ir-run-button';
    btn.type = 'button';
    btn.title = 'Run this cell';
    btn.setAttribute('aria-label', 'Run this cell');
    btn.innerHTML = RUN_ICON;
    btn.addEventListener('click', (evt) => {
      evt.preventDefault();
      evt.stopPropagation();
      runCell(prompt);
    });
    return btn;
  }

  function makeCheck(prompt) {
    const btn = document.createElement('button');
    btn.className = 'ir-run-button ir-run-done';
    btn.type = 'button';
    btn.title = 'Prerequisite files loaded (click to run again)';
    btn.setAttribute('aria-label', 'Prerequisite files loaded, click to run again');
    btn.innerHTML = CHECK_ICON;
    btn.addEventListener('click', (evt) => {
      evt.preventDefault();
      evt.stopPropagation();
      runCell(prompt);
    });
    return btn;
  }

  function makeSpinner() {
    const span = document.createElement('span');
    span.className = 'ir-spinner';
    span.title = 'Running…';
    span.setAttribute('aria-label', 'Running');
    return span;
  }

  // The prompt's own text is always exactly "[ ]:", "[*]:", or "[N]:" for a
  // code cell -- "*" only ever appears there while the kernel is busy on it.
  function isBusy(prompt) {
    return (prompt.textContent || '').indexOf('*') !== -1;
  }

  // "[N]:" (N >= 1) means this cell has completed at least one run.
  function hasRun(prompt) {
    return /\[\d+\]/.test(prompt.textContent || '');
  }

  // Every notebook's very first code cell -- the one students are told to
  // "click the button below to load our prerequisite files" -- is exactly
  // "%pip install ...". Once that specific cell has run, show a checkmark
  // instead of the play icon so it's obvious the prerequisite step is done,
  // without affecting any other cell's button.
  function isPrereqCell(prompt) {
    const cellNode = prompt.closest('.jp-Cell');
    const code = cellNode ? cellNode.querySelector('.cm-content') : null;
    return !!code && (code.textContent || '').includes('%pip install');
  }

  function sync(prompt) {
    const busy = isBusy(prompt);
    const btn = prompt.querySelector('.ir-run-button');
    const spinner = prompt.querySelector('.ir-spinner');
    const done = !busy && hasRun(prompt) && isPrereqCell(prompt);

    if (busy) {
      if (btn) btn.remove();
      if (!spinner) prompt.prepend(makeSpinner());
      return;
    }
    if (spinner) spinner.remove();
    if (btn && btn.classList.contains('ir-run-done') !== done) btn.remove();
    if (!prompt.querySelector('.ir-run-button')) {
      prompt.prepend(done ? makeCheck(prompt) : makeButton(prompt));
    }
  }

  function syncAll() {
    document.querySelectorAll('.jp-CodeCell .jp-InputArea-prompt').forEach(sync);
  }

  syncAll();
  new MutationObserver(syncAll).observe(document.body, {
    childList: true,
    subtree: true,
    characterData: true,
  });
})();
