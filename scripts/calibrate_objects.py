import math
import re
import arcpy
import helpers

arcpy.env.overwriteOutput = True


def dist_form(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


# SEGMENT_ID
class _CurveCollection:
    def __init__(self, fc_path, subset_roads, ground_truth):
        print(fc_path)
        print(subset_roads)
        self.fc_path = fc_path
        # self._score = 0
        self.angle = float(re.search('[0-9]p[0-9]', fc_path).group().replace('p', '.'))

        self._segments_oid_field = arcpy.Describe(subset_roads).OIDFieldName

        self.cnt_under = 0
        self.cnt_over = 0

        self.length_diff = 0
        self.end_point_diff = 0

        self.len_under = 0
        self.len_over = 0

        self.start_offset = 0
        self.end_offset = 0

        # copy identified curves to memory to speed and add x, y to start, end
        tmp_copy_curves = r'in_memory\tmp_copy_curves'
        arcpy.CopyFeatures_management(fc_path, tmp_copy_curves)
        arcpy.AddField_management(tmp_copy_curves, 'start_x', "FLOAT")
        arcpy.AddField_management(tmp_copy_curves, 'start_y', "FLOAT")
        arcpy.AddField_management(tmp_copy_curves, 'end_x', "FLOAT")
        arcpy.AddField_management(tmp_copy_curves, 'end_y', "FLOAT")
        arcpy.CalculateField_management(tmp_copy_curves, 'start_x', "!Shape!.FirstPoint.X", "PYTHON_9.3")
        arcpy.CalculateField_management(tmp_copy_curves, 'start_y', "!Shape!.FirstPoint.Y", "PYTHON_9.3")
        arcpy.CalculateField_management(tmp_copy_curves, 'end_x', "!Shape!.LastPoint.X", "PYTHON_9.3")
        arcpy.CalculateField_management(tmp_copy_curves, 'end_y', "!Shape!.LastPoint.Y", "PYTHON_9.3")

        subset_id_rows = arcpy.SearchCursor(subset_roads)

        for r in subset_id_rows:
            seg_id = r.getValue(self._segments_oid_field)
            ground_truth_seg_layer = 'gt_curve_layer'
            id_curves_seg_layer = 'id_seg_curve_layer'
            arcpy.MakeFeatureLayer_management(ground_truth, ground_truth_seg_layer, "SEGMENT_ID = {0}".format(seg_id))
            arcpy.MakeFeatureLayer_management(tmp_copy_curves, id_curves_seg_layer, "SEGMENT_ID = {0}".format(seg_id))

            ground_truth_count = int(arcpy.GetCount_management(ground_truth_seg_layer).getOutput(0))
            identified_count = int(arcpy.GetCount_management(id_curves_seg_layer).getOutput(0))

            diff = identified_count - ground_truth_count

            if diff > 0:
                self.cnt_over += diff
            else:
                self.cnt_under += -diff

            # print(diff)
            # print(dir(ground_truth_count))
            # print('ground', ground_truth_count)
            # print("id'd", identified_count)
            # print('over', self.cnt_over)
            # print('under', self.cnt_under)
            # print(int(ground_truth_count))

            tmp_join_gt_to_id_curves = r'in_memory\join_gt_to_id'

            try:

                arcpy.SpatialJoin_analysis(
                    id_curves_seg_layer,
                    ground_truth,
                    tmp_join_gt_to_id_curves,
                    "JOIN_ONE_TO_ONE",
                    "KEEP_ALL",
                    match_option="CLOSEST")



                the_rows = arcpy.SearchCursor(tmp_join_gt_to_id_curves)

                for the_row in the_rows:
                    len_diff = the_row.getValue('length_gt') - the_row.getValue('CURV_LENG')
                    if len_diff > 0:
                        self.len_over += len_diff
                    else:
                        self.len_under += -len_diff

                    start_x_gt = the_row.getValue('start_x_gt')
                    start_y_gt = the_row.getValue('start_y_gt')
                    end_x_gt = the_row.getValue('end_x_gt')
                    end_y_gt = the_row.getValue('end_y_gt')

                    start_x_id = the_row.getValue('start_x')
                    start_y_id = the_row.getValue('start_y')
                    end_x_id = the_row.getValue('end_x')
                    end_y_id = the_row.getValue('end_y')

                    self.start_offset += math.sqrt(
                        math.pow(start_x_gt - start_x_id, 2) + math.pow(start_y_gt - start_y_id, 2)
                    )
                    self.end_offset += math.sqrt(
                        math.pow(end_x_gt - end_x_id, 2) + math.pow(end_y_gt - end_y_id, 2)
                    )

            except Exception:
                self.len_over = -1
                self.len_under = -1
                self.start_offset = -1
                self.end_offset = -1



    @property
    def score(self):
        miscount = self.cnt_under + self.cnt_over
        len_diff = self.len_under + self.len_over
        offset_diff = self.start_offset + self.end_offset
        return miscount


class CurveCollectionOriginal(_CurveCollection):
    def __init__(self, fc_path, subset_roads, ground_truth):
        _CurveCollection.__init__(self, fc_path, subset_roads, ground_truth)
        self.method = "No Smooth"


class CurveCollectionBezier(_CurveCollection):
    def __init__(self, fc_path, subset_roads, ground_truth):
        _CurveCollection.__init__(self, fc_path, subset_roads, ground_truth)
        nm = fc_path[fc_path.find('bezier') + 7:]
        self.method = "Bezier"
        deviation_num = float(re.search('[0-9]{2}_[0-9]', nm).group().replace('_', '.'))
        self.deviation = "{0} Meters".format(deviation_num)


class CurveCollectionPaek(_CurveCollection):
    def __init__(self, fc_path, subset_roads, ground_truth):
        _CurveCollection.__init__(self, fc_path, subset_roads, ground_truth)
        self.method = "Paek"
        nm = fc_path[fc_path.find('paek') + 5:]
        tolerance_num = int(re.search('[0-9]{3}', nm).group().replace('_', '.'))
        self.tolerance = "{0} Meters".format(tolerance_num)
