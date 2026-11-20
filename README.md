# DXFExportUnits

Scales DXF export to a chosen unit and sets the DXF `$INSUNITS` header to match -- for
**every** DXF export in FreeCAD, not just a dedicated export command. Works against a
completely stock FreeCAD install; no custom build or forked source required.

## Why this exists

FreeCAD works in millimeters internally and always writes DXF files with
`$INSUNITS` claiming millimeters, regardless of what the geometry actually
needs to be in (inches for a machinist, say). This addon fixes both halves:
it scales the exported geometry to the chosen unit, and corrects the
`$INSUNITS` header so downstream CAD/CAM/laser software interprets the
file's scale correctly.

Previously this lived as a direct edit to a forked FreeCAD source tree
(`src/Mod/Draft/importDXF.py`), loaded via a `sys.path` hack pointing at
that dev checkout. That only worked on the one machine with that exact
checkout at that exact path, and broke on every FreeCAD reinstall or
upgrade.

## How it works

This addon ships a complete, working copy of that same `importDXF.py`
(unit dropdown, `$INSUNITS` header correction, C++ scaling when the
installed FreeCAD binary supports it, pure-Python fallback when it
doesn't) as a self-contained file bundled inside this folder, instead of
pointing at an external dev checkout. No monkey-patching code is needed
to make this take effect:

FreeCAD's own Mod-folder loader processes system module folders (where
the real `Draft/importDXF.py` ships) before user Mod folders, but builds
`sys.path` via repeated `insert(0, ...)` -- so every user Mod folder,
including this one, ends up earlier in `sys.path` than the system Draft
folder automatically. Python's `import importDXF`, used throughout
FreeCAD (File -> Export, Draft, TechDraw, any other addon), therefore
finds this addon's bundled copy first and shadows the stock one.

`Init.py`'s only job is to confirm that shadowing actually happened and
say so clearly in the Report view -- a silent failure here (wrong Mod
directory for this FreeCAD version, a stray `package.xml`, anything that
stops this folder from being scanned at all) is otherwise very hard to
notice; see the two gotchas below, both hit and confirmed while building
this.

### Version coupling -- the one real tradeoff of this approach

The bundled `importDXF.py` is the actual upstream-FreeCAD-1.1.3-based
file (the fork's scaling feature re-applied on top of upstream 1.1.3's
own DXF work, including its `draftmake`/`draftobjects`/`draftgeoutils`
submodule split), not a from-scratch reimplementation -- so it has full
feature parity with the original, not an approximation. The tradeoff:
it's tied to that version's internal Draft module layout. It works
against the custom fork binary and against any stock FreeCAD 1.1.3+
install sharing that layout. If a future FreeCAD version restructures
Draft's internals again, this bundled copy will need re-syncing from
whatever version introduces that change -- it won't silently misbehave,
it'll fail an `import` inside `Init.py`'s try/except and log a warning,
not break the rest of FreeCAD.

### Do not add a `package.xml`

Confirmed against `src/App/FreeCADInit.py`'s own Mod-loading logic: when a
`package.xml` is present in a Mod directory, FreeCAD only runs that
directory's `Init.py` if the metadata declares a `<content><workbench>`
block -- otherwise it's skipped silently, no error or warning anywhere.
This addon deliberately has no workbench class, so a `package.xml` here
(even a well-formed one) would silently disable the whole addon. Omitting
`package.xml` entirely falls through to FreeCAD's unconditional
`RunInitPy(Dir)` path instead, which is what actually loads it.

### Newer FreeCAD versions use a version-specific user data directory

Confirmed on FreeCAD 1.1: `FreeCAD.getUserAppDataDir()` returns
`...\FreeCAD\v1-1\`, not the plain `...\FreeCAD\` most documentation
(including earlier drafts of this README) assumes. A file placed in the
unversioned path is silently never scanned -- no error anywhere, it just
behaves as if the addon doesn't exist. Always get the real path from
FreeCAD itself (see Installation below) rather than assuming it.

## Installation

1. Find your actual `Mod` directory by running this in FreeCAD's Python
   console first -- **do not assume the path below**:
   ```python
   import os
   print(os.path.join(FreeCAD.getUserAppDataDir(), "Mod"))
   ```
2. Copy the `DXFExportUnits` folder into that exact directory. For
   reference, the unversioned conventional locations are:
   - **Windows**: `%APPDATA%\FreeCAD\Mod\`
   - **Linux**: `~/.FreeCAD/Mod/` (or `~/.local/share/FreeCAD/Mod/`)
   - **macOS**: `~/Library/Application Support/FreeCAD/Mod/`
3. Fully quit FreeCAD (check Task Manager / `ps` for a lingering process,
   not just closed windows) and relaunch -- Mod directories are only
   scanned at startup.

There is no workbench to switch into, no toolbar, and no new menu --
DXF export everywhere in FreeCAD picks up the scaling automatically.

To verify it actually loaded, check in the Python console:
```python
import importDXF
print(importDXF.__file__)  # should point inside this addon's folder, not Draft's
```
Or check the Report view for a `DXFExportUnits:` line at startup.

## Settings

**Edit -> Preferences -> Import-Export -> DXF + SCALING.** One control:
the export unit dropdown (Millimeters / Centimeters / Meters / Inches /
Feet / Unitless), bound to the same `Mod/Draft` parameter
(`dxfExportUnits`) the bundled `importDXF.py` reads directly. "Unitless"
exports raw millimeter coordinates with no `$INSUNITS` claim at all
(matches the DXF spec's "unitless" convention), rather than scaling by
1.0 and claiming millimeters.

FreeCAD has no supported way for an addon to remove or hide another
preferences page, so the native "DXF" tab (and, on a FreeCAD build with
the fork's own native dropdown baked in, its own copy of this same
control) still appears in the list too -- not present at all on a stock
FreeCAD without that build-specific addition.

An earlier version of this page duplicated every setting from the native
"DXF" tab, not just the unit dropdown. Reverted: with both pages bound to
the same `Mod/Draft` parameters and both potentially open/loaded at once,
whichever page's OK/Apply handler runs last can silently overwrite a
change just made on the other -- confirmed as the cause of "the setting
doesn't stick" on a build that has the native dropdown too. Keeping this
page to only the one control this addon is actually responsible for
avoids that failure mode as much as possible; it isn't fully eliminable
while a second page bound to the same parameter can exist at all, which
stops being possible the moment this runs on a stock FreeCAD without the
fork's native dropdown.

## License

LGPL-2.1-or-later (same as FreeCAD).
