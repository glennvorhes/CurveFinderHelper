import arcpy
from scripts.arcpy_geom.features import Feature
from scripts.arcpy_geom.arcpy_descibe import ArcpyDescribeFeatureClass


def write_to_feature_class(fc, features):
    """

    :param fc:
    :type fc: str
    :param features:
    :type features: list[Feature]
    :return:
    :rtype:
    """

    desc = ArcpyDescribeFeatureClass(fc)

    insert = arcpy.InsertCursor(fc)
    row = None

    for f in features:
        row = insert.newRow()
        row.shape = f.shape

        for field in desc.field_names:

            if field in f.properties.keys():
                row.setValue(field, f.properties[field])

        insert.insertRow(row)

    del row
    del insert




if __name__ == '__main__':
    print('here')

    tst_path3 = r'C:\tmp\tmp.gdb\primary_rd1'





