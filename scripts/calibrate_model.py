
import arcpy
import os
import sys
from collections import defaultdict

try:
    import helpers
    import calibrate_objects as cal
except ImportError:
    sys.path.extend(os.path.dirname(__file__))
    import helpers
    import calibrate_objects as cal


ground_truth = arcpy.GetParameterAsText(0)
original_curves_workspace = arcpy.GetParameterAsText(1)
smoothed_curves_workspace = arcpy.GetParameterAsText(2)
debug = str(arcpy.GetParameterAsText(2)).lower() == 'true'
result_file = r'C:\Users\glenn\Desktop\output.txt'

# ground_truth = r'C:\_temp\New File Geodatabase.gdb\output_gt3'
# original_curves_workspace = r'C:\_original.gdb'
# smoothed_curves_workspace = r'C:\_temp_curves.gdb'

compare_list = []


arcpy.env.workspace = original_curves_workspace

max = 10

counter = 0
for fc in arcpy.ListFeatureClasses():

    compare_list.append(cal.CurveCollectionOriginal(fc, ground_truth))

    counter += 1

    if counter > max and debug:
        break

arcpy.env.workspace = smoothed_curves_workspace

counter = 0
for fc in arcpy.ListFeatureClasses():

    if fc.find('bezier') > -1:
        compare_list.append(cal.CurveCollectionBezier(fc, ground_truth))
    elif fc.find('paek') > -1:
        compare_list.append(cal.CurveCollectionPaek(fc, ground_truth))

    counter += 1

    if counter > max and debug:
        break

compare_list.sort(key=lambda s: s.score)

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

with open(result_file, 'w') as f:
    f.write(out_msg)





