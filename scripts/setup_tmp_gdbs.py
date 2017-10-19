import arcpy
import os

arcpy.env.overwriteOutput = True

tmp_dir = arcpy.GetParameterAsText(0)
# tmp_dir = 'C:\\tmp'

if not os.path.isdir(tmp_dir):
    raise IOError('{0} does not exist'.format(tmp_dir))


smoothed_lines = os.path.join(tmp_dir, 'smoothed_lines.gdb')
original_curves = os.path.join(tmp_dir, 'original_curves.gdb')
smoothed_curves = os.path.join(tmp_dir, 'smoothed_curves.gdb')

for g in [smoothed_lines, original_curves, smoothed_curves]:
    if arcpy.Exists(g):
        arcpy.env.workspace = g
        fcs = arcpy.ListFeatureClasses()
        for fc in fcs:
            arcpy.Delete_management(os.path.join(g, fc))
    else:
        arcpy.CreateFileGDB_management(os.path.dirname(g), os.path.basename(g))

arcpy.SetParameterAsText(1, smoothed_lines)
arcpy.SetParameterAsText(2, original_curves)
arcpy.SetParameterAsText(3, smoothed_curves)
