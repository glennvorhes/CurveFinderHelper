import os
import sys

import arcpy

try:
    import helpers
except ImportError:
    sys.path.extend(os.path.dirname(__file__))
    import helpers

os.chdir(os.path.dirname(__file__))

input_fc = arcpy.GetParameterAsText(0)
name_field = str(arcpy.GetParameterAsText(1))
smoothing_alg = str(arcpy.GetParameterAsText(2)) or 'None'
deviation_or_tolerance = str(arcpy.GetParameterAsText(3))
angle = float(str(arcpy.GetParameterAsText(4)))
output = arcpy.GetParameterAsText(5)

tmp_gdb = r'C:\_tmp.gdb'
tmp_proc = os.path.join(tmp_gdb, 'tmp')

if not arcpy.Exists(tmp_gdb):
    arcpy.CreateFileGDB_management(os.path.dirname(tmp_gdb), os.path.basename(tmp_gdb))

if smoothing_alg == 'Bezier':
    arcpy.SmoothLine_cartography(input_fc, tmp_proc, "BEZIER_INTERPOLATION")
    arcpy.Densify_edit(tmp_proc, "OFFSET", max_deviation=deviation_or_tolerance)
elif smoothing_alg == 'Paek':
    arcpy.SmoothLine_cartography(input_fc, tmp_proc, "PAEK", tolerance=deviation_or_tolerance)
elif smoothing_alg == 'None':
    arcpy.CopyFeatures_management(input_fc, tmp_proc)
else:
    arcpy.AddError("smoothing algorithm not found")
    exit(1)

msg = helpers.run_finder(tmp_proc, name_field, tmp_gdb, angle=angle)

files = helpers.file_list_from_msg(msg)

if len(files) > 0:
    arcpy.CopyFeatures_management(files[0], output)
else:
    arcpy.AddError("Something wrong with copying output")
