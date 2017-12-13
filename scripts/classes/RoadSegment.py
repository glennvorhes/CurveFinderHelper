import re
from scripts.classes.MiniSegment import MiniSegment
from scripts.classes.Curve import Curve
from scripts.constants import SideOfLine, BasicCurveType, IdCurveConstants, CurveType


class RoadSegment:
    def __init__(self, segment_id, road_name, feat, units):
        """

        :param segment_id:
        :type segment_id: int
        :param road_name:
        :type road_name: str
        :param feat:
        :type feat: scripts.arcpy_geom.features.LineString
        :param units:
        :type units: str
        """

        self.segment_id = segment_id
        self.road_name = road_name
        self._dDistance = 183 if units == 'meter' else 600

        self.mini_segment_list = []
        """
        :type: list[MiniSegment]
        """

        self.all_curve_in_the_poly = []
        """
        :type: list[Curve]
        """

        self.feat = feat
        """
        :type: scripts.arcpy_geom.features.LineString
        """
        # self.feat.add_m()

        for i in range(0, len(self.feat.vertices) - 1):
            self.mini_segment_list.append(
                MiniSegment(
                    self.feat.vertices[i],
                    self.feat.vertices[i + 1]
                )
            )

        for i in range(0, len(self.mini_segment_list)):
            if i == 0:
                self.mini_segment_list[i].defl_angle = 0.1
                self.mini_segment_list[i].side = SideOfLine.ONTHELINE
                self.mini_segment_list[i].set_pre_seg(None)
            else:
                # print(self.mini_segment_list[i - 1])
                self.mini_segment_list[i].set_pre_seg(self.mini_segment_list[i - 1])

            if i < len(self.mini_segment_list) - 1:
                self.mini_segment_list[i].set_next_seg(self.mini_segment_list[i + 1])

    def _return_verts(self, start_ind, end_ind):
        # print(start_ind, end_ind)
        v = []
        for i in range(start_ind, end_ind):
            v.append(self.mini_segment_list[i].start_pnt)

        v.append(self.mini_segment_list[end_ind - 1].end_pnt)

        return v

    def process_mini_segments(self, threshold):

        # Some global variables in one polyline

        official_n = ""
        tas_link_id = -1
        trn_link_id = -1
        trn_node_f = -1
        trn_node_t = -1
        tre_sys = -1
        vers_date = -1

        cumul_tan_len = 0  # cumulative tangent length between curves
        prev_curve_type = BasicCurveType.TG
        prev_curve_dir = SideOfLine.ONTHELINE
        # next_curve_basic_type = BasicCurveType.TG

        index = -1
        while index < len(self.mini_segment_list):
            index += 1

            try:
                seg = self.mini_segment_list[index]
            except IndexError:
                break

            if index < len(self.mini_segment_list) - 1 and \
                    seg.curve_type == BasicCurveType.HAP and \
                    seg.next_seg.curve_type == BasicCurveType.HAP:
                p_curve = Curve(threshold)
                # pCurve.ID = indexCurveID + +
                p_curve.Type = CurveType.HAP
                # pCurve.Length = self.mini_segment_list[index].length + self.mini_segment_list[index].next_seg.length
                p_curve.Dir = self.mini_segment_list[index].next_seg.side
                p_curve.CentralAngle = 180 - self.mini_segment_list[index].next_seg.defl_angle
                p_curve.Radius = -1

                p_curve.extend_vertices(self._return_verts(index, index + 2))

                p_curve.RouteDir = ""  # current street direction N/S/E/W
                p_curve.RouteFullName = ""

                p_curve.OfficialN = official_n
                p_curve.TASlinkID = tas_link_id
                p_curve.TRNLinkID = trn_link_id
                p_curve.TRNNode_F = trn_node_f
                p_curve.TRNNote_T = trn_node_t
                p_curve.RTESys = tre_sys
                p_curve.Vers_date = vers_date

                #  add the curve
                self.all_curve_in_the_poly.append(p_curve)

                cumul_tan_len = 0  # reset tangent length
                prev_curve_type = BasicCurveType.HAP
                prev_curve_dir = p_curve.Dir

            if seg.curve_type == BasicCurveType.TG or seg.curve_type == BasicCurveType.RTG:
                cumul_tan_len += seg.length  # add tangent length

            elif seg.curve_type in [BasicCurveType.CURV, BasicCurveType.CONSECUCOMPCURV, BasicCurveType.REVSCURV]:
                for j in range(index, len(self.mini_segment_list)):
                    if self.mini_segment_list[j].curve_type != self.mini_segment_list[index].curve_type:
                        break

                eng_tang_len = 0

                for k in range(j, len(self.mini_segment_list)):
                    if self.mini_segment_list[k].curve_type in [BasicCurveType.TG, BasicCurveType.RTG]:
                        eng_tang_len += self.mini_segment_list[k].length
                    else:
                        break

                if k == len(self.mini_segment_list):  # rest are all tangent
                    next_curve_basic_type = BasicCurveType.TG
                    next_curve_dir = SideOfLine.ONTHELINE
                else:  # more curves
                    next_curve_basic_type = self.mini_segment_list[k].curve_type
                    next_curve_dir = self.mini_segment_list[k].side

                # judge the transition
                b_begin_ts = False
                b_end_ts = False
                number_of_seg = j - index

                if number_of_seg >= 3:  # start consideration of transition

                    #  judge the beginning seg whether it is a transition
                    if self.mini_segment_list[index + 1].defl_angle >= IdCurveConstants.dAngleTSPreAngleLowerLimit and \
                                    self.mini_segment_list[index].defl_angle < \
                                    IdCurveConstants.dPctTSThreshold * self.mini_segment_list[
                                    index + 1].defl_angle and \
                                    self.mini_segment_list[index].defl_angle < IdCurveConstants.dAngleTSUpperLimit:
                        b_begin_ts = True
                        p_curve = Curve(threshold)

                        p_curve.Type = CurveType.TS

                        p_curve.extend_vertices(self._return_verts(index, index + 1))

                        p_curve.RouteDir = ""  # current street direction N/S/E/W
                        p_curve.RouteFullName = ""
                        p_curve.OfficialN = official_n
                        p_curve.TASlinkID = tas_link_id
                        p_curve.TRNLinkID = trn_link_id
                        p_curve.TRNNode_F = trn_node_f
                        p_curve.TRNNote_T = trn_node_t
                        p_curve.RTESys = tre_sys
                        p_curve.Vers_date = vers_date
                        self.all_curve_in_the_poly.append(p_curve)

                    # judge the ending seg whether it is a transition
                    if self.mini_segment_list[j - 1].defl_angle >= IdCurveConstants.dAngleTSPreAngleLowerLimit and \
                            self.mini_segment_list[j].defl_angle < IdCurveConstants.dPctTSThreshold * \
                            self.mini_segment_list[j - 1].defl_angle \
                            and self.mini_segment_list[j].defl_angle < IdCurveConstants.dAngleTSUpperLimit:
                        b_end_ts = True
                        p_curve = Curve(threshold)
                        p_curve.Type = CurveType.TS
                        # p_curve.Length = self.mini_segment_list[j - 1].length

                        p_curve.extend_vertices(self._return_verts(j - 1, j))

                        p_curve.RouteDir = ""  # current street direction N/S/E/W
                        p_curve.RouteFullName = ""
                        p_curve.OfficialN = official_n
                        p_curve.TASlinkID = tas_link_id
                        p_curve.TRNLinkID = trn_link_id
                        p_curve.TRNNode_F = trn_node_f
                        p_curve.TRNNote_T = trn_node_t
                        p_curve.RTESys = tre_sys
                        p_curve.Vers_date = vers_date
                        self.all_curve_in_the_poly.append(p_curve)

                p_curve = Curve(threshold)

                if self.mini_segment_list[index].curve_type == BasicCurveType.CONSECUCOMPCURV:
                    p_curve.Dir = self.mini_segment_list[index + 1].side
                else:
                    p_curve.Dir = self.mini_segment_list[index].side

                # determine Curve Type
                if eng_tang_len > self._dDistance and cumul_tan_len > self._dDistance:  # both 183m tangents
                    p_curve.Type = CurveType.IC
                elif cumul_tan_len <= self._dDistance < eng_tang_len:  # ending 183 tangent
                    if prev_curve_type == BasicCurveType.TG:  # first curve in the polyline
                        p_curve.Type = CurveType.IC
                    else:
                        if prev_curve_type == BasicCurveType.HAP:
                            #  pCurve.Type = CurveType.CC  #  this is a compound curve
                            p_curve.Type = CurveType.IC  # 10/08/2013
                        else:
                            if p_curve.Dir == prev_curve_dir:
                                p_curve.Type = CurveType.CC  # this is a compound curve
                            else:
                                if self.mini_segment_list[index].curve_type == BasicCurveType.CONSECUCOMPCURV:
                                    p_curve.Type = CurveType.CC
                                else:
                                    p_curve.Type = CurveType.RC
                elif cumul_tan_len > self._dDistance >= eng_tang_len:  # beginning 183 tangent
                    if next_curve_basic_type == BasicCurveType.HAP:
                        #  pCurve.Type = CurveType.CC  #  this is a compound curve
                        p_curve.Type = CurveType.IC  # 10/08/2013
                    elif next_curve_basic_type == BasicCurveType.TG or next_curve_basic_type == BasicCurveType.RTG:
                        p_curve.Type = CurveType.IC  # 10/08/2013
                    else:  # right side is not tangent
                        if p_curve.Dir == next_curve_dir:
                            p_curve.Type = CurveType.CC  # this is a compound curve
                        else:
                            if next_curve_basic_type == BasicCurveType.CONSECUCOMPCURV:
                                p_curve.Type = CurveType.CC  # this is a compound curve
                            else:
                                p_curve.Type = CurveType.RC
                elif cumul_tan_len <= self._dDistance and eng_tang_len <= self._dDistance:
                    # no 183 tangent on both sides
                    if next_curve_basic_type == BasicCurveType.HAP and prev_curve_type == BasicCurveType.HAP:
                        #  pCurve.Type = CurveType.CC  #  this is a compound curve
                        p_curve.Type = CurveType.IC  # 10/08/2013
                    elif next_curve_basic_type == BasicCurveType.HAP:  # immediate hap on right
                        if prev_curve_type == BasicCurveType.TG:  # first curve in the polyline
                            p_curve.Type = CurveType.IC  # 10/08/2013
                        else:
                            if p_curve.Dir == prev_curve_dir:
                                p_curve.Type = CurveType.CC  # this is a compound curve
                            else:
                                if self.mini_segment_list[index].curve_type == BasicCurveType.CONSECUCOMPCURV:
                                    p_curve.Type = CurveType.CC
                                else:
                                    p_curve.Type = CurveType.RC
                    elif prev_curve_type == BasicCurveType.HAP:  # immediate hap on left
                        if next_curve_basic_type == BasicCurveType.TG or next_curve_basic_type == BasicCurveType.RTG:
                            p_curve.Type = CurveType.IC  # 10/08/2013
                        else:
                            if p_curve.Dir == next_curve_dir:
                                p_curve.Type = CurveType.CC  # this is a compound curve
                            else:
                                if next_curve_basic_type == BasicCurveType.CONSECUCOMPCURV:
                                    p_curve.Type = CurveType.CC  # this is a compound curve
                                else:
                                    p_curve.Type = CurveType.RC
                    else:  # not immediate hap on left and right
                        if next_curve_basic_type == BasicCurveType.TG or next_curve_basic_type == BasicCurveType.RTG:
                            # rest are all tangennts
                            if prev_curve_type == BasicCurveType.TG:  # first curve
                                p_curve.Type = CurveType.IC
                            else:
                                if p_curve.Dir == prev_curve_dir:
                                    p_curve.Type = CurveType.CC  # this is a compound curve
                                else:
                                    if self.mini_segment_list[index].curve_type == BasicCurveType.CONSECUCOMPCURV:
                                        p_curve.Type = CurveType.CC
                                    else:
                                        p_curve.Type = CurveType.RC
                        else:
                            if prev_curve_type == BasicCurveType.TG:  # first curve
                                if p_curve.Dir == next_curve_dir:
                                    p_curve.Type = CurveType.CC  # this is a compound curve
                                else:
                                    if next_curve_basic_type == BasicCurveType.CONSECUCOMPCURV:
                                        p_curve.Type = CurveType.CC  # this is a compound curve
                                    else:
                                        p_curve.Type = CurveType.RC
                            else:
                                if p_curve.Dir == prev_curve_dir and p_curve.Dir == next_curve_dir:
                                    p_curve.Type = CurveType.CC  # this is a compound curve
                                elif (p_curve.Dir == prev_curve_dir and p_curve.Dir != next_curve_dir) or (
                                        p_curve.Dir != prev_curve_dir and p_curve.Dir == next_curve_dir):
                                    p_curve.Type = CurveType.RC  # this is a reverse curve
                                elif p_curve.Dir != prev_curve_dir and p_curve.Dir != next_curve_dir:
                                    p_curve.Type = CurveType.RC  # this is a reverse curve

                # determine curve segments, curve length, central angle and radius
                # p_curve.Length = 0
                p_curve.CentralAngle = 0
                p_curve.numVertices = 0

                if b_begin_ts is False and b_end_ts is False:  # no transition
                    q = 0
                    for n in range(index, j):
                        p_curve.CentralAngle += self.mini_segment_list[n].defl_angle
                        q += 1

                    p_curve.extend_vertices(self._return_verts(index, j))
                    p_curve.CentralAngle += self.mini_segment_list[j].defl_angle
                    p_curve.has_transition = False

                elif b_begin_ts is True and b_end_ts is False:
                    q = 0
                    for n in range(index + 1, j):
                        p_curve.CentralAngle += self.mini_segment_list[n].defl_angle
                        q += 1

                    p_curve.extend_vertices(self._return_verts(index + 1, j))
                    p_curve.CentralAngle += self.mini_segment_list[j].defl_angle
                    p_curve.has_transition = True

                elif b_begin_ts is False and b_end_ts is True:
                    q = 0

                    for n in range(index, j - 1):
                        p_curve.CentralAngle += self.mini_segment_list[n].defl_angle
                        q += 1

                    p_curve.extend_vertices(self._return_verts(index, j - 1))
                    p_curve.CentralAngle += self.mini_segment_list[j - 1].defl_angle
                    p_curve.has_transition = True

                elif b_begin_ts is True and b_end_ts is True:
                    q = 0
                    for n in range(index + 1, j - 1):
                        # for int n = index + 1 n < j - 1 n++
                        # p_curve.Length += self.mini_segment_list[n].length
                        p_curve.CentralAngle += self.mini_segment_list[n].defl_angle
                        q += 1

                    p_curve.extend_vertices(self._return_verts(index + 1, j - 1))
                    p_curve.CentralAngle += self.mini_segment_list[j - 1].defl_angle
                    p_curve.has_transition = True

                p_curve.Radius = 180 * p_curve.Length / p_curve.CentralAngle / 3.1415926

                p_curve.OfficialN = official_n
                p_curve.TASlinkID = tas_link_id
                p_curve.TRNLinkID = trn_link_id
                p_curve.TRNNode_F = trn_node_f
                p_curve.TRNNote_T = trn_node_t
                p_curve.RTESys = tre_sys
                p_curve.Vers_date = vers_date

                self.all_curve_in_the_poly.append(p_curve)
                cumul_tan_len = 0  # reset tangent length
                prev_curve_dir = p_curve.Dir
                prev_curve_type = self.mini_segment_list[index].curve_type
                index = j - 1
                # jump to the next segment feature can be tangent or
                # curve or hap there will be a index++, so j-1 is used.

    def find_curves(self, threshold):

        for i in range(len(self.mini_segment_list)):
            self.mini_segment_list[i].set_seg_type(threshold)

        self.process_mini_segments(threshold)

        # for s in self.allCurveinthePoly:
        #     print(s.num_vertices)

        # print(self.allCurveinthePoly[4].coords)

        # for i in range(len(self.mini_segment_list)):
        #     print(i, self.mini_segment_list[i].curve_type)

        # print(len(self.allCurveinthePoly))


