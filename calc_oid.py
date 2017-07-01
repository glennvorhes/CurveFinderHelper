import arcpy

fc = arcpy.GetParameterAsText(0)
field = arcpy.GetParameterAsText(1)


input_copy = r'in_memory\input_copy'

arcpy.CalculateField_management(fc, field, '!{0}!'.format(arcpy.Describe(fc).OIDFieldName), 'PYTHON_9.3')

arcpy.SetParameterAsText(2, arcpy.Describe(fc).catalogPath)



