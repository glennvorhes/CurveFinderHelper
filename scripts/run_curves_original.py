import os
import sys

import arcpy

try:
    import helpers
except ImportError:
    sys.path.extend(os.path.dirname(__file__))
    import helpers

os.chdir(os.path.dirname(__file__))

original = arcpy.GetParameterAsText(0)
name_field = str(arcpy.GetParameterAsText(1))
out_workspace = str(arcpy.GetParameterAsText(2)).strip()
debug = arcpy.GetParameterAsText(3).strip().lower() == 'true'

# workspace = r'C:\_temp\_smoothed'
# name_field = 'PRIMARYNAM'


name_field = helpers.setup_name_field(name_field)
helpers.setup_workspace(out_workspace)


the_file = arcpy.Describe(original).catalogPath
msg = helpers.run_finder(the_file, name_field, out_workspace, multi=(not debug))
arcpy.AddMessage(msg)


arcpy.SetParameterAsText(4, out_workspace)
