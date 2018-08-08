import arcpy
import os
from uuid import uuid4

arcpy.env.overwriteOutput = True

tmp_dir = arcpy.GetParameterAsText(0)
# tmp_dir = 'C:\\tmp'

if not os.path.isdir(tmp_dir):
    raise IOError('{0} does not exist'.format(tmp_dir))


smoothed_lines = os.path.join(tmp_dir, '{0}.gdb'.format('a' + str(uuid4()).replace('-', '')))
tmp_curves = os.path.join(tmp_dir, '{0}.gdb'.format('a' + str(uuid4()).replace('-', '')))

for g in [smoothed_lines, tmp_curves]:
    arcpy.CreateFileGDB_management(os.path.dirname(g), os.path.basename(g))

arcpy.SetParameterAsText(1, smoothed_lines)
arcpy.SetParameterAsText(2, tmp_curves)
