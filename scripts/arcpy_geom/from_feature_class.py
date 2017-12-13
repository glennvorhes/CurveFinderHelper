import math
import re
import arcpy
from scripts.arcpy_geom.arcpy_descibe import ArcpyDescribeFeatureClass
from scripts.arcpy_geom import features
from scripts.arcpy_geom import wkt_parse


def row_to_feature(the_row, desc):
    """

    :param the_row: arcgis row
    :type the_row:
    :param desc:
    :type desc: ArcpyDescribeFeatureClass
    :return:
    :rtype: features.Feature
    """
    feat = wkt_parse.wkt_to_feat(the_row.getValue(desc.shape_field).WKT)
    feat.properties = {field: the_row.getValue(field) for field in desc.field_names}
    return feat


if __name__ == '__main__':
    # fc = r'C:\tmp\tmp.gdb\point_zm'
    fc = r'C:\tmp\tmp.gdb\multipoint'
    # fc = r'C:\tmp\tmp.gdb\m_poly'
    # fc = r'C:\tmp\tmp.gdb\iowa_dis_44_m'
    search = arcpy.SearchCursor(fc)

    des = ArcpyDescribeFeatureClass(fc)

    for row in search:
        f = row_to_feature(row, des)
