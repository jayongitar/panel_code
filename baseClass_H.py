# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 17:03:00 2018

@author: jay smith
"""
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

from mpl_toolkits.mplot3d import Axes3D
from numpy.random import rand
from pylab import figure

# ID class:  Initializes an empty list for each type of entity (points, nodes...)
# the method getID takes in an ent_type and:  1) return next available index in the
# corresponding ent_type list.  2) appends index to list
class ID:
    # Initialize empty lists for entities to be indexed and stored
    def __init__(self): 
        self.point_ls = [];
        self.node_ls  = []; 
        self.ctp_ls   = [];
        self.par_ls   = [];
    def __str__(self):
        return "<node_ls{} pnt_ls{}>".format(self.point_ls,self.node_ls)
    # returns next availalbe index in list and appends to list
    def getID(self, ent_type):
        # for ent_type point
        if   ent_type == 'point':
            index = len(self.point_ls)
            self.point_ls.append(index)
            return_ls = [ent_type, index]
#            return return_ls
            return index
        # for ent_type node
        elif ent_type == 'node':
            index = len(self.node_ls)
            self.node_ls.append(index)
            return_ls = [ent_type, index]
#            return return_ls
            return index
        elif ent_type == 'ctp':
            index = len(self.ctp_ls)
            self.ctp_ls.append(index)
            return_ls = [ent_type, index]
#            return return_ls
            return index
        elif ent_type == 'par':
            index = len(self.par_ls)
            self.par_ls.append(index)
            return_ls = [ent_type, index]
#            return return_ls
            return index
        else:
            return "invalid entity type"
        
    def get_ls(self, ent_type):
        
        if ent_type == 'point':
                return self.point_ls
        if ent_type == 'node':
                return self.node_ls
            
class point:
    # Class attributes
    ent_type = 'point'
    # Initializer / Instance attributes (specific to each object)
    def __init__(self, x=0, y=0, z=0, frame='{XX}'):
        self.x = x
        self.y = y
        self.z = z
        self.frame = frame
    def __str__(self):
        return "<{},{},{}> {}".format(self.x, self.y, self.z, self.frame)
    
#point1 = point(1,0,0,'{body}')
#print(point1)
     
class node(point):
    # Class attributes
    ent_type = 'node'
    # Initializer
    def __init__(self, point=None, index=None, grid_index=None):
        self.point = point
        self.index = index
        self.grid_index = grid_index
    def __str__(self):
        return "<{}_index={}, grid_index={}>, point=<{},{},{}> frame={}".format(self.ent_type, self.index, self.grid_index, self.point.x, self.point.y, self.point.z, self.point.frame)
    
#node1 = node(point1,3)
#print(node1)
        
class config(ID, point):
    def __init__(self, name):
#        super().__init__()
        ID.__init__(self)
        point.__init__(self)
        self.name = name
        # Initialize objects
        
    def __str__(self):
        return "class name = {}, point_ls = {}, node_ls = {}".format(self.name, self.point_ls, self.node_ls)
    
class geom(ID,node):
    def __init__(self, name, span, chord, n_span, n_chord):
#        super().__init__()
        ID.__init__(self)
        node.__init__(self)
        self.name = name
        self.span = span
        self.chord = chord
        self.n_span = n_span
        self.n_chord = n_chord
        # Initialize objects
    def __str__(self):
        return "{}: span={}, chord={}".format(self.name, self.span, self.chord)
    def build_nodes(self):
        node_ls = []
        for j in range(self.n_chord):
            for i in range(self.n_span):
                y = self.span*i/(self.n_span-1)-self.span/2
                x =-self.chord*j/(self.n_chord-1)+0.25*self.chord
                node1 = node(point(x,y,0,'{body}'), ID.getID(self,'node'),j*100+i)
                node_ls.append(node1)
                
        ctp_ls = []
        for j in range(self.n_chord-1):
            for i in range(self.n_span-1):
                yc = self.span*i/(self.n_span-1)-self.span/2 + 0.5*(self.span)/(self.n_span-1)
                xc =-self.chord*j/(self.n_chord-1)+0.25*self.chord - 0.5*(self.chord)/(self.n_chord-1)
                ctp1 = node(point(xc,yc,0,'{body}'), ID.getID(self,'ctp'),j*100+i)
                ctp_ls.append(ctp1)
        
        print('length of node_ls = %4.0f' % (len(node_ls)))
        print('length of ctp_ls = %4.0f' % (len(ctp_ls)))
        
        node_dict = {}
        for i in range(len(node_ls)):
            node_i = node_ls[i]
            node_dict[node_i.grid_index] = node_i.index
        ctp_dict = {}
        
        for i in range(len(ctp_ls)):
            ctp_i = ctp_ls[i]
            ctp_dict[ctp_i.grid_index] = ctp_i.index
            
        return_ls = [node_ls, ctp_ls, node_dict, ctp_dict]
        return return_ls
    
    def ps(self):
        ctp_ls = []
        for j in range(self.n_chord-1):
            for i in range(self.n_span-1):
                pass
        return
                
        
    
        
geom1 = geom('geom1',10,2,6,6)
#print(geom1)
return_ls1 = geom1.build_nodes()
node_ls1 = return_ls1[0]
ctp_ls1  = return_ls1[1]
node_dict1 = return_ls1[2]
ctp_dict1  = return_ls1[3]

plt.close
fig = plt.figure(num=1)
ax = plt.axes(projection='3d')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

ax.set_xlim(-5,5)
ax.set_ylim(-5,5)
ax.set_zlim(-5,5)
ax.set_aspect('equal', 'box')

x_ls = [];  y_ls = [];  z_ls = []
for i in range(len(node_ls1)):
    node_i = node_ls1[i]
    index = node_i.grid_index
    x = node_i.point.x
    y = node_i.point.y
    z = node_i.point.z
#    print(index)
#    print(x)
#    print(y)
#    print(z)
    ax.scatter(([x]), ([y]), ([z]), 'od', color='b')
    ax.text(x,y,z, 'n_%s' % str(index), size=5, zorder=1, color='k')
    
for i in range(len(ctp_ls1)):
    ctp_i = ctp_ls1[i]
    index = ctp_i.grid_index
    x = ctp_i.point.x
    y = ctp_i.point.y
    z = ctp_i.point.z
    ax.scatter(([x]), ([y]), ([z]), 'od', color='red')
    ax.text(x,y,z, 'n_%s' % str(index), size=5, zorder=1, color='red')



    












