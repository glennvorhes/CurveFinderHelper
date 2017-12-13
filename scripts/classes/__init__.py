import arcpy

def print_arc(*args):
    print(args)
    args = [str(a) for a in args]

    arcpy.AddMessage(', '.join(args))