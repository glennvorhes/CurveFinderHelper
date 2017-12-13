from scripts.arcpy_geom.Vertex import Vertex
from scripts.classes.StraightLine import StraightLine
import math
from scripts.constants import SideOfLine, BasicCurveType, AboveBelowLine, IdCurveConstants

_allow = [BasicCurveType.TG, BasicCurveType.HAP, BasicCurveType.RTG,
          BasicCurveType.CONSECUCOMPCURV, BasicCurveType.REVSCURV, BasicCurveType.CURV]


def _point_on_side_of_a_line(pnt_a, pnt_b, pnt_c):
    """
    
    :param pnt_a:
    :type pnt_a: Vertex
    :param pnt_b:
    :type pnt_b: Vertex
    :param pnt_c:
    :type pnt_c: Vertex
    :return: 
    :rtype: 
    """
    the_line = StraightLine(pnt_a, pnt_b)
    loc_of_point = the_line.point_above_or_below_the_line(pnt_c)

    if pnt_b.x > pnt_a.x:  # the line goes to right (Xd > Xc)

        if loc_of_point == AboveBelowLine.ABOVE:
            the_result = SideOfLine.LEFT
        elif loc_of_point == AboveBelowLine.BELOW:
            the_result = SideOfLine.RIGHT
        else:
            the_result = SideOfLine.ONTHELINE
    elif pnt_b.x < pnt_a.x:  # the Line goes to left (Xd < Xc)
        if loc_of_point == AboveBelowLine.ABOVE:
            the_result = SideOfLine.RIGHT
        elif loc_of_point == AboveBelowLine.BELOW:
            the_result = SideOfLine.LEFT
        else:
            the_result = SideOfLine.ONTHELINE
    else:  # Xd = Xc
        if pnt_b.y > pnt_a.y:  # the line goes up(Yd > Yc)
            if pnt_c.x > pnt_b.x:
                the_result = SideOfLine.RIGHT
            elif pnt_c.x < pnt_b.x:
                the_result = SideOfLine.LEFT
            else:
                the_result = SideOfLine.ONTHELINE
        elif pnt_b.y < pnt_a.y:  # the line goes down (Yd < Yc)
            if pnt_c.x > pnt_b.x:
                the_result = SideOfLine.LEFT
            elif pnt_c.x < pnt_b.x:
                the_result = SideOfLine.RIGHT
            else:
                the_result = SideOfLine.ONTHELINE
        else:  # on the line
            the_result = SideOfLine.ONTHELINE

    return the_result


def _get_angle_between_two_lines(pnt_a, pnt_b, pnt_c):
    """

    :param pnt_a:
    :type pnt_a: Vertex
    :param pnt_b:
    :type pnt_b: Vertex
    :param pnt_c:
    :type pnt_c: Vertex
    :return: 
    :rtype: 
    """
    u_x = pnt_b.x - pnt_a.x
    u_y = pnt_b.y - pnt_a.y
    v_x = pnt_c.x - pnt_b.x
    v_y = pnt_c.y - pnt_b.y

    abs_u = math.sqrt(math.pow(u_x, 2) + math.pow(u_y, 2))
    abs_v = math.sqrt(math.pow(v_x, 2) + math.pow(v_y, 2))

    cos_val = (u_x * v_x + u_y * v_y) / (abs_u * abs_v)
    # print(cos_val)
    # print(type(cos_val))
    try:
        arcos_val = math.acos(cos_val)
    except ValueError:
        arcos_val = 0

    ret_val = arcos_val / math.pi * 180
    # print(ret_val)

    return ret_val


