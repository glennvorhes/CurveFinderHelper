import arcpy

fc = arcpy.GetParameterAsText(0)
field = arcpy.GetParameterAsText(1)



arcpy.CalculateField_management(fc, field, '!{0}!'.format(arcpy.Describe(fc).OIDFieldName), 'PYTHON_9.3')

arcpy.SetParameterAsText(2, arcpy.Describe(fc).catalogPath)



