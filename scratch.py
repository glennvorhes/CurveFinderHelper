


tmp_smooth = r"in_memory\smooth"

args = ['CurveCommandLine.exe', '-f', 'primarynam', '-m', input_f]
# args = ['CurveCommandLine.exe', '-f', 'primarynam', input_f]

# curve finding
# p = subprocess.Popen(args, stdout=subprocess.PIPE)
# p_status = p.wait()
# msg = p.stdout.read()
# print(msg)


test = r"""
Running angle 0.5
Output to: C:\Users\glenn\PycharmProjects\CurveFinderHelperSamples\vermont\vermont_sub_0p5.shp
Running angle 0.6
Output to: C:\Users\glenn\PycharmProjects\CurveFinderHelperSamples\vermont\vermont_sub_0p6.shp
Running angle 0.7
Output to: C:\Users\glenn\PycharmProjects\CurveFinderHelperSamples\vermont\vermont_sub_0p7.shp
Running angle 0.8
Output to: C:\Users\glenn\PycharmProjects\CurveFinderHelperSamples\vermont\vermont_sub_0p8.shp
Running angle 0.9
Output to: C:\Users\glenn\PycharmProjects\CurveFinderHelperSamples\vermont\vermont_sub_0p9.shp
Running angle 1
Output to: C:\Users\glenn\PycharmProjects\CurveFinderHelperSamples\vermont\vermont_sub_1.shp
Running angle 1.1
Output to: C:\Users\glenn\PycharmProjects\CurveFinderHelperSamples\vermont\vermont_sub_1p1.shp
Running angle 1.2
Output to: C:\Users\glenn\PycharmProjects\CurveFinderHelperSamples\vermont\vermont_sub_1p2.shp
Running angle 1.3
Output to: C:\Users\glenn\PycharmProjects\CurveFinderHelperSamples\vermont\vermont_sub_1p3.shp
Running angle 1.4
Output to: C:\Users\glenn\PycharmProjects\CurveFinderHelperSamples\vermont\vermont_sub_1p4.shp
Running angle 1.5
Output to: C:\Users\glenn\PycharmProjects\CurveFinderHelperSamples\vermont\vermont_sub_1p5.shp
Finished Sucessfully

"""
out_fclasses = []

for f in re.findall(r'[A-Z]:\\.+', test):
    if f.find('.gdb') > -1:
        pass
    else:
        if not os.path.isfile(f):
            continue
    out_fclasses.append(f)

print(out_fclasses)

# print re.findall(r'[A-Z]:\\.+', test)

#
# # bezier process
# arcpy.SmoothLine_cartography(input_f, tmp_smooth, "BEZIER_INTERPOLATION")
# # vary max deviation, keep it low, converts curves to lines with vertices provided smoothline output to a gdb or in_memory
# arcpy.Densify_edit(tmp_smooth, "OFFSET", max_deviation="0.1 Meters")
#
# # paek, vary smoothing tolerance, might need to to high
# arcpy.SmoothLine_cartography("vermont_sub", r"in_memory\paek", "PAEK", "1 Meters")
#



