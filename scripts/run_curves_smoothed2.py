import os
import sys

import arcpy

try:
    from classes.CurveFinder import CurveFinder
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
    from classes.CurveFinder import CurveFinder

from arcpy_geom.arcpy_descibe import ArcpyDescribeFeatureClass

# os.chdir(os.path.dirname(__file__))

smoothed_workspace = arcpy.GetParameterAsText(0)
name_field = str(arcpy.GetParameterAsText(1))
curve_workspace = str(arcpy.GetParameterAsText(2)).strip()
debug = str(arcpy.GetParameterAsText(3)).lower() == 'true'

# workspace = r'C:\_temp\_smoothed'
# name_field = 'PRIMARYNAM'

arcpy.env.workspace = smoothed_workspace
#
# name_field = helpers.setup_name_field(name_field)
# helpers.setup_workspace(out_workspace)

counter = 0
fcs = arcpy.ListFeatureClasses()

for f in fcs:
    the_file = os.path.join(smoothed_workspace, f)
    out_curve = os.path.join(curve_workspace, f)

    finder = CurveFinder(the_file, road_name_field=name_field)
    if debug:
        finder.run(1.0)
    else:
        finder.run(iterate=True)
    finder.output_curves(out_curve)
    arcpy.AddMessage("Created: " + out_curve)

arcpy.SetParameterAsText(4, curve_workspace)
