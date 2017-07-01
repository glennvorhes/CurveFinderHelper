import arcpy
import os
import sys
import shutil

arcpy.env.overwriteOutput = True

try:
    import helpers
except ImportError:
    sys.path.extend(os.path.dirname(__file__))
    import helpers

this_dir = os.path.dirname(__file__)
os.chdir(this_dir)
samples_dir = os.path.join(this_dir, os.pardir, 'CurveFinderHelperSamples')

input_f = arcpy.GetParameterAsText(0)
output_workspace = arcpy.GetParameterAsText(1) or r'C:\_temp_smooth.gdb'
debug = str(arcpy.GetParameterAsText(2)).lower() == 'true'

is_feet = helpers.is_feet(input_f)
is_meters = helpers.is_meters(input_f)

if not (is_meters or is_feet):
    arcpy.AddError("Input feature class must be in feet or meters")
    exit(0)

input_name = helpers.get_file_name(input_f)


if output_workspace.find('.gdb') > -1:
    if arcpy.Exists(output_workspace):
        arcpy.Delete_management(output_workspace)

    arcpy.CreateFileGDB_management(os.path.dirname(output_workspace), os.path.basename(output_workspace))
else:

    if not os.path.isdir(output_workspace):
        os.mkdir(output_workspace)

        output_workspace = os.path.join(output_workspace, '_smoothed')

    if os.path.isdir(output_workspace):
        shutil.rmtree(output_workspace)

    os.mkdir(output_workspace)

smooth = r"in_memory\smooth"
tmp_smooth = r"in_memory\temp_smooth"

arcpy.SmoothLine_cartography(input_f, smooth, "BEZIER_INTERPOLATION")

for i in range(10):

    bezier_deviation = (i + 1) * 0.1
    out_name_bezier = helpers.make_output_name(input_name, 'bezier', bezier_deviation)

    paek_tolerance = (i + 1) * 2
    out_name_paek = helpers.make_output_name(input_name, 'paek', paek_tolerance)

    bezier_deviation_str = "{0} Meters".format(bezier_deviation)
    arcpy.CopyFeatures_management(smooth, tmp_smooth)
    arcpy.Densify_edit(tmp_smooth, "OFFSET", max_deviation=bezier_deviation_str)
    arcpy.CopyFeatures_management(tmp_smooth, os.path.join(output_workspace, out_name_bezier))

    paek_tolerance_str = "{0} Meters".format(paek_tolerance)
    arcpy.SmoothLine_cartography(
        input_f, os.path.join(output_workspace, out_name_paek), "PAEK", tolerance=paek_tolerance_str)

    arcpy.AddMessage("BEZIER: {0}, PAEK: {1}".format(bezier_deviation_str, paek_tolerance_str))

    if debug:
        break

arcpy.SetParameterAsText(3, output_workspace)

