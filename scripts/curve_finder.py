import arcpy
import add_dir
from classes.CurveFinder import CurveFinder
from datetime import datetime
import os

tst_path3 = r'C:\tmp\tmp.gdb\iowa_dis_13_sub_1'

# r'C:\tmp\tmp.gdb\iowa_dis_13_gt'

finder = CurveFinder(tst_path3, road_name_field='OFF_NAME')
finder.run(angle=5)
out_fc = os.path.join(r'C:\tmp\tmp.gdb', datetime.now().strftime('p%Y_%m_%d_%H_%M_%S'))
finder.output_curves(out_fc)

print(out_fc)


