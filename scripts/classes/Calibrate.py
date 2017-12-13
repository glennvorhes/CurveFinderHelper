import arcpy
from scripts.classes import outFc
from collections import defaultdict
import re
import os


class CurveSegment:
    def __init__(self, seg_id, start_m, end_m):
        self.seg_id = seg_id
        self.start_m = start_m
        self.end_m = end_m
        self.length = end_m - start_m
        self.found = False


class _ByThreshold:
    def __init__(self, threshold):
        self.threshold = threshold
        self.segment_id_dict = defaultdict(list)
        self.len_match = 0
        self.len_miss = 0
        self.len_over = 0
        self.count_over = 0
        self.count_under = 0
        self.count_match = 0
        self.method = None
        self.tolerance = None
        self.deviation = None
        self.path = None

    def add_segment(self, seg_id, start_m, end_m):
        self.segment_id_dict[str(seg_id)].append(CurveSegment(seg_id, start_m, end_m))

    def sort(self):
        for k in self.segment_id_dict.keys():
            self.segment_id_dict[k].sort(key=lambda x: x.start_m)

    def get_by_key(self, k):
        """

        :param k:
        :type k:
        :return:
        :rtype: list[CurveSegment]
        """

        if k not in self.segment_id_dict.keys():
            return []

        return self.segment_id_dict[k]

    @property
    def score(self):
        return self.len_match - self.len_miss - self.len_over


def match_miss_over(gt, bt):
    """

    :param gt:
    :type gt: GroundTruthCollection
    :param bt:
    :type bt: _ByThreshold
    :return:
    :rtype:
    """

    all_keys = [k for k in gt.segment_id_dict.keys()]
    all_keys.extend([k for k in bt.segment_id_dict.keys()])
    all_keys = list(set(all_keys))

    for k in all_keys:
        if not gt.get_by_key(k):
            for a in bt.segment_id_dict[k]:
                bt.len_over += a.length
                a.found = True
                bt.count_over += 1
        if not bt.get_by_key(k):
            for a in bt.segment_id_dict[k]:
                bt.len_miss += a.length
                a.found = True
                bt.count_under += 1

        for id_curve in bt.get_by_key(k):
            for gt_curve in gt.get_by_key(k):
                if id_curve.start_m <= gt_curve.start_m and id_curve.end_m >= gt_curve.start_m and id_curve.end_m <= gt_curve.end_m:
                    bt.len_match += id_curve.end_m - gt_curve.start_m
                    bt.len_over += gt_curve.start_m - id_curve.start_m
                    bt.count_match += 1
                    id_curve.found = True
                    gt_curve.found = True
                elif id_curve.start_m >= gt_curve.start_m and id_curve.start_m <= gt_curve.end_m and id_curve.end_m >= gt_curve.end_m:
                    bt.len_match += gt_curve.end_m - id_curve.start_m
                    bt.len_over += id_curve.end_m - gt_curve.end_m
                    bt.count_match += 1
                    id_curve.found = True
                    gt_curve.found = True
                elif id_curve.start_m <= gt_curve.start_m and id_curve.end_m >= gt_curve.end_m:
                    bt.len_match += gt_curve.length
                    bt.len_over += gt_curve.start_m - id_curve.start_m
                    bt.len_over += id_curve.end_m - gt_curve.end_m
                    bt.count_match += 1
                    id_curve.found = True
                    gt_curve.found = True
                elif gt_curve.start_m <= id_curve.start_m and id_curve.end_m <= gt_curve.end_m:
                    bt.len_match += id_curve.length
                    bt.len_miss += id_curve.start_m - gt_curve.start_m
                    bt.len_miss += gt_curve.end_m - id_curve.end_m
                    bt.count_match += 1
                    id_curve.found = True
                    gt_curve.found = True

            if not id_curve.found:
                bt.len_over += id_curve.length
                bt.count_over += 1

        for gt_curve in gt.get_by_key(k):
            if not gt_curve.found:
                bt.len_miss += gt_curve.length
                bt.count_under += 1


