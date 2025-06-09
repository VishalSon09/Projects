from pxr import Usd, UsdGeom, Sdf
import math


def cone(resolution):
    """
    Create poly cone
    """

    points = []  # List of point positions
    face_vertex_counts = []  # List of vertex count per face
    face_vertex_indices = []  # List of vertex indices

    # Create cone points
    for point in range(resolution):
        angle = 2.0 * 3.14 * point / resolution

        x = math.cos(angle)
        z = math.sin(angle)
        points.append((x, 0, z))

    # Add tip
    points.append((0, 2, 0))

    # Crete cone faces
    for point in range(resolution):
        triangle = [point, (point + 1) % resolution, resolution]
        face_vertex_indices.extend(triangle)
        face_vertex_counts.append(3)

    geometry_data = {'points': points,
                     'face_vertex_counts': face_vertex_counts,
                     'face_vertex_indices': face_vertex_indices}

    return geometry_data


def crate_geometry():
    """
    Procedurally create geometry and save it to the USDA file
    """

    # Create USD
    stage = Usd.Stage.CreateNew('/home/vishal/Documents/Houdini Projects/Kiryha/PROMO/cone_one.usda')

    # Build mesh object
    root_xform = UsdGeom.Xform.Define(stage, '/Root')
    mesh = UsdGeom.Mesh.Define(stage, '/Root/Cone')

    # Build cone geometry.
    geometry_data = cone(12)

    # Set mesh attributes
    mesh.GetPointsAttr().Set(geometry_data['points'])
    mesh.GetFaceVertexCountsAttr().Set(geometry_data['face_vertex_counts'])
    mesh.GetFaceVertexIndicesAttr().Set(geometry_data['face_vertex_indices'])

    # Set orientation and subdivisionScheme
    mesh.CreateOrientationAttr().Set(UsdGeom.Tokens.leftHanded)
    mesh.CreateSubdivisionSchemeAttr().Set("none")

    # print(geometry_data)
    print(len(geometry_data['points']))

    # Save USD
    stage.GetRootLayer().Save()

crate_geometry()