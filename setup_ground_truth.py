import arcpy
import os
import sys

try:
    import helpers
except ImportError:
    sys.path.extend(os.path.dirname(__file__))
    import helpers

input_fc = arcpy.GetParameterAsText(0)

arcpy.AddField_management(input_fc, 'SEGMENT_ID', 'LONG')

fields = helpers.set_curve_geom_number(input_fc, is_ground_truth=True)

arcpy.CalculateField_management(input_fc, 'SEGMENT_ID', '[uid]')

desc = arcpy.Describe(input_fc)

fields.extend([str(desc.OIDFieldName), str(desc.ShapeFieldName), 'SEGMENT_ID'])

for f in desc.fields:
    if str(f.name) not in fields:
        arcpy.DeleteField_management(input_fc, f.name)


output_fc = arcpy.SetParameterAsText(1, input_fc)

