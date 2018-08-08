import arcpy
import os
import sys
from uuid import uuid4
import re
from collections import defaultdict

try:
    from classes.CalibScore import CalibScore
    from classes import outFc
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
    from classes.CalibScore import CalibScore
    from classes import outFc

if arcpy.GetParameterAsText(0):
    skip_smoothed = False
else:
    skip_smoothed = True

ground_truth = arcpy.GetParameterAsText(0)
curves_workspace = arcpy.GetParameterAsText(1)
_match_weight = float(arcpy.GetParameterAsText(2))
_miss_weight = float(arcpy.GetParameterAsText(3))
_over_weight = float(arcpy.GetParameterAsText(4))
debug = str(arcpy.GetParameterAsText(5)).lower() == 'true'


class _Result:

    def __init__(self):
        self.method = ''
        self.angle = -1.0
        self.deviation = ''
        self.tolerance = ''
        self.gt_found = -1
        self.gt_missed = -1
        self.no_gt = -1
        self.match_pcnt = -1.1
        self.miss_pcnt = -1.1
        self.over_pcnt = -1.1
        self.score = -1e10
        self.path = ''

    def __str__(self):
        return "Method: {0}, Ang: {1}, GtFound: {2}, GtMissed{3}, NoGt: {4}".format(
            self.method, self.angle, self.gt_found, self.gt_missed, self.no_gt
        )


def make_result(meth_, ang_, dev_, tol_, pth_, calib_, match_weight, miss_weight, over_weight):
    """

    :param meth_:
    :type meth_: str
    :param ang_:
    :type ang_: float
    :param dev_:
    :type dev_: str
    :param tol_:
    :type tol_: str
    :param pth_:
    :type pth_: str
    :param calib_:
    :type calib_: CalibScore
    :param match_weight:
    :type match_weight: float
    :param miss_weight:
    :type miss_weight: float
    :param over_weight:
    :type over_weight: float
    :return:
    :rtype: _Result
    """

    _res = _Result()
    _res.method = meth_
    _res.angle = ang_
    _res.deviation = dev_
    _res.tolerance = tol_
    _res.gt_found = calib_.gt_found_count
    _res.gt_missed = calib_.gt_count - calib.gt_found_count
    _res.no_gt = calib_.id_no_gt_count
    _res.match_pcnt = calib_.matched_pcnt
    _res.miss_pcnt = calib_.missed_pcnt
    _res.over_pcnt = calib_.over_pcnt
    _res.score = calib_.score(match_weight, miss_weight, over_weight)
    _res.path = pth_

    return _res


out_table = r'in_memory\a' + str(uuid4()).replace('-', '')
parts = out_table.split('\\')

arcpy.CreateTable_management(parts[0], parts[1])
arcpy.AddField_management(out_table, 'method', 'TEXT', field_length=30)
arcpy.AddField_management(out_table, 'angle', 'FLOAT')
arcpy.AddField_management(out_table, 'deviation', 'TEXT', field_length=20)
arcpy.AddField_management(out_table, 'tolerance', 'TEXT', field_length=20)

arcpy.AddField_management(out_table, 'gt_found', 'LONG')
arcpy.AddField_management(out_table, 'gt_missed', 'LONG')
arcpy.AddField_management(out_table, 'no_gt', 'LONG')

arcpy.AddField_management(out_table, 'match_pcnt', 'FLOAT')
arcpy.AddField_management(out_table, 'miss_pnct', 'FLOAT')
arcpy.AddField_management(out_table, 'over_pcnt', 'FLOAT')

arcpy.AddField_management(out_table, 'score', 'FLOAT')
arcpy.AddField_management(out_table, 'path', 'TEXT', field_length=200)

calib = CalibScore()

for row in arcpy.SearchCursor(ground_truth):

    gt_seg_id = int(row.getValue(outFc.SEGMENT_ID))
    gt_start_m = float(row.getValue(outFc.START_M))
    gt_end_m = float(row.getValue(outFc.END_M))

    calib.add_gt(gt_seg_id, gt_start_m, gt_end_m)

arcpy.env.workspace = curves_workspace

counter = 0

result_list = []

for fc in arcpy.ListFeatureClasses():

    calib.reset()

    method = ''
    tolerance = ''
    deviation = ''

    pth = os.path.join(curves_workspace, fc)

    pth_lower = pth.lower()

    if pth_lower.find('bezier') > -1:
        method = 'Bezier'
        nm = pth_lower[pth_lower.find('bezier') + 7:]
        deviation_num = float(re.search('[0-9]{2}_[0-9]', nm).group().replace('_', '.'))
        deviation = "{0} Meters".format(deviation_num)
    elif pth_lower.find('paek') > -1:
        method = 'Paek'
        nm = pth_lower[pth_lower.find('paek') + 5:]
        tolerance_num = int(re.search('[0-9]{3}', nm).group().replace('_', '.'))
        tolerance = "{0} Meters".format(tolerance_num)
    else:
        method = 'Original'

    last_thresh = None
    is_first = True

    thresh_seg_start_end_list = []
    thresh_seg_start_end_dict = defaultdict(list)

    for r in arcpy.SearchCursor(pth):
        thresh = round(float(r.getValue(outFc.THRESHOLD)), 2)
        seg_id = int(r.getValue(outFc.SEGMENT_ID))
        start_m = float(r.getValue(outFc.START_M))
        end_m = float(r.getValue(outFc.END_M))

        thresh_seg_start_end_dict[str(thresh)].append((seg_id, start_m, end_m))

    for k, v in thresh_seg_start_end_dict.items():
        calib.reset()

        for c in v:
            calib.add_id(*c)

        result_list.append(
            make_result(method, float(k), deviation, tolerance, pth, calib, _match_weight, _miss_weight, _over_weight)
        )


result_list.sort(key=lambda x: x.score, reverse=True)

insert = arcpy.InsertCursor(out_table)
row = None
for i in range(len(result_list)):
    r = result_list[i]
    """
    @:type: _Result
    """

    row = insert.newRow()
    row.setValue("method", r.method)
    row.setValue("angle", r.angle)

    row.setValue("deviation", r.deviation)
    row.setValue("tolerance", r.tolerance)

    row.setValue("gt_found", r.gt_found)
    row.setValue("gt_missed", r.gt_missed)
    row.setValue("no_gt", r.no_gt)

    row.setValue("match_pcnt", r.match_pcnt)
    row.setValue("miss_pnct", r.miss_pcnt)
    row.setValue("over_pcnt", r.over_pcnt)

    row.setValue("score", r.score)
    row.setValue("path", r.path)

    insert.insertRow(row)
del row, insert

if len(result_list) == 0:
    arcpy.AddError("Best method not found")
    exit(0)

best = result_list[0]

out_msg = "Best Approach\n"
out_msg += '\tMethod: {0}\n'.format(best.method)
out_msg += '\tAngle: {0}\n'.format(best.angle)

if best.deviation:
    out_msg += '\tDeviation: {0}\n'.format(best.deviation)
elif best.tolerance:
    out_msg += '\tTolerance: \n'.format(best.tolerance)
else:
    out_msg += '\tOriginal input is best'

arcpy.AddMessage(out_msg)
arcpy.SetParameterAsText(6, out_table)
