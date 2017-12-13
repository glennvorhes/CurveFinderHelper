import arcpy
from uuid import uuid4

arcpy.env.overwriteOutput = True


input_fc = arcpy.GetParameterAsText(0)
output_fc = arcpy.GetParameterAsText(1)
catalog_path = arcpy.Describe(output_fc).catalogPath

# tmp_copy = r'in_memory/a{0}'.format(str(uuid4()).replace('-', ''))

arcpy.CopyFeatures_management(input_fc, catalog_path)
# arcpy.CopyFeatures_management(tmp_copy, input_fc)
#
# arcpy.SetParameterAsText(1, input_fc)
