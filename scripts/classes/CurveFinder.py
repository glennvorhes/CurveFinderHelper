import arcpy
from scripts.classes import outFc
from scripts.classes.RoadSegment import RoadSegment
from scripts.arcpy_geom.arcpy_descibe import ArcpyDescribeFeatureClass
from scripts.arcpy_geom.from_feature_class import row_to_feature
from scripts.constants import CurveType
import re
import os
from datetime import datetime


class CurveFinder:
    def __init__(self,
                 input_path,
                 road_name_field=outFc.NO_HIGHWAY_ID):

        if road_name_field is not None and len(str(road_name_field).strip()) == 0:
            road_name_field = None

        self.desc = ArcpyDescribeFeatureClass(input_path)

        if self.desc.units not in ('meter', 'foot'):
            raise Exception("spatial reference of inputs must be feet or meters")

        self._road_name_field = outFc.NO_HIGHWAY_ID if road_name_field is None else road_name_field
        """
        :type: str
        """

        if self._road_name_field != outFc.NO_HIGHWAY_ID and self._road_name_field not in self.desc.field_names:
            raise Exception('provided highway/road name field not in input feature class')

        self._is_dissolved = True

        self._tmp_out_features = outFc.create_feature_class(self.desc.srs, self._is_dissolved)
        """
        :type: str
        """

        self._road_segments = []
        """
        :type: list[RoadSegment]
        """

    def run(self, angle=1.0, iterate=False):

        id_field = outFc.SEGMENT_ID if \
            outFc.SEGMENT_ID.lower() in self.desc.field_names_lower else self.desc.oid_field

        rows = arcpy.SearchCursor(self.desc.catalog_path)
        row = None
        for row in rows:
            feat = row_to_feature(row, self.desc)
            """
            :type: scripts.arcpy_geom.features.LineString
            """
            feat.add_m()

            if feat.multipart:
                raise Exception('Input has multipart features, must be single part')

            road_segment = RoadSegment(
                int(row.getValue(id_field)),
                '' if self._road_name_field == outFc.NO_HIGHWAY_ID else str(row.getValue(self._road_name_field)),
                feat,
                self.desc.units
            )

            if iterate:
                ang = 0.3
                while ang <= 2.0:
                    road_segment.find_curves(ang)
                    ang += 0.1
            else:
                road_segment.find_curves(angle)

            self._road_segments.append(road_segment)

        del row, rows

    def output_curves(self, output_fc):

        insert = arcpy.InsertCursor(self._tmp_out_features)
        ins = None

        for i in range(len(self._road_segments)):
            r_seg = self._road_segments[i]
            for j in range(len(r_seg.all_curve_in_the_poly)):
                curv = self._road_segments[i].all_curve_in_the_poly[j]

                if curv.num_vertices < 3:
                    continue

                ins = insert.newRow()
                ins.shape = curv.shape

                ins.setValue(outFc.SEGMENT_ID, r_seg.segment_id)
                ins.setValue(outFc.CURV_ID, j)
                ins.setValue(outFc.FULL_NAME, r_seg.road_name)
                ins.setValue(outFc.CURV_LENG, curv.Length)
                ins.setValue(outFc.NUM_VERT, curv.num_vertices)
                
                if not self._is_dissolved:
                    ins.setValue(outFc.TASLINKID, curv.TASlinkID)
                    ins.setValue(outFc.TRNLINKID, curv.TRNLinkID)
                    ins.setValue(outFc.TRNNODE_F, curv.TRNNode_F)
                    ins.setValue(outFc.TRNNODE_T, curv.TRNNote_T)
                    ins.setValue(outFc.RTESYS, curv.RTESys)
                    ins.setValue(outFc.OFFICIAL_N, curv.OfficialN)
                    ins.setValue(outFc.VERS_DATE, curv.Vers_date)

                ins.setValue(outFc.THRESHOLD, curv.angleThreshold)
                ins.setValue(outFc.START_M, curv.start_m)
                ins.setValue(outFc.END_M, curv.end_m)

                ins.setValue(outFc.CURV_TYPE, curv.Type)

                if curv.Type != CurveType.TS:
                    ins.setValue(outFc.CURV_DIRE, curv.Dir)

                if curv.Type in [CurveType.HAP, CurveType.TS]:
                    ins.setValue(outFc.RADIUS, None)
                    ins.setValue(outFc.DEGREE, None)
                    ins.setValue(outFc.HAS_TRANS, "")

                    if curv.Type == CurveType.HAP:
                        ins.setValue(outFc.INTSC_ANGL, curv.CentralAngle)
                else:
                    ins.setValue(outFc.RADIUS, curv.Radius)
                    ins.setValue(outFc.DEGREE, curv.CentralAngle)
                    ins.setValue(outFc.HAS_TRANS, 'Yes' if curv.has_transition else 'No')

                insert.insertRow(ins)

        del ins, insert

        arcpy.CopyFeatures_management(self._tmp_out_features, output_fc)



if __name__ == "__main__":
    s = datetime.now()
    # tst_path = r'C:\tmp2\original_curves.gdb\primary_rsub_83_0p9'
    # tst_path2 = r'T:\Projects\CurveFinder\Iowa\IowaCurve\LRS_Linework\NonPrimary.shp'
    # tst_path3 = r'C:\tmp\tmp.gdb\primary_rd1'
    tst_path3 = r'C:\Users\glenn\Desktop\curves\iowa.gdb\primary_dissolve_dis_sub5'

    # r'C:\tmp\tmp.gdb\iowa_dis_13_gt'

    finder = CurveFinder(tst_path3, road_name_field='OFF_NAME')
    finder.run(angle=1)
    finder.output_curves(os.path.join(r'C:\tmp\tmp.gdb', datetime.now().strftime('p%Y_%m_%d_%H_%M_%S')))

    print(datetime.now() - s)
