import arcpy

arcpy.env.overwriteOutput = True


input_fc = arcpy.GetParameterAsText(0)
catalog_path = arcpy.Describe(input_fc).catalogPath

arcpy.CopyFeatures_management(input_fc, r'in_memory/temp_copy')
arcpy.CopyFeatures_management(r'in_memory/temp_copy', catalog_path)


arcpy.SetParameterAsText(1, catalog_path)
