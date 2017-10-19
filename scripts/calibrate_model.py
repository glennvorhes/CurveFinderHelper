
import arcpy
import os
import sys
from uuid import uuid4


try:
    import helpers
    import calibrate_objects as cal
except ImportError:
    sys.path.extend(os.path.dirname(__file__))
    import helpers
    import calibrate_objects as cal


ground_truth = arcpy.GetParameterAsText(0) or r'C:\_tmp.gdb\roads_gt3'
original_curves_workspace = arcpy.GetParameterAsText(1) or r'C:\tmp\original_curves'
smoothed_curves_workspace = arcpy.GetParameterAsText(2) or r'C:\tmp\smoothed_curves'
bug = arcpy.GetParameterAsText(4)
if bug:
    debug = str(bug).lower() == 'true'
else:
    debug = True


compare_list = []
"""
:type: list[cal.CurveCollectionOriginal|cal.CurveCollectionBezier|cal.CurveCollectionPaek]
"""

max_run = 2
arcpy.env.workspace = original_curves_workspace

for fc in arcpy.ListFeatureClasses():
    compare_list.append(cal.CurveCollectionOriginal(fc, ground_truth))

arcpy.env.workspace = smoothed_curves_workspace
counter = 0
for fc in arcpy.ListFeatureClasses():

    if fc.find('bezier') > -1:
        compare_list.append(cal.CurveCollectionBezier(fc, ground_truth))
    elif fc.find('paek') > -1:
        compare_list.append(cal.CurveCollectionPaek(fc, ground_truth))

    counter += 1

    if counter > max_run and debug:
        break

compare_list.sort(key=lambda s: s.score)

out_table = r'in_memory\a' + str(uuid4()).replace('-', '')
parts = out_table.split('\\')

arcpy.CreateTable_management(parts[0], parts[1])
arcpy.AddField_management(out_table, 'method', 'TEXT', field_length=30)
arcpy.AddField_management(out_table, 'deviation', 'FLOAT')
arcpy.AddField_management(out_table, 'tolerance', 'SHORT')
arcpy.AddField_management(out_table, 'angle', 'FLOAT')
arcpy.AddField_management(out_table, 'score', 'FLOAT')

rows = arcpy.InsertCursor(out_table)

for c in compare_list:
    row = rows.newRow()
    row.setValue("method", c.method)
    if isinstance(c, cal.CurveCollectionBezier):
        row.setValue("deviation", c.deviation)
    if isinstance(c, cal.CurveCollectionPaek):
        row.setValue("tolerance", c.tolerance)
    row.setValue("angle", c.angle)
    row.setValue("score", c.score)
    rows.insertRow(row)

if len(compare_list) == 0:
    arcpy.AddError("Best method not found")
    exit(0)

best = compare_list[0]

out_msg = "Best Approach\n"
out_msg += '\tMethod: {0}\n'.format(best.method)
out_msg += '\tAngle: {0}\n'.format(best.angle)

if isinstance(best, cal.CurveCollectionBezier):
    out_msg += '\tDeviation: {0}\n'.format(best.deviation)
elif isinstance(best, cal.CurveCollectionPaek):
    out_msg += '\tTolerance: \n'.format(best.tolerance)
elif isinstance(best, cal.CurveCollectionOriginal):
    pass
else:
    arcpy.AddError("Best method not found")

arcpy.SetParameterAsText(3, out_table)


