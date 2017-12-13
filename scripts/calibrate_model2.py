
import arcpy
import os
import sys
from uuid import uuid4

try:
    from classes.Calibrate import Calibrate
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
    from classes.Calibrate import Calibrate

if arcpy.GetParameterAsText(0):
    skip_smoothed = False
else:
    skip_smoothed = True

ground_truth = arcpy.GetParameterAsText(0)
curves_workspace = arcpy.GetParameterAsText(1)
debug = str(arcpy.GetParameterAsText(2)).lower() == 'true'
#
# ground_truth = r'C:\Users\glenn\Desktop\curves\iowa.gdb\primary_dissolve_gt_prep17'
# curves_workspace = r'C:\tmp\temp_curves.gdb'
# debug = True

out_table = r'in_memory\a' + str(uuid4()).replace('-', '')
parts = out_table.split('\\')

arcpy.CreateTable_management(parts[0], parts[1])
arcpy.AddField_management(out_table, 'method', 'TEXT', field_length=30)
arcpy.AddField_management(out_table, 'angle', 'FLOAT')
arcpy.AddField_management(out_table, 'deviation', 'TEXT', field_length=20)
arcpy.AddField_management(out_table, 'tolerance', 'TEXT', field_length=20)

arcpy.AddField_management(out_table, 'cnt_match', 'LONG')
arcpy.AddField_management(out_table, 'cnt_under', 'LONG')
arcpy.AddField_management(out_table, 'cnt_over', 'LONG')

arcpy.AddField_management(out_table, 'len_match', 'FLOAT')
arcpy.AddField_management(out_table, 'len_under', 'FLOAT')
arcpy.AddField_management(out_table, 'len_over', 'FLOAT')

arcpy.AddField_management(out_table, 'score', 'FLOAT')
arcpy.AddField_management(out_table, 'path', 'TEXT', field_length=200)

calib = Calibrate(ground_truth, curves_workspace, debug)

insert = arcpy.InsertCursor(out_table)
row = None
for c in calib.all_by_thresh:
    row = insert.newRow()
    row.setValue("angle", c.threshold)

    row.setValue("method", c.method)

    if c.deviation is not None:
        row.setValue("deviation", c.deviation)
    if c.tolerance is not None:
        row.setValue("tolerance", c.tolerance)

    row.setValue("cnt_match", c.count_match)
    row.setValue("cnt_under", c.count_under)
    row.setValue("cnt_over", c.count_over)

    row.setValue("len_match", c.len_match)
    row.setValue("len_under", c.len_miss)
    row.setValue("len_over", c.len_over)

    row.setValue("score", c.score)
    row.setValue("path", c.path)

    insert.insertRow(row)
del row, insert

if len(calib.all_by_thresh) == 0:
    arcpy.AddError("Best method not found")
    exit(0)

best = calib.all_by_thresh[0]

out_msg = "Best Approach\n"
out_msg += '\tMethod: {0}\n'.format(best.method)
out_msg += '\tAngle: {0}\n'.format(best.threshold)

if best.deviation is not None:
    out_msg += '\tDeviation: {0}\n'.format(best.deviation)
elif best.tolerance is not None:
    out_msg += '\tTolerance: \n'.format(best.tolerance)
else:
    out_msg += '\tOriginal input is best'
print(out_msg)
arcpy.SetParameterAsText(3, out_table)
