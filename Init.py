# SPDX-License-Identifier: LGPL-2.1-or-later

"""DXFExportUnits -- ships a complete, working copy of the
i-machine-things/FreeCAD fork's importDXF.py (DXF export unit scaling:
unit dropdown, $INSUNITS header, C++ scaling when the binary supports it,
pure-Python fallback when it doesn't) as a self-contained file inside this
addon, instead of a sys.path hack into an external dev source checkout.

No code here does the patching -- FreeCAD's own Mod-folder loader
processes system module folders (where the real Draft/importDXF.py lives)
before user Mod folders, but builds sys.path via repeated insert(0, ...),
so every user Mod folder (including this one) ends up earlier in
sys.path than the system Draft folder automatically. Python's
`import importDXF`, used throughout FreeCAD, therefore finds this
addon's copy first and shadows the stock one -- no explicit sys.path
manipulation needed.

This file's only job is to confirm that shadow actually took effect and
say so clearly, since a silent failure here (wrong Mod directory, a
stray package.xml, anything that stops this folder from being scanned)
is otherwise very hard to notice. See README.md for the version-coupling
caveat: the bundled importDXF.py is tied to upstream FreeCAD 1.1.3's
internal Draft module layout.
"""

import importlib.util
import os

import FreeCAD

try:
    _mod_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:  # FreeCAD runs Init.py without __file__ (1.1 and 26.3)
    _mod_dir = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "DXFExportUnits")

try:
    # Find where `import importDXF` will load from without running it: importing it this early
    # fails in FreeCAD 1.1, because Init.py runs before FreeCAD.GuiUp exists.
    _spec = importlib.util.find_spec("importDXF")
    if _spec is None or not _spec.origin:
        raise ImportError("importDXF not found on sys.path")
    actual_file = _spec.origin
    actual_dir = os.path.dirname(os.path.abspath(actual_file))
    if os.path.normcase(os.path.realpath(actual_dir)) == os.path.normcase(os.path.realpath(_mod_dir)):
        FreeCAD.Console.PrintLog(
            "DXFExportUnits: importDXF loads from this addon ({}) -- "
            "shadowing the stock copy, unit scaling active\n".format(actual_file)
        )
    else:
        FreeCAD.Console.PrintWarning(
            "DXFExportUnits: importDXF loads from {} instead of this addon's "
            "own copy at {} -- unit scaling is NOT active. Another Mod folder "
            "is shadowing ahead of this one, or this folder isn't being "
            "scanned at all (wrong Mod directory for this FreeCAD version? "
            "see README.md).\n".format(actual_file, _mod_dir)
        )
except Exception as exc:  # noqa: BLE001
    FreeCAD.Console.PrintWarning(
        "DXFExportUnits: could not locate importDXF to verify the shadow: {}\n".format(exc)
    )
