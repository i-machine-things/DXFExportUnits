# SPDX-License-Identifier: LGPL-2.1-or-later

"""DXFExportUnits -- GUI-only half: registers the "DXF Export Units"
preferences page under Import-Export, next to FreeCAD's native DXF
settings. The export scaling itself needs nothing GUI-specific -- it
comes from this addon's bundled importDXF.py shadowing the stock one via
Mod-folder load order (see Init.py, which just verifies that shadow took
effect), active in console mode too.

Deliberately no Workbench subclass, no toolbar, no commands, no menu
entries -- this addon has nothing for a user to switch into or click;
the only thing to interact with is the one preferences page below.
"""

import os

import FreeCAD
import FreeCADGui

try:
    _mod_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _mod_dir = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "DXFExportUnits")

_prefs_ui = os.path.join(_mod_dir, "Resources", "ui", "preferences-dxfexportunits.ui")

if os.path.exists(_prefs_ui):
    FreeCADGui.addPreferencePage(_prefs_ui, "Import-Export")
else:
    FreeCAD.Console.PrintWarning(
        "DXFExportUnits: preferences UI not found at {} -- export unit will "
        "default to Millimeters until set via the Parameter editor "
        "(Edit -> Preferences -> General -> Parameters, "
        "BaseApp/Preferences/Mod/Draft/dxfExportUnits).\n".format(_prefs_ui)
    )
