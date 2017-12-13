import math

class Vertex:

    def __init__(self, x, y, z=None, m=None):
        self.x = x
        self.y = y
        self.z = z
        self.m = m

    @property
    def kw(self):
        return {
            'X': self.x,
            'Y': self.y,
            'Z': self.z,
            'M': self.m
        }

    def get_2d_dist(self, v2):
        """

        :param v2:
        :type v2: Vertex
        :return:
        :rtype: float
        """
        return math.sqrt(
            math.pow(self.x - v2.x, 2) +
            math.pow(self.y - v2.y, 2)
         )

    def get_3d_dist(self, v2):
        """

        :param v2:
        :type v2: Vertex
        :return:
        :rtype: float
        """
        diff_3d = 0

        if self.z is not None and v2.z is not None:
            diff_3d = self.z - v2

        return math.sqrt(
            math.pow(self.x - v2.x, 2) +
            math.pow(self.y - v2.y, 2) +
            math.pow(diff_3d, 2)
         )

    def get_m_diff(self, v2):
        """

        :param v2:
        :type v2: Vertex
        :return:
        :rtype:
        """
        if self.m is not None and v2.m is not None:
            return v2.m - self.m
        else:
            return None

    def as_list(self):
        """

        :return:
        :rtype: list[float]
        """
        c = [self.x, self.y]

        if self.z is not None:
            c.append(self.z)

        if self.m is not None:
            c.append(self.m)

        return c



    def __str__(self):
        out_str = 'x: {0}, y: {1}'.format(self.x, self.y)
        if self.z is not None:
            out_str += ', z: {0}'.format(self.z)
        if self.m is not None:
            out_str += ', m: {0}'.format(self.m)

        return out_str
