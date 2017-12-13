import os
import sys

import arcpy

# try:
#     import helpers
# except ImportError:
#     sys.path.extend(os.path.dirname(__file__))
#     import helpers

try:
    from classes.Calibrate import Calibrate
    from classes.CurveFinder import CurveFinder
    from arcpy_geom.arcpy_descibe import ArcpyDescribeFeatureClass
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
    from classes.CurveFinder import CurveFinder
    from classes.Calibrate import Calibrate
    from arcpy_geom.arcpy_descibe import ArcpyDescribeFeatureClass


# os.chdir(os.path.dirname(__file__))

input_fc = arcpy.GetParameterAsText(0)
name_field = str(arcpy.GetParameterAsText(1))
smoothing_alg = str(arcpy.GetParameterAsText(2)) or 'None'
deviation_or_tolerance = str(arcpy.GetParameterAsText(3)).strip()
angle = float(str(arcpy.GetParameterAsText(4)))
output = arcpy.GetParameterAsText(5)

if smoothing_alg in ['Bezier', 'Paek'] and len(deviation_or_tolerance) == 0:
    arcpy.AddError('Deviation or Tolerance must be provided if a smoothing algorithm is selected')

tmp_features = r'in_memory\tmp_feats'

if smoothing_alg == 'Bezier':
    arcpy.SmoothLine_cartography(input_fc, tmp_features, "BEZIER_INTERPOLATION")
    arcpy.Densify_edit(tmp_features, "OFFSET", max_deviation=deviation_or_tolerance)
elif smoothing_alg == 'Paek':
    arcpy.SmoothLine_cartography(input_fc, tmp_features, "PAEK", tolerance=deviation_or_tolerance)
elif smoothing_alg == 'None':
    arcpy.CopyFeatures_management(input_fc, tmp_features)
else:
    arcpy.AddError("smoothing algorithm not found")

desc = ArcpyDescribeFeatureClass(tmp_features)
finder = CurveFinder(desc.catalog_path, road_name_field=name_field)
finder.run(angle=angle)
finder.output_curves(output)
