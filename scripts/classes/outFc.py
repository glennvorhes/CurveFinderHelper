import arcpy
from uuid import uuid4
import os
arcpy.env.overwriteOutput = True


NO_HIGHWAY_ID = "<None>"
THRESHOLD = 'THRESHOLD'
SEGMENT_ID = "SEGMENT_ID"
CURV_ID = "CURV_ID"
FULL_NAME = "FULL_NAME"
TASLINKID = "TASLINKID"
TRNLINKID = "TRNLINKID"
TRNNODE_F = "TRNNODE_F"
TRNNODE_T = "TRNNODE_T"
RTESYS = "RTESYS"
OFFICIAL_N = "OFFICIAL_N"
VERS_DATE = "VERS_DATE"
CURV_TYPE = "CURV_TYPE"
CURV_DIRE = "CURV_DIRE"
CURV_LENG = "CURV_LENG"
RADIUS = "RADIUS"
DEGREE = "DEGREE"
HAS_TRANS = "HAS_TRANS"
INTSC_ANGL = "INTSC_ANGL"
START_M = "START_M"
END_M = "END_M"
NUM_VERT = "NUM_VERT"


def _make_field_base(field_name):
    return {'field_name': field_name}


def _make_field_text(field_name, field_length=25):
    d = _make_field_base(field_name)
    d['field_type'] = 'TEXT'
    d['field_length'] = field_length
    return d


def _make_field_integer(field_name):
    d = _make_field_base(field_name)
    d['field_type'] = 'LONG'
    d['field_precision'] = 8
    return d


def _make_field_double(field_name):
    d = _make_field_base(field_name)
    d['field_type'] = 'FLOAT'
    d['field_precision'] = 8
    d['field_scale'] = 8
    return d


def create_feature_class(sr, is_dissolved=True):
    field_list = [
        _make_field_double(THRESHOLD),
        _make_field_integer(SEGMENT_ID),
        _make_field_integer(CURV_ID),
        _make_field_text(FULL_NAME, 254)
    ]

    if not is_dissolved:
        field_list.extend([
            _make_field_integer(TASLINKID),
            _make_field_integer(TRNLINKID),
            _make_field_integer(TRNNODE_F),
            _make_field_integer(TRNNODE_T),
            _make_field_integer(RTESYS),
            _make_field_text(OFFICIAL_N),
            _make_field_integer(VERS_DATE)
        ])

    field_list.extend([
        _make_field_text(CURV_TYPE, 100),
        _make_field_text(CURV_DIRE),
        _make_field_double(CURV_LENG),
        _make_field_double(RADIUS),
        _make_field_double(DEGREE),
        _make_field_text(HAS_TRANS),
        _make_field_double(INTSC_ANGL),
        _make_field_double(START_M),
        _make_field_double(END_M),
        _make_field_integer(NUM_VERT)
    ])

    out_dir = 'in_memory'
    fc_name = 'a' + str(uuid4()).replace('-', '')
    out_path = os.path.join(out_dir, fc_name)

    arcpy.CreateFeatureclass_management(out_dir, fc_name, 'POLYLINE', spatial_reference=sr, has_m='ENABLED')

    for f in field_list:
        arcpy.AddField_management(out_path, **f)

    return out_path

#
# if __name__ == '__main__':
#     tst_path = r'C:\tmp2\original_curves.gdb\primary_rsub_83_0p9'
#     print('start')
#     tmp_features = create_feature_class(tst_path)
#     print('end')
#
#     print(arcpy.Describe(tst_path).catalogPath)
#
#     # arcpy.CopyFeatures_management(tmp_features, r'C:\tmp2\original_curves.gdb\mmmmm')