class MiniSegment:
    def __init__(self, start_pnt, end_pnt):
        """

        :param start_pnt:
        :type start_pnt: Vertex
        :param end_pnt:
        :type end_pnt: Vertex
        """
        self.start_pnt = start_pnt
        self.end_pnt = end_pnt
        self._length = end_pnt.m - start_pnt.m

        self._pre_seg = None
        """
        :type: MiniSegment
        """

        self._next_seg = None
        """
        :type: MiniSegment
        """

        self.defl_angle = 0
        self.side = SideOfLine.ONTHELINE
        self._curve_type = None
        self.curve_type = BasicCurveType.TG

    @property
    def pre_seg(self):
        return self._pre_seg

    @property
    def next_seg(self):
        return self._next_seg

    def set_next_seg(self, next_seg):
        self._next_seg = next_seg

    def set_pre_seg(self, seg):
        """

        :param seg:
        :type seg: MiniSegment|None
        :return:
        :rtype:
        """
        self._pre_seg = seg
        """
        :type: MiniSegment
        """

        if seg is None:
            self.defl_angle = 0.1
            self.side = SideOfLine.ONTHELINE
        else:
            pt_a = self._pre_seg.start_pnt
            pt_b = self.start_pnt
            pt_c = self.end_pnt

            self.defl_angle = _get_angle_between_two_lines(pt_a, pt_b, pt_c)
            self.side = _point_on_side_of_a_line(pt_a, pt_b, pt_c)

    @property
    def length(self):
        return self._length

    @property
    def curve_type(self):
        return self.curve_type

    @curve_type.setter
    def curve_type(self, curve_type):
        assert curve_type in _allow
        self._curve_type = curve_type

    def set_seg_type(self, angle_threshold):
        self.curve_type = BasicCurveType.TG

        if self.pre_seg is None:
            self.curve_type = BasicCurveType.TG
        elif self.next_seg is None:
            if self.pre_seg.curve_type == BasicCurveType.TG or self.pre_seg.curve_type == BasicCurveType.RTG:
                # the one before the last segment is a tangent
                if self.defl_angle >= angle_threshold:
                    if self.defl_angle >= IdCurveConstants.dHAPThreshold:
                        # in this case, it is a horizontal angle point
                        self.curve_type = BasicCurveType.HAP  # current segment is one part of the HAP
                        self.pre_seg.curve_type = BasicCurveType.HAP
                        # the segment before current segment becomes the other part of HAP
                    else:
                        self.curve_type = self.pre_seg.curve_type
                else:  # less than the angle threshold
                    # still considered as a tangent
                    self.curve_type = self.pre_seg.curve_type
            elif self.pre_seg.curve_type == BasicCurveType.CURV or \
                    self.pre_seg.curve_type == BasicCurveType.REVSCURV or \
                    self.pre_seg.curve_type == BasicCurveType.CONSECUCOMPCURV:
                # the one before the last segment is a curve
                if self.defl_angle >= angle_threshold:  # end the curve by a tangent
                    if self.side == self.pre_seg.side:  # same side
                        self.curve_type = BasicCurveType.TG
                    else:  # different side
                        self.curve_type = BasicCurveType.RTG
                else:  # less than the angle threshold terminate the curve.
                    # will not enter this part
                    self.curve_type = BasicCurveType.TG
                    self.pre_seg.curve_type = BasicCurveType.TG
            elif self.pre_seg.curve_type == BasicCurveType.HAP:
                if self.defl_angle >= angle_threshold:
                    if self.side == self.pre_seg.side:  # same side
                        # impossible
                        self.curve_type = BasicCurveType.TG
                        self.pre_seg.curve_type = BasicCurveType.TG
                    else:  # different side
                        if self.defl_angle >= IdCurveConstants.dHAPThreshold:
                            self.curve_type = BasicCurveType.HAP
                            # becomes a non-standard tangent, which cannot be used to calculate the radius
                        else:
                            self.curve_type = BasicCurveType.TG  # is a tangent
                else:  # less than the angle threshold terminate the curve.
                    self.curve_type = BasicCurveType.TG  # is a tangent
        else:
            if self.defl_angle >= angle_threshold:
                if self.pre_seg.curve_type == BasicCurveType.TG or self.pre_seg.curve_type == BasicCurveType.RTG:
                    # previous seg is a tangent
                    # beginning of a curve but curve type unknown
                    # can be a reverse horizontal angle point, a tangent, or a curve
                    if self.next_seg.defl_angle >= angle_threshold:
                        # next segment has a deflection angle greater than the threshold
                        if self.next_seg.side == self.side:  # next segment is on the same side
                            self.curve_type = BasicCurveType.CURV  # current segment is a part of curve
                        else:  # next segment is on the reverse side
                            if self.defl_angle >= IdCurveConstants.dHAPThreshold:
                                self.curve_type = BasicCurveType.HAP  # current segment is horizontal angle point
                                self.pre_seg.curve_type = BasicCurveType.HAP
                                # the one before current segment is horizontal angle point
                            else:
                                self.curve_type = self.pre_seg.curve_type  # keep as tang or rtang
                    else:  # next segment does not have a deflection angle greater than the threshold
                        if self.defl_angle >= IdCurveConstants.dHAPThreshold:
                            self.curve_type = BasicCurveType.HAP  # current segment is horizontal angle point
                            self.pre_seg.curve_type = BasicCurveType.HAP
                            # the one before current segment is horizontal angle point
                        else:
                            self.curve_type = self.pre_seg.curve_type  # keep as tang or rtang
                elif self.pre_seg.curve_type == BasicCurveType.HAP:  # previous seg is a horizontal angle point segment
                    if self.side != self.pre_seg.side:  # reverse side
                        # can be a reverse horizontal angle point, a tangent, or a curve
                        if self.next_seg.defl_angle >= angle_threshold:
                            # next segment has a deflection angle greater than the threshold
                            if self.next_seg.side == self.side:  # next segment is on the same side
                                self.curve_type = BasicCurveType.CURV  # current segment is a part of curve
                            else:  # next segment is on the reverse side
                                if self.defl_angle >= IdCurveConstants.dHAPThreshold:
                                    self.curve_type = BasicCurveType.HAP  # current segment is horizontal angle point
                                else:
                                    self.curve_type = BasicCurveType.TG
                        else:  # next segment does not have a deflection angle greater than the threshold
                            if self.defl_angle >= IdCurveConstants.dHAPThreshold:
                                self.curve_type = BasicCurveType.HAP  # current segment is horizontal angle point
                            else:
                                self.curve_type = BasicCurveType.TG
                    else:  # same side
                        # zl2015
                        # can be a reverse horizontal angle point, a tangent, or a curve
                        if self.next_seg.defl_angle >= angle_threshold:
                            # next segment has a deflection angle greather than the threshold
                            if self.next_seg.side == self.side:  # next segment is on the same side
                                self.curve_type = BasicCurveType.CURV  # current segment is a part of curve
                            else:  # next segment is on the reverse side
                                if self.defl_angle >= IdCurveConstants.dHAPThreshold:
                                    self.curve_type = BasicCurveType.HAP  # current segment is horizontal angle point
                                else:
                                    self.curve_type = BasicCurveType.TG
                        else:  # next segment does not have a deflection angle greater than the threshold
                            if self.defl_angle >= IdCurveConstants.dHAPThreshold:
                                self.curve_type = BasicCurveType.HAP  # current segment is horizontal angle point
                            else:
                                self.curve_type = BasicCurveType.TG
                elif self.pre_seg.curve_type == BasicCurveType.CURV or \
                        self.pre_seg.curve_type == BasicCurveType.REVSCURV or \
                        self.pre_seg.curve_type == BasicCurveType.CONSECUCOMPCURV:
                    # previous seg is a curve seg

                    if self.side == self.pre_seg.side:  # same side
                        # zl2015
                        if self.length >= self.pre_seg.length * IdCurveConstants.dMultipLenThreshold:
                            # if current seg is much longer than the previous seg
                            self.curve_type = BasicCurveType.TG  # current segment is considered a tangent same side
                            # end zl2015
                        else:
                            # zl2015
                            if self.defl_angle >= IdCurveConstants.dHAPAngleinCurve:
                                # angle great than intersection angle
                                self.curve_type = BasicCurveType.HAP
                                self.pre_seg.curve_type = BasicCurveType.HAP
                                # end zl2015
                            else:
                                # can be a reverse horizontal a tangent, a reverse tangent, or a curve
                                if self.next_seg.defl_angle >= angle_threshold:
                                    # next segment has a deflection angle greather than the threshold
                                    if self.next_seg.side == self.side:  # next segment is on the same side
                                        # zl2015
                                        if self.pre_seg.length >= self.length * IdCurveConstants.dMultipLenThreshold:
                                            # if the previous seg in the curve is much longer than the current seg
                                            self.pre_seg.curve_type = BasicCurveType.TG  # previous segment is a tangent
                                            self.curve_type = BasicCurveType.CURV
                                            # current segment is the start of of curve
                                            # end zl2015
                                        else:
                                            self.curve_type = self.pre_seg.curve_type
                                            # current segment is a part of curve
                                    else:  # next segment is on the reverse side
                                        if self.next_seg.next_seg is not None:  # last seg
                                            if self.next_seg.next_seg.defl_angle >= angle_threshold:
                                                # next next segment has a deflection angle greather than the threshold
                                                self.curve_type = self.pre_seg.curve_type
                                                # current segment is the same type as the previous segment
                                            else:  # next next get is tangent
                                                self.curve_type = BasicCurveType.RTG
                                        else:
                                            self.curve_type = BasicCurveType.RTG
                                else:  # next segment does not have a deflection angle greater than the threshold
                                    self.curve_type = BasicCurveType.TG
                    else:  # reverse side
                        # zl2015
                        if self.defl_angle >= IdCurveConstants.dHAPAngleinCurve:  # angle great than intersection angle
                            self.curve_type = BasicCurveType.HAP
                            self.pre_seg.curve_type = BasicCurveType.HAP
                            # end zl2015
                        else:
                            # can be a reverse horizontal a tangent, a reverse tangent, or a curve
                            if self.next_seg.defl_angle >= angle_threshold:
                                # next segment has a deflection angle greater than the threshold
                                if self.next_seg.side == self.side:  # next segment is on the same side
                                    # reverse curve
                                    if self.pre_seg.curve_type == BasicCurveType.CURV:  # if previous seg is a curve
                                        self.curve_type = BasicCurveType.REVSCURV
                                        # current segment is a part of reverse curve
                                    elif self.pre_seg.curve_type == BasicCurveType.CONSECUCOMPCURV:
                                        self.curve_type = BasicCurveType.CONSECUCOMPCURV
                                        # current segment is a part of reverse curve
                                    elif self.pre_seg.curve_type == BasicCurveType.REVSCURV:
                                        # if previous seg is a reverse curve
                                        self.curve_type = BasicCurveType.CURV
                                        # current segment is a part of reverse curve
                                else:  # next segment is on the reverse side
                                    if self.next_seg.next_seg is None:
                                        # current seg is the second last seg in the polyline
                                        if self.defl_angle >= IdCurveConstants.dHAPThreshold:
                                            self.curve_type = BasicCurveType.HAP
                                            # current segment is horizontal angle point
                                        else:
                                            self.curve_type = BasicCurveType.TG
                                    else:  # there has at least two segs before the polyline ends
                                        if self.next_seg.next_seg.defl_angle >= angle_threshold:
                                            # next next segment has a deflection angle greather than the threshold
                                            if self.next_seg.next_seg.side == self.next_seg.side:
                                                # next next segment is on the same side
                                                self.curve_type = BasicCurveType.CONSECUCOMPCURV
                                                # current segment is horizontal angle point
                                            else:  # next next segment is on the reverse side
                                                if self.defl_angle >= IdCurveConstants.dHAPThreshold:
                                                    self.curve_type = BasicCurveType.HAP
                                                    # current segment is horizontal angle point
                                                else:
                                                    self.curve_type = BasicCurveType.TG
                                        else:
                                            if self.defl_angle >= IdCurveConstants.dHAPThreshold:
                                                self.curve_type = BasicCurveType.HAP
                                                # current segment is horizontal angle point
                                            else:
                                                self.curve_type = BasicCurveType.TG
                            else:  # next segment does not have a deflection angle greather than the threshold
                                self.curve_type = BasicCurveType.RTG
            else:  # less than the threshold
                # becomes a tangent, previous seg must already a tangent or reverse tangent
                self.curve_type = BasicCurveType.TG  # becomes a tangent

            # artificial intelligence part
            try:
                if self.pre_seg.pre_seg.curve_type in \
                        [BasicCurveType.CURV, BasicCurveType.CONSECUCOMPCURV, BasicCurveType.REVSCURV] and \
                        self.pre_seg.curve_type in [BasicCurveType.TG, BasicCurveType.RTG] and \
                        self.curve_type in [BasicCurveType.TG, BasicCurveType.RTG]:
                    # curr, prev are tg, and prev prev is a curve
                    # potential issues on tangent direction need to be fixed
                    if self.next_seg.side == self.pre_seg.pre_seg.side and self.next_seg.defl_angle >= angle_threshold:
                        # next segment is a curve set and is on the same direction of the prepare segment curve
                        if self.pre_seg.length / self.pre_seg.pre_seg.length < \
                                IdCurveConstants.dMultipLenThreshold and \
                                self.length / self.pre_seg.pre_seg.length < \
                                IdCurveConstants.dMultipLenThreshold:
                            self.curve_type = self.pre_seg.pre_seg.curve_type
                            self.pre_seg.curve_type = self.pre_seg.pre_seg.curve_type
                            self.side = self.pre_seg.pre_seg.side
                            self.pre_seg.side = self.pre_seg.pre_seg.side
            except AttributeError:
                pass

            try:
                if self.pre_seg.pre_seg.pre_seg.curve_type in \
                        [BasicCurveType.CURV, BasicCurveType.CONSECUCOMPCURV, BasicCurveType.REVSCURV] and \
                        self.pre_seg.pre_seg.curve_type in [BasicCurveType.TG, BasicCurveType.RTG] and \
                        self.pre_seg.curve_type in [BasicCurveType.TG, BasicCurveType.RTG] and \
                        self.curve_type in [BasicCurveType.TG, self.curve_type == BasicCurveType.RTG]:
                    # curr, prev are tg, and prev prev is a curve

                    # potential issues on tangent direction need to be fixed
                    if self.next_seg.side == self.pre_seg.pre_seg.pre_seg.side and \
                                    self.next_seg.defl_angle >= angle_threshold:
                        # next segment is a curve set and is on the same direction of the prepare segment curve
                        if self.pre_seg.pre_seg.length / self.pre_seg.pre_seg.pre_seg.length < \
                                IdCurveConstants.dMultipLenThreshold and \
                                self.pre_seg.length / self.pre_seg.pre_seg.pre_seg.length < \
                                IdCurveConstants.dMultipLenThreshold and \
                                self.length / self.pre_seg.pre_seg.pre_seg.length < \
                                IdCurveConstants.dMultipLenThreshold:
                            self.curve_type = self.pre_seg.pre_seg.pre_seg.curve_type
                            self.pre_seg.curve_type = self.pre_seg.pre_seg.pre_seg.curve_type
                            self.pre_seg.pre_seg.curve_type = self.pre_seg.pre_seg.pre_seg.curve_type
                            self.side = self.pre_seg.pre_seg.pre_seg.side
                            self.pre_seg.side = self.pre_seg.pre_seg.pre_seg.side
                            self.pre_seg.pre_seg.side = self.pre_seg.pre_seg.pre_seg.side
            except AttributeError:
                pass

