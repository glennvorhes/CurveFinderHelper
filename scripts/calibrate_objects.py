
import math
import re

import arcpy

import helpers

arcpy.env.overwriteOutput = True


def dist_form(x1, y1, x2, y2):
    return ((x1 - x2)**2 + (y1 - y2)**2)**0.5


class _CurveCollection:

    def __init__(self, fc, gt):
        self.score = 0
        self.angle = float(re.search('[0-9]p[0-9]', fc).group().replace('p', '.'))

        tmp_join = r'in_memory\tmp_join'

        arcpy.SpatialJoin_analysis(fc, gt, tmp_join, "JOIN_ONE_TO_MANY", "KEEP_ALL", match_option="CLOSEST")
        helpers.set_curve_geom_number(tmp_join)

        for r in arcpy.SearchCursor(tmp_join):
            self.score += math.fabs(r.getValue('length_gt') - r.getValue('length'))
            # print(math.fabs(r.getValue('length_gt') - r.getValue('length')))
            # print('d', dist_form(r.getValue('start_x'), r.getValue('start_x_gt'), r.getValue('start_y'), r.getValue('start_y_gt')))


class CurveCollectionOriginal(_CurveCollection):
    def __init__(self, fc, gt):
        _CurveCollection.__init__(self, fc, gt)
        self.method = "Original"


class CurveCollectionBezier(_CurveCollection):
    def __init__(self, fc, gt):
        _CurveCollection.__init__(self, fc, gt)
        nm = fc[fc.find('bezier') + 7:]
        self.method = "Bezier"
        self.deviation = float(re.search('[0-9]{2}_[0-9]', nm).group().replace('_', '.'))


class CurveCollectionPaek(_CurveCollection):
    def __init__(self, fc, gt):
        _CurveCollection.__init__(self, fc, gt)
        self.method = "Bezier"
        nm = fc[fc.find('paek') + 5:]
        self.tolerance = int(re.search('[0-9]{3}', nm).group().replace('_', '.'))

