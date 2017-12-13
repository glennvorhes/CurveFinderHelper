import sys
import os
import arcpy

try:
    from classes.CurveFinder import CurveFinder
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
    from classes.CurveFinder import CurveFinder
from arcpy_geom.arcpy_descibe import ArcpyDescribeFeatureClass


arcpy.env.overwriteOutput = True

original = arcpy.GetParameterAsText(0)
name_field = str(arcpy.GetParameterAsText(1))
out_workspace = str(arcpy.GetParameterAsText(2)).strip()
debug = str(arcpy.GetParameterAsText(3)).lower() == 'true'
add_stuff = ''

# original = r'C:\Users\glenn\Desktop\curves\iowa.gdb\primary_dissolve_dis_sub5'
# name_field = 'OFF_NAME'
# out_workspace = r'C:\Users\glenn\Desktop\curves\iowa.gdb'
# debug = True
# add_stuff = 'a'

desc = ArcpyDescribeFeatureClass(original)

original_curves = os.path.join(out_workspace, 'original') + add_stuff
finder = CurveFinder(desc.catalog_path, road_name_field=name_field)

if debug:
    finder.run(1.0)
else:
    finder.run(iterate=True)

finder.output_curves(original_curves)
arcpy.SetParameterAsText(4, original_curves)
