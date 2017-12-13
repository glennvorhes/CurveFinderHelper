from scripts.arcpy_geom.Vertex import Vertex
from scripts.constants import AboveBelowLine


class StraightLine:

    def __init__(self, pt1, pt2):
        """

        :param pt1:
        :type pt1: Vertex
        :param pt2:
        :type pt2: Vertex
        """
        self.bVerticalLine = None
        self.xIntercept = None
        self.k = None
        self.b = None

        if pt1.x == pt2.x:
            self.bVerticalLine = True
            self.xIntercept = pt1.x

        else:
            self.bVerticalLine = False
            self.k = (pt1.y - pt2.y) / (pt1.x - pt2.x)
            self.b = pt1.y - self.k * pt1.x

    def point_above_or_below_the_line(self, pt_c):
        """

        :param pt_c:
        :type pt_c: Vertex
        :return:
        :rtype: str
        """

        try:
            y_0 = self.k * pt_c.x + self.b
        except TypeError:
            return AboveBelowLine.ONTHELINE

        if pt_c.y > y_0:
            return AboveBelowLine.ABOVE
        elif pt_c.y < y_0:
            return AboveBelowLine.BELOW
        else:
            return AboveBelowLine.ONTHELINE


