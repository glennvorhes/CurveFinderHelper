import arcpy
import re
import os
import subprocess


def is_feet(input_fc):
    linear_unit = arcpy.Describe(input_fc).spatialReference.linearUnitName.lower()

    return re.search('foot|feet', linear_unit) is not None


def is_meters(input_fc):
    linear_unit = arcpy.Describe(input_fc).spatialReference.linearUnitName.lower()

    return re.search('meter', linear_unit) is not None


def get_path(input_fc):
    return arcpy.Describe(input_fc).catalogPath


def get_workspace(input_fc):
    return os.path.dirname(get_path(input_fc))


def get_file_name(input_fc):
    return os.path.basename(get_path(input_fc))


def make_output_name(fclass_name, alg, val):
    if isinstance(val, int):
        v = str(val).zfill(3)
    elif isinstance(val, float):
        v = str(val).zfill(4)
    else:
        raise ValueError('val must be int or float')

    v = v.replace('.', '_')

    out_name = "{0}_{1}_{2}".format(fclass_name, alg, v)

    if out_name.find('.shp') > -1:
        out_name = out_name.replace('.shp', '') + '.shp'

    return out_name


def set_curve_geom_number(input_fc, is_ground_truth=False):

    desc = arcpy.Describe(input_fc)
    existing_fields = [str(f.name) for f in desc.fields]

    fields = ['length', 'start_x', 'start_y', 'end_x', 'end_y']

    if is_ground_truth:
        for i in range(len(fields)):
            fields[i] += '_gt'

    for f in fields:
        if f not in existing_fields:
            arcpy.AddField_management(input_fc, f, "DOUBLE")

    arcpy.CalculateField_management(input_fc, fields[0], '!{0}!.length'.format(desc.ShapeFieldName), 'PYTHON_9.3')
    arcpy.CalculateField_management(input_fc, fields[1], '!{0}!.firstPoint.X'.format(desc.ShapeFieldName), 'PYTHON_9.3')
    arcpy.CalculateField_management(input_fc, fields[2], '!{0}!.firstPoint.Y'.format(desc.ShapeFieldName), 'PYTHON_9.3')
    arcpy.CalculateField_management(input_fc, fields[3], '!{0}!.lastPoint.X'.format(desc.ShapeFieldName), 'PYTHON_9.3')
    arcpy.CalculateField_management(input_fc, fields[4], '!{0}!.lastPoint.Y'.format(desc.ShapeFieldName), 'PYTHON_9.3')

    return fields


def setup_name_field(field):
    if field:
        return field.strip()
    else:
        return ''


def setup_workspace(wksp):
    if wksp.endswith('.gdb') and arcpy.Exists(wksp):
        arcpy.Delete_management(wksp)
        arcpy.CreateFileGDB_management(os.path.dirname(wksp), os.path.basename(wksp))


def run_finder(the_file, name_field, out_workspace=None, multi=True, angle=None):
    """

    :param the_file:
    :type the_file: str
    :param name_field:
    :type name_field: str
    :param out_workspace:
    :type out_workspace: str
    :param multi:
    :type multi: bool
    :param angle:
    :type angle: float
    :return:
    :rtype:
    """

    os.chdir(os.path.dirname(__file__))

    args = [os.path.join(os.pardir, 'bin', 'CurveCommandLine.exe')]

    if angle is not None:
        args.extend(['-a', str(angle)])
    elif multi:
        args.append('-m')

    if out_workspace is not None:
        args.extend(['-o', out_workspace])

    if len(name_field) > 0:

        field_valid = False

        for field in arcpy.Describe(the_file).fields:
            if name_field.lower() == field.name.lower():
                field_valid = True
                break

        if field_valid:
            args.extend(['-f', name_field])
        else:
            arcpy.AddWarning("Field {0} not found in {1}".format(name_field, the_file))

    args.append(the_file)

    p = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
    p.wait()
    return p.stdout.read()


def file_list_from_msg(msg):
    return re.findall(r'[A-Z]:\\\S+', msg)
















