from ..arcpy_geom.features import LineString


class Curve(LineString):

    def __init__(self, angle_threshold):
        self.Type = None
        self._Length = None
        self._Dir = None
        self.Dir = None
        self._CentralAngle = None
        self.CentralAngle = None
        self._Radius = None
        self.Radius = None
        self.angleThreshold = angle_threshold
        self.has_transition = None

        self.OfficialN = None
        self.TASlinkID = None
        self.TRNLinkID = None
        self.TRNNode_F = None
        self.TRNNote_T = None
        self.RTESys = None
        self.Vers_date = None

        LineString.__init__(self, [])

    @property
    def start_m(self):
        if self.num_vertices == 0:
            return None
        else:
            return self.vertices[0].m

    @property
    def end_m(self):
        if self.num_vertices == 0:
            return None
        else:
            return self.vertices[-1].m

    @property
    def Length(self):
        cumul_len = 0

        if len(self.vertices) > 1:
            for i in range(1, len(self.vertices)):
                cumul_len += self.vertices[i].get_2d_dist(self._vertices[i - 1])

        return cumul_len

    @property
    def Dir(self):
        return self._Dir

    @Dir.setter
    def Dir(self, d):
        self._Dir = d
        self.set_property('Dir', d)

    @property
    def CentralAngle(self):
        return self._CentralAngle

    @CentralAngle.setter
    def CentralAngle(self, a):
        self._CentralAngle = a
        self.set_property('CentralAngle', a)

    @property
    def Radius(self):
        return self._Radius

    @Radius.setter
    def Radius(self, r):
        self._Radius = r
        self.set_property('Radius', r)



