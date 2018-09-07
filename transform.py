#!/usr/bin/python

import numpy as np
import re
import sys

# off file
# obj = {'header': (numVertices, numFaces, numEdges), 
#        'vertices': [], 
#        'faces': []}

def read_file(filename):
    obj_file = open(filename, 'r')
    obj = {}

    # read in OFF    
    obj_file.readline()
    
    # read in header
    header = re.split(' ', obj_file.readline()[:-1])
    obj['header'] = tuple([int(n) for n in header])

    # read in vertices
    vertices = []    
    for i in range(obj['header'][0]):
        vertex = re.split(' ', obj_file.readline()[:-1])
        vertex = [float(c) for c in vertex]
        vertices.append(vertex)
    obj['vertices'] = np.matrix(vertices)
    #print np.amax(np.absolute(obj['vertices']), axis=0)

    # read in faces
    faces = []
    for i in range(obj['header'][1]):
        face = obj_file.readline()
        face = face[:-1] if face[-1] == '\n' else face
        face = re.split(' ', face)
        face = face[:-1] if face[-1] == '' else face
        face = [int(idx) for idx in face]
        faces.append(face)
    obj['faces'] = np.matrix(faces)

    obj_file.close()
    return obj

def write_file(obj, filename):
    obj_file = open(filename, 'w')

    # write header
    obj_file.write('OFF\n')
    obj_file.write(" ".join(map(str, obj['header'])) + '\n')

    # write vertices
    vertices = obj['vertices'].tolist()
    [obj_file.write(" ".join(map(str, vertex)) + '\n') for vertex in vertices]

    # write faces
    faces = obj['faces'].tolist()
    [obj_file.write(" ".join(map(str, face)) + '\n') for face in faces]

    obj_file.close()

def transform(obj, scale, Rx, Ry, Rz, Tx, Ty, Tz, cog):
    new_obj = dict(obj)   

    # construct rotation matrix
    Rx *= (np.pi/180)
    Ry *= (np.pi/180)
    Rz *= (np.pi/180)

    Rx = np.matrix([[1,         0,            0],
                    [0, np.cos(Rx), -np.sin(Rx)],
                    [0, np.sin(Rx),  np.cos(Rx)]])

    Ry = np.matrix([[ np.cos(Ry), 0, np.sin(Ry)],
                    [          0, 1,          0],
                    [-np.sin(Ry), 0, np.cos(Ry)]])

    Rz = np.matrix([[np.cos(Rz), -np.sin(Rz), 0],
                    [np.sin(Rz),  np.cos(Rz), 0],
                    [         0,           0, 1]])

    R = Rz*Ry*Rx

    # scale and rotate
    vertices = R*(scale*new_obj['vertices'].T)

    # construct translate matrix
    if cog:
        Tx = -(np.max(vertices[0,:]) + np.min(vertices[0,:]))/2.0
        Ty = -(np.max(vertices[1,:]) + np.min(vertices[1,:]))/2.0
        Tz = -(np.max(vertices[2,:]) + np.min(vertices[2,:]))/2.0
    
    T = np.matrix(new_obj['header'][0]*[[Tx, Ty, Tz]]).T

    new_obj['vertices'] = (vertices + T).T

    return new_obj


if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) >= 2:    
        file_in = args[0]
        file_out = args[1]

        scale = 1

        Rx = 0
        Ry = 0
        Rz = 0

        Tx = 0
        Ty = 0
        Tz = 0

        cog = False  

        if '-S' in args:
            idx = args.index('-S')
            scale = float(args[idx+1])

        if '-R' in args:
            idx = args.index('-R')
            Rx = float(args[idx+1])
            Ry = float(args[idx+2])
            Rz = float(args[idx+3])
            
        if '-T' in args:
            idx = args.index('-T')

            if args[idx+1] == 'cog':
                cog = True
            else:
                Tx = float(args[idx+1])
                Ty = float(args[idx+2])
                Tz = float(args[idx+3])

    else:
        print "Need at least two arguments"

    obj = read_file(file_in)
    new_obj = transform(obj, scale, Rx, Ry, Rz, Tx, Ty, Tz, cog)
    write_file(new_obj, file_out)

