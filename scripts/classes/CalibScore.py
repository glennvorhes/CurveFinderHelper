from collections import defaultdict
# import arcpy

class _BaseSeg:

    def __init__(self, start, end):
        if start < end:
            self.start = start
            self.end = end
        else:
            self.start = end
            self.end = start

    @property
    def seg_length(self):
        return self.end - self.start


class _Gt(_BaseSeg):

    def __init__(self, start, end):
        _BaseSeg.__init__(self, start, end)

        self._matched_len = 0
        self._found = False

    def reset(self):
        self._matched_len = 0
        self._found = False

    def check_id_seg(self, i):
        """

        :param i: id segment
        :type i: _Id
        """

        if i.end < self.start or i.start > self.end:
            return
        # gt outside id curve
        elif self.start <= i.start and i.end <= self.end:
            self._matched_len += i.end - i.start
            i.over_len -= i.seg_length
        # id outside gt
        elif i.start < self.start and self.end < i.end:
            self._matched_len += self.seg_length
            i.over_len -= self.end - self.start
        # id segment overlaps start of gt
        elif i.start < self.start < i.end:
            self._matched_len += i.end - self.start
            i.over_len -= i.end - self.start
        # id segment overlaps end of gt
        elif i.start < self.end < i.end:
            self._matched_len += self.end - i.start
            i.over_len -= self.end - i.start
        else:
            return

        self._found = True
        i.gt_match = True

    @property
    def matched_len(self):
        return self._matched_len

    @property
    def missed_len(self):
        return self.seg_length - self.matched_len

    @property
    def found(self):
        return self._found


class _Id(_BaseSeg):
    def __init__(self, start, end):
        _BaseSeg.__init__(self, start, end)

        self.over_len = self.seg_length
        self.gt_match = False


class _CalibScoreRoute:

    def __init__(self):
        """

        :param id_seg_arr: identified curves
        :type id_seg_arr:
        :param gt_seg_arr: gt curves
        :type gt_seg_arr:
        """

        self._matched_len = 0
        self._missed_len = 0
        self._over_len = 0
        self._finalized = False
        self._total_id_len = 0
        self._id_gt_match_count = 0
        self._gt_found_count = 0

        self._total_gt_len = 0

        self._gt_list = []
        """
        @:type: list[_Gt]
        """

        self._id_list = []
        """
        @:type: list[_Id]
        """

        self._id_seg_arr = []
        self._gt_seg_arr = []

    def _finalize(self):

        for g in self._gt_list:
            for i in self._id_list:
                g.check_id_seg(i)

        for g in self._gt_list:
            self._matched_len += g.matched_len
            self._missed_len += g.missed_len
            self._gt_found_count += 1 if g.found else 0

        for i in self._id_list:
            self._over_len += i.over_len
            self._id_gt_match_count += 1 if i.gt_match else 0

        self._finalized = True

    def reset(self):
        self._matched_len = 0
        self._missed_len = 0
        self._over_len = 0
        self._finalized = False
        self._total_id_len = 0
        self._id_list = []
        self._gt_found_count = 0
        self._id_gt_match_count = 0

        for g in self._gt_list:
            g.reset()

    def add_id(self, start, end):
        _id = _Id(start, end)
        self._id_list.append(_id)
        self._total_id_len += _id.seg_length

    def add_gt(self, start, end):
        gt = _Gt(start, end)
        self._gt_list.append(gt)
        self._total_gt_len += gt.seg_length

    def _check_final(self):
        if not self._finalized:
            self._finalize()

    @property
    def id_seg_count(self):
        self._check_final()
        return len(self._id_list)

    @property
    def total_id_len(self):
        self._check_final()
        return float(self._total_id_len)

    @property
    def gt_id_match_count(self):
        self._check_final()
        return self._id_gt_match_count

    @property
    def total_gt_len(self):
        self._check_final()
        return float(self._total_gt_len)

    @property
    def matched_len(self):
        self._check_final()
        return float(self._matched_len)

    @property
    def missed_len(self):
        self._check_final()
        return float(self._missed_len)

    @property
    def over_len(self):
        self._check_final()
        return float(self._over_len)

    @property
    def gt_count(self):
        return len(self._gt_list)

    @property
    def gt_found_count(self):
        self._check_final()
        return self._gt_found_count


class CalibScore:

    # def __init__(self, id_seg_arr, gt_seg_arr):
    def __init__(self):
        """

        :param id_seg_arr: identified curves
        :type id_seg_arr:
        :param gt_seg_arr: gt curves
        :type gt_seg_arr:
        """

        self._matched_len = 0
        self._missed_len = 0
        self._over_len = 0
        self._finalized = False

        self._total_gt_len = 0
        self._total_id_len = 0

        self._total_gt_count = 0
        self._total_gt_found_count = 0

        self._total_id_count = 0
        self._total_id_match_count = 0

        self._route_calib_dict = defaultdict(_CalibScoreRoute)

    def add_id(self, route, start, end):
        if isinstance(route, int):
            route = str(route)

        self._route_calib_dict[route].add_id(start, end)

    def add_gt(self, route, start, end):
        if isinstance(route, int):
            route = str(route)

        self._route_calib_dict[route].add_gt(start, end)

    def _finalize(self):

        for itm in self._route_calib_dict.values():
            """
            :type: _CalibScoreRoute
            """

            self._total_gt_len += itm.total_gt_len
            self._total_id_len += itm.total_id_len
            self._matched_len += itm.matched_len
            self._missed_len += itm.missed_len
            self._over_len += itm.over_len
            self._total_gt_count += itm.gt_count
            self._total_gt_found_count += itm.gt_found_count
            self._total_id_count += itm.id_seg_count
            self._total_id_match_count += itm.gt_id_match_count

        self._finalized = True

    def reset(self):
        self._matched_len = 0
        self._missed_len = 0
        self._over_len = 0
        self._finalized = False

        self._total_gt_len = 0
        self._total_id_len = 0

        self._total_gt_count = 0
        self._total_gt_found_count = 0

        self._total_id_count = 0
        self._total_id_match_count = 0

        for itm in self._route_calib_dict.values():
            itm.reset()

    def _check_final(self):
        if not self._finalized:
            self._finalize()

    @property
    def total_gt_len(self):
        self._check_final()
        return float(self._total_gt_len)

    @property
    def matched_pcnt(self):
        self._check_final()
        if self.total_gt_len == 0:
            return 0
        return float(self._matched_len) / self.total_gt_len

    @property
    def missed_pcnt(self):
        self._check_final()
        if self.total_gt_len == 0:
            return 0
        return float(self._missed_len) / self.total_gt_len

    @property
    def over_pcnt(self):
        self._check_final()
        if self.total_gt_len == 0:
            return 0
        return float(self._over_len) / self.total_gt_len

    @property
    def gt_count(self):
        self._check_final()
        return self._total_gt_count

    @property
    def gt_found_count(self):
        self._check_final()
        return self._total_gt_found_count

    @property
    def id_count(self):
        self._check_final()
        return self._total_id_count

    @property
    def id_match_count(self):
        self._check_final()
        return self._total_id_match_count

    @property
    def id_no_gt_count(self):
        self._check_final()
        return self.id_count - self.id_match_count

    def score(self, match_weight, miss_weight, over_weight):
        """
        matched * 10 - missed * 5 - over * 2

        :return:
        :rtype:
        """
        return match_weight * self.matched_pcnt - miss_weight * self.missed_pcnt - over_weight * self.over_pcnt
