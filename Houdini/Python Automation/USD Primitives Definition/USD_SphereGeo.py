from pxr import Usd, UsdGeom, Sdf
import math


def get_cartesian_position(theta, phi):

    x = math.sin(phi) * math.cos(theta)
    y = math.sin(phi) * math.sin(theta)
    z = math.cos(phi)

    position = (x, y, z)

    return position

def sphere(h_points, v_points):
    '''
    Polygonal Sphere
    '''

    points = []
    face_vertex_counts = []
    face_vertex_indices = []

    #Create sphere points
    points.append( (0,0,1) )  #Top pole

    for v_pt in range(v_points - 1):    #Range exclude top pole
        v_angle = v_pt * 3.14 / ( v_points - 1 )

        for h_pt in range(h_points):
            h_angle = h_pt * 2.0 * 3.15 / h_points

            position = get_cartesian_position(h_angle, v_angle)

            points.append(position)

    points.append( (0, 0, -1) )   #Bottom pole
    # print(points)

    #Create sphere faces
    
    # Top pole faces
    top_pole_index = 0
    first_row_start = 1
    for h in range(h_points):
        next_point  = (h+1) % h_points
        face_vertex_indices.extend( [top_pole_index, first_row_start + next_point, h + first_row_start ] )
        face_vertex_counts.append(3)

    # Create body faces(quads)
    for v in range(1, v_points - 2):
        row_start = 1 + (v_points-1) * h_points
        next_row_start =  row_start + h_points

        for h in range(h_points):
            next_point = (h + 1) % h_points
            face_vertex_indices.extend( [row_start+h, 
                                         row_start+next_point, 
                                         next_row_start+next_point, 
                                         next_row_start+h] )
            face_vertex_counts.append(4)

    ## Bottom pole faces
    bottom_pole_index = len(points) - 1
    last_row_start = 1 + (v_points - 3) * h_points
    for h in range(h_points):
        next_point = (h+1) % h_points
        face_vertex_indices.extend( [bottom_pole_index, 
                                     h+last_row_start, 
                                     last_row_start+next_point] )
        face_vertex_counts.append(3)

    geometryData = {'points': points,
                    'face_vertex_indices': face_vertex_indices, 
                    'face_vertex_counts': face_vertex_counts}
    
    return geometryData

print( sphere(8, 6) )



def create_geometry():

    stage = Usd.Stage.CreateNew('/home/vishal/Documents/Houdini Projects/Kiryha/PROMO/sphere2.usda')
    root = UsdGeom.Xform.Define(stage, "/Root")
    mesh = UsdGeom.Mesh.Define(stage, "/Root/Sphere")

    geometryData = sphere(8,6)

    mesh.GetPointsAttr().Set(geometryData['points'])
    mesh.GetFaceVertexIndicesAttr().Set(geometryData['face_vertex_indices'])
    mesh.GetFaceVertexCountsAttr().Set(geometryData['face_vertex_counts'])
    
    mesh.CreateOrientationAttr().Set(UsdGeom.Tokens.leftHanded)
    mesh.CreateSubdivisionSchemeAttr().Set('none')

    stage.GetRootLayer().Save()

create_geometry()