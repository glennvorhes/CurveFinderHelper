
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


if arcpy.GetParameterAsText(0):
    skip_smoothed = False
else:
    skip_smoothed = True


ground_truth = arcpy.GetParameterAsText(0) or r'C:\_tmp.gdb\roads_gt3'
subset_roads = arcpy.GetParameterAsText(1) or r'C:\_tmp.gdb\roads_subset'
original_curves_workspace = arcpy.GetParameterAsText(2) or r'C:\tmp\original_curves.gdb'
smoothed_curves_workspace = arcpy.GetParameterAsText(3) or r'C:\tmp\smoothed_curves.gdb'
bug = arcpy.GetParameterAsText(5)
if bug:
    debug = str(bug).lower() == 'true'
else:
    debug = True




compare_list = []
"""
:type: list[cal.CurveCollectionOriginal|cal.CurveCollectionBezier|cal.CurveCollectionPaek]
"""


arcpy.env.workspace = original_curves_workspace

for fc in arcpy.ListFeatureClasses():
    compare_list.append(cal.CurveCollectionOriginal(os.path.join(original_curves_workspace, fc), subset_roads, ground_truth))

arcpy.env.workspace = smoothed_curves_workspace
counter = 0

if not skip_smoothed:
    for fc in arcpy.ListFeatureClasses():
        if fc.find('bezier') > -1:
            compare_list.append(cal.CurveCollectionBezier(os.path.join(smoothed_curves_workspace, fc), subset_roads, ground_truth))
        elif fc.find('paek') > -1:
            compare_list.append(cal.CurveCollectionPaek(os.path.join(smoothed_curves_workspace, fc), subset_roads, ground_truth))

        counter += 1

        if counter > helpers.max_run * 2 and debug:
            break

compare_list.sort(key=lambda s: s.score)

out_table = r'in_memory\a' + str(uuid4()).replace('-', '')
parts = out_table.split('\\')

arcpy.CreateTable_management(parts[0], parts[1])
arcpy.AddField_management(out_table, 'method', 'TEXT', field_length=30)
arcpy.AddField_management(out_table, 'deviation', 'TEXT', field_length=20)
arcpy.AddField_management(out_table, 'tolerance', 'TEXT', field_length=20)
arcpy.AddField_management(out_table, 'angle', 'FLOAT')

arcpy.AddField_management(out_table, 'cnt_under', 'LONG')
arcpy.AddField_management(out_table, 'cnt_over', 'LONG')

arcpy.AddField_management(out_table, 'len_under', 'FLOAT')
arcpy.AddField_management(out_table, 'len_over', 'FLOAT')

arcpy.AddField_management(out_table, 'srt_offset', 'FLOAT')
arcpy.AddField_management(out_table, 'end_offset', 'FLOAT')

arcpy.AddField_management(out_table, 'score', 'FLOAT')
arcpy.AddField_management(out_table, 'path', 'TEXT', field_length=200)


rows = arcpy.InsertCursor(out_table)

for c in compare_list:
    row = rows.newRow()
    row.setValue("method", c.method)
    if isinstance(c, cal.CurveCollectionBezier):
        row.setValue("deviation", c.deviation)
    if isinstance(c, cal.CurveCollectionPaek):
        row.setValue("tolerance", c.tolerance)
    row.setValue("angle", c.angle)

    row.setValue("cnt_under", c.cnt_under)
    row.setValue("cnt_over", c.cnt_over)

    row.setValue("len_under", c.len_under)
    row.setValue("len_over", c.len_over)

    row.setValue("srt_offset", c.start_offset)
    row.setValue("end_offset", c.end_offset)

    row.setValue("score", c.score)
    row.setValue("path", c.fc_path)
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

arcpy.SetParameterAsText(4, out_table)


