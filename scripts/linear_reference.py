import arcpy
from uuid import uuid4
import add_dir
from scripts.arcpy_geom.arcpy_descibe import ArcpyDescribeFeatureClass
from scripts.arcpy_geom.from_feature_class import row_to_feature
from scripts.arcpy_geom.to_feature_class import write_to_feature_class


arcpy.env.overwriteOutput = True


def _def_add_linear_ref(in_fc, out_fc):
    desc = ArcpyDescribeFeatureClass(in_fc)

    desc.duplicate(out_fc, force_m=True)
    search = arcpy.SearchCursor(input_fc)
    features = []
    """
    :type: list[scripts.arcpy_geom.features.LineString]
    """

    for row in search:
        ll = row_to_feature(row, desc)
        """
        :type: scripts.arcpy_geom.features.LineString
        """
        ll.add_m()

        features.append(ll)

    write_to_feature_class(out_fc, features)


if __name__ == '__main__':
    input_fc = arcpy.GetParameterAsText(0) or r'C:\Users\glenn\Desktop\curves\iowa.gdb\primary_dissolve'
    output_fc = arcpy.GetParameterAsText(1) or r'C:\tmp\tmp.gdb\a' + str(uuid4()).replace('-', '')
    _def_add_linear_ref(input_fc, output_fc)
