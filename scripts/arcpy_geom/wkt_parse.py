import re
from scripts.arcpy_geom.Vertex import Vertex
from scripts.arcpy_geom import features


def _wkt_to_vertices(wkt_str, has_z, has_m):
    """

    :param wkt_str:
    :type wkt_str: str
    :param has_z:
    :type has_z: bool
    :param has_m:
    :type has_m: bool
    :return:
    :rtype:
    """

    inr = r'(-|\d|\.|\s|[a-zA-Z]|,)+'

    wkt_str = wkt_str.strip()[1:-1]

    if re.search(r'^(\s*\(){2}', wkt_str):
        p = []
        for r in re.finditer(r'(\s*\(){2}' + inr + r'(\)\s*,\s*\()*' + inr + r'(\s*\)){2}', wkt_str):
            p.append(_wkt_to_vertices(r.group(0).strip(), has_z, has_m))
        return p
    elif re.search(r'^(\s*\()', wkt_str):
        p = []

        for r in re.finditer(r'\(' + inr + r'\)', wkt_str):
            p.append(_wkt_to_vertices(r.group(0).strip(), has_z, has_m))
        return p
    else:
        vert_list = []
        for r in re.split(r'\s*,\s*', wkt_str):
            ps = r.split()

            x = float(ps[0])
            y = float(ps[1])
            z = None
            m = None

            if has_m and has_z:
                z = float(ps[2])
                m = float(ps[3])
            elif has_m:
                m = float(ps[2])
            elif has_z:
                z = float(ps[2])

            vert_list.append(Vertex(x, y, z, m))
        return vert_list


def wkt_to_feat(wkt):
    """

    :param wkt:
    :type wkt:
    :return:
    :rtype: features.Feature
    """
    geom_prefix = re.search(r'\s*[a-zA-Z]+\s*[a-zA-Z]*\s*', wkt).group(0)
    wkt = wkt.replace(geom_prefix, '').strip()
    geom_type = geom_prefix.strip().lower()
    geom_type_parts = geom_type.split()
    geom_type = geom_type_parts[0]

    has_m = False
    has_z = False

    if len(geom_type_parts) > 1:
        zm = geom_type_parts[1]
        has_m = zm.find('m') > -1
        has_z = zm.find('z') > -1

    verts = _wkt_to_vertices(wkt, has_z, has_m)

    if geom_type == 'point':
        return features.Point(verts)
    elif geom_type == 'linestring' or geom_type == 'multilinestring':
        return features.LineString(verts)
    elif geom_type == 'polygon' or geom_type == 'multipolygon':
        return features.Polygon(verts)
    elif geom_type == 'multipoint':
        return features.MultiPoint(verts)
    else:
        raise NotImplementedError('geom type not implemented: {0}'.format(geom_type))

#
# if __name__ == '__main__':
#     the_wkt = 'MULTIPOLYGON (((-93.804035279999937 43.108270270000048, -93.803921675999959 43.108196561000057, -93.803735646999939 43.10833608300004, -93.803879999999936 43.108438865000039, -93.804035279999937 43.108270270000048) , (-93.804035279999937 43.108270270000048, -93.803921675999959 43.108196561000057, -93.803735646999939 43.10833608300004, -93.803879999999936 43.108438865000039, -93.804035279999937 43.108270270000048)), ((-93.803589210999974 43.108435136000026, -93.803359701999966 43.108444702000043, -93.803464416999986 43.108578984000076, -93.803642176999972 43.108627858000034, -93.803589210999974 43.108435136000026)))'
#
#     wkt_to_feat(the_wkt)