if __name__ == '__main__':
    oid_ = 171
    road_name_ = 'STATE OF IOWA, US 34 W'
    wkt_ = 'MULTILINESTRING ((370716.05219999701 112948.47929999977, 370755.75419999659 112944.66180000082, 370832.7480000034 112938.70870000124, 370884.73860000074 112937.51799999923, 370935.9355000034 112938.70870000124, 370959.11969999969 112939.13540000096, 370982.28170000017 112940.23719999939, 371005.40169999748 112942.01319999993, 371028.46019999683 112944.46189999953, 371051.43760000169 112947.58130000159, 371074.31440000236 112951.3685999997, 371097.07119999826 112955.82059999928, 371119.68860000372 112960.933699999, 371203.03239999712 112982.36490000039, 371316.9355000034 113013.71799999848, 371418.93240000308 113042.68989999965, 371486.00419999659 113063.3273999989, 371544.34489999712 113078.40870000049, 371616.97299999744 113094.28370000049, 371642.68829999864 113099.68800000101, 371668.54129999876 113104.3898999989, 371694.51269999892 113108.38589999825, 371720.58340000361 113111.67309999838, 371746.73390000314 113114.24909999967, 371772.94489999861 113116.11180000007, 371831.28549999744 113120.87429999933, 371886.84799999744 113124.04930000007, 371954.71360000223 113124.04930000007, 372123.78239999712 113125.23990000039, 372239.27300000191 113125.63679999858, 372413.10419999808 113127.621199999, 372484.54169999808 113127.621199999, 372599.63549999893 113127.22430000082, 372704.01359999925 113129.60550000146, 372892.92610000074 113130.79619999975, 372986.19169999659 113131.58989999816, 373086.20419999957 113130.39930000156, 373126.03750000149 113131.02169999853))'
    units_ = 'meter'

    segm = RoadSegment(oid_, road_name_, wkt_, units_)
    segm.find_curves(1.0)
