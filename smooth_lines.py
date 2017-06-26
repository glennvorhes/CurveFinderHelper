# import arcpy
import os
import subprocess

input_f = r"C:\samples\vermont\vermont_sub.shp"
tmp_smooth = r"in_memory\smooth"

os.chdir(os.path.dirname(__file__))

# args = ['CurveCommandLine.exe', '-f', 'primarynam', '-m', input_f]
args = ['CurveCommandLine.exe', '-f', 'primarynam', input_f]

p = subprocess.Popen(args)
#
# (output, err) = p.communicate()
# print(output)
#This makes the wait possible
p_status = p.wait()


#
# # bezier process
# arcpy.SmoothLine_cartography(input_f, tmp_smooth, "BEZIER_INTERPOLATION")
# # vary max deviation, keep it low, converts curves to lines with vertices provided smoothline output to a gdb or in_memory
# arcpy.Densify_edit(tmp_smooth, "OFFSET", max_deviation="0.1 Meters")
#
# # paek, vary smoothing tolerance, might need to to high
# arcpy.SmoothLine_cartography("vermont_sub", r"in_memory\paek", "PAEK", "1 Meters")
#



# CurveCommandLine.exe
