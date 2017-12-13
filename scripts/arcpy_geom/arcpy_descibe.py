import arcpy
import re
import os
from abc import abstractmethod
arcpy.env.overwriteOutput = True


class _Field:

    def __init__(self, field_object):

        self.name = str(field_object.name)
        self.type = str(field_object.type)
        self.precision = int(field_object.precision)
        self.scale = int(field_object.scale)
        self.length = int(field_object.length)
        self.alias = str(field_object.aliasName)
        self.nullable = bool(field_object.isNullable)
        self.required = bool(field_object.required)
        self.domain = str(field_object.domain)

    @property
    def field_props(self):
        return {
            'field_name': self.name,
            'field_type': self.type,
            'field_precision': self.precision,
            'field_scale': self.scale,
            'field_length': self.length,
            'field_alias': self.alias,
            'field_is_nullable': self.nullable,
            'field_is_required': self.required,
            'field_domain': self.domain
        }


def _get_fields(the_input, skip_fields):
    """

    :param the_input:
    :type the_input: str
    :param skip_fields:
    :type skip_fields: list[str]
    :return:
    :rtype: list[_Field]
    """
    fields = arcpy.ListFields(the_input)

    for i in range(len(skip_fields)):
        skip_fields[i] = skip_fields[i].lower()

    skip_fields.extend(['shape_length', 'shape_area'])

    field_list = []

    for fi in fields:
        the_field = _Field(fi)
        if str(the_field.name).lower() in skip_fields:
            continue
        else:
            field_list.append(the_field)

    return field_list


class ArcpyDescribeBase:

    def __init__(self, the_input):
        self._desc = arcpy.Describe(the_input)
        self._catalog_path = str(self._desc.catalogPath)
        self._oid_field = str(self._desc.OIDFieldName)
        self._workspace = os.path.dirname(self._catalog_path)
        self._fields = []

    def duplicate(self, output_dataset):

        for the_f in self.fields:
            arcpy.AddField_management(output_dataset, **the_f.field_props)

    @property
    def catalog_path(self):
        """

        :return:
        :rtype: str
        """
        return self._catalog_path

    @property
    def oid_field(self):
        """

        :return:
        :rtype: str
        """
        return self._oid_field

    @property
    def workspace(self):
        """

        :return:
        :rtype: str
        """
        return self._workspace

    @property
    def fields(self):
        """

        :return:
        :rtype: list[_Field]
        """
        return [ff for ff in self._fields]

    @property
    def field_names(self):
        """

        :return:
        :rtype: list[str]
        """
        return [ff.name for ff in self.fields]

    @property
    def field_names_lower(self):
        """

        :return:
        :rtype: list[str]
        """
        return [ff.name.lower() for ff in self.fields]


class ArcpyDescribeTable(ArcpyDescribeBase):

    def __init__(self, the_input):
        ArcpyDescribeBase.__init__(self, the_input)
        self._fields = _get_fields(self._catalog_path, [self.oid_field])

    def duplicate(self, output_table):
        arcpy.CreateTable_management(os.path.dirname(output_table), os.path.basename(output_table))
        ArcpyDescribeBase.duplicate(self, output_table)


class ArcpyDescribeFeatureClass(ArcpyDescribeBase):

    def __init__(self, the_input):
        ArcpyDescribeBase.__init__(self, the_input)

        self._shape_field = str(self._desc.shapeFieldName)

        self._srs = self._desc.spatialReference

        self._is_shapefile = re.search('.shp$', self._catalog_path) is not None
        self._shape_type = str(self._desc.shapeType).upper()
        self._has_m = bool(self._desc.hasM)
        self._has_z = bool(self._desc.hasZ)

        self._units = str(self._desc.spatialReference.linearUnitName).lower()

        if self._units == 'meter':
            pass
        elif self._units.find('foot') > -1:
            self._units = 'foot'

        self._fields = _get_fields(self._catalog_path, [self.oid_field, self.shape_field])

    def duplicate(self, output_fc, force_z=False, force_m=False):
        arcpy.CreateFeatureclass_management(
            os.path.dirname(output_fc),
            os.path.basename(output_fc),
            geometry_type=self.shape_type,
            has_m='ENABLED' if self.has_m or force_m else 'DISABLED',
            has_z='ENABLED' if self.has_z or force_z else 'DISABLED',
            spatial_reference=self.srs
        )

        ArcpyDescribeBase.duplicate(self, output_fc)

    @property
    def shape_field(self):
        """

        :return:
        :rtype: str
        """
        return self._shape_field

    @property
    def shape_type(self):
        """

        :return:
        :rtype: str
        """
        return self._shape_type

    @property
    def has_z(self):
        """

        :return:
        :rtype: bool
        """
        return self._has_z

    @property
    def has_m(self):
        """

        :return:
        :rtype: bool
        """
        return self._has_m

    @property
    def srs(self):
        """

        :return:
        :rtype:
        """
        return self._srs

    @property
    def is_shapefile(self):
        """

        :return:
        :rtype: bool
        """
        return self._is_shapefile

    @property
    def units(self):
        """

        :return:
        :rtype: str
        """
        return self._units


if __name__ == '__main__':
    fcc = r'C:\tmp\tmp.gdb\point_zm'
    describe = ArcpyDescribeFeatureClass(fcc)
    describe.duplicate(r'C:\tmp\tmp.gdb\point_zm_1')

    # for f in describe.fields:
    #     print(f.field_props)
    #
    # print(describe.fields)
    # print(describe.has_m)
    # print(describe.has_z)