class _CurveCollection:

    def __init__(self, fc_path, method):
        self.method = method
        self.path = fc_path
        self.by_threshold_dict = {}

        search = arcpy.SearchCursor(fc_path)

        for row in search:

            thresh = float(row.getValue(outFc.THRESHOLD))
            if str(thresh) not in self.by_threshold_dict:
                self.by_threshold_dict[str(thresh)] = _ByThreshold(thresh)

            self.by_threshold_dict[str(thresh)].add_segment(
                row.getValue(outFc.SEGMENT_ID),
                row.getValue(outFc.START_M),
                row.getValue(outFc.END_M)
            )

        for v in self.by_threshold_dict.values():
            v.sort()

        self._by_threshold_list = [v for v in self.by_threshold_dict.values()]
        """
        :type: list[_ByThreshold]
        """

    @property
    def by_threshold_list(self):
        """

        :return:
        :rtype: list[_ByThreshold]
        """
        return [v for v in self._by_threshold_list]


class _CurveCollectionOriginal(_CurveCollection):
    def __init__(self, fc_path):
        _CurveCollection.__init__(self, fc_path, "Original")

        for a in self._by_threshold_list:
            a.method = self.method
            a.path = fc_path


class _CurveCollectionBezier(_CurveCollection):
    def __init__(self, fc_path):
        _CurveCollection.__init__(self, fc_path, 'Bezier')

        nm = fc_path[fc_path.find('bezier') + 7:]
        deviation_num = float(re.search('[0-9]{2}_[0-9]', nm).group().replace('_', '.'))
        self.deviation = "{0} Meters".format(deviation_num)

        for a in self._by_threshold_list:
            a.method = self.method
            a.deviation = self.deviation
            a.path = fc_path


class _CurveCollectionPaek(_CurveCollection):
    def __init__(self, fc_path):
        _CurveCollection.__init__(self, fc_path, 'Paek')

        nm = fc_path[fc_path.find('paek') + 5:]
        tolerance_num = int(re.search('[0-9]{3}', nm).group().replace('_', '.'))
        self.tolerance = "{0} Meters".format(tolerance_num)

        for a in self._by_threshold_list:
            a.method = self.method
            a.tolerance = self.tolerance
            a.path = fc_path


class _Score:

    def __init__(self):
        pass


class GroundTruthCollection:

    def __init__(self, ground_truth):

        self.segment_id_dict = defaultdict(list)

        search = arcpy.SearchCursor(ground_truth)

        for row in search:
            self.segment_id_dict[str(row.getValue(outFc.SEGMENT_ID))].append(
                CurveSegment(
                    row.getValue(outFc.SEGMENT_ID),
                    row.getValue(outFc.START_M),
                    row.getValue(outFc.END_M)
                )
            )

        for k in self.segment_id_dict.keys():
            self.segment_id_dict[k].sort(key=lambda x: x.start_m)

    def get_by_key(self, k):
        """

        :param k:
        :type k:
        :return:
        :rtype: list[CurveSegment]
        """

        if k not in self.segment_id_dict.keys():
            return []

        return self.segment_id_dict[k]


class AllCurves:

    def __init__(self, curve_wksp, debug):

        arcpy.env.workspace = curve_wksp

        self.compare_list = []
        """
        :type: list[_CurveCollection]
        """

        counter = 0

        for fc in arcpy.ListFeatureClasses():

            if counter > 2 and debug:
                break

            p = os.path.join(curve_wksp, fc)

            if fc.lower().find('bezier') > -1:
                self.compare_list.append(_CurveCollectionBezier(p))
            elif fc.lower().find('paek') > -1:
                self.compare_list.append(_CurveCollectionPaek(p))
            else:
                self.compare_list.append(_CurveCollectionOriginal(p))

            counter += 1


class Calibrate:

    def __init__(self, ground_truth, curve_workspace, debug=False):
        self._gt = GroundTruthCollection(ground_truth)
        self._c = AllCurves(curve_workspace, debug)

        for j in self._c.compare_list:
            for k, v in j.by_threshold_dict.items():
                match_miss_over(self._gt, v)

        self._all_by_thresh = []
        """
        :type: list[_ByThreshold]
        """

        for j in self._c.compare_list:
            self._all_by_thresh.extend(j.by_threshold_list)

    @property
    def all_by_thresh(self):
        """

        :return:
        :rtype: list[_ByThreshold]
        """
        self._all_by_thresh.sort(key=lambda x: x.score, reverse=True)
        return [t for t in self._all_by_thresh]


if __name__ == '__main__':
    cal = Calibrate(r'C:\Users\glenn\Desktop\curves\iowa.gdb\primary_dissolve_gt_prep17', r'C:\tmp\temp_curves.gdb')


