# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 11:52:02 2018

@author: jay smith
"""
import numpy as np
import matplotlib.pyplot as plt

class ID:
    
    # Initializer / Instance attributes
    def __init__(self,ent_type,index):
        if   ent_type == 'point':
            self.ent_type = 'point'
            self.index = index
        elif ent_type == 'node':
            self.ent_type = 'node'
            self.index = index
        elif ent_type == 'control_point':
            self.ent_type = 'control_point'
            self.index = index
        elif ent_type == 'point_vortex':
            self.ent_type = 'point_vortex'
            self.index = index
        elif ent_type == 'line_vort':
            self.ent_type = 'line_vortex'
            self.index = index
        else:
            return "invalid entity type"
        
    def __str__(self):
        return "<{} {}>".format(self.ent_type,self.index)
    

class fig3D:
    
    # Initializer / Instance attributes
    def __init__(self,fig_n):
        self.fig_n = fig_n
    
    def create_figure(self):
        plt.close()
        fig = plt.figure(num=self.fig_n)
        ax = Axes3D(fig)
        return ax
        
        
class plot3D:
    
    # Initializer / Instance attritubes
    def __init__(self,ax,node):
        self.ax = ax
        self.node = node
    def pl(self):
        self.ax.plot(([self.node.point.x]), ([self.node.point.y]), ([self.node.point.z]),'o')
        index = self.node.ID.index
        x = self.node.point.x
        y = self.node.point.y
        z = self.node.point.z
#        print('index')
#        print(str(index))
#        print(x)
#        print(y)
#        print(z)
        self.ax.text(x,y,z, '%s' % (str(index)), size=20, zorder=1, color='k') 


class point:
    # Initializer / Instance attributes (specific to each object)
    def __init__(self, x=0, y=0, z=0, frame='{XX}'):
        self.x = x
        self.y = y
        self.z = z
        self.frame = frame
    def __str__(self):
        return "<{},{},{}> {}".format(self.x, self.y, self.z, self.frame)
    
    
class node(ID,point):
    def __init__(self, ID, point):
        self.ID = ID
        self.point = point
    def __str__(self):
        return "{}_{} <{},{},{}> {}".format(self.ID.ent_type, self.ID.index, self.point.x, self.point.y, self.point.z, self.point.frame)


class geom():
    def __init__(self, node, span, chord, n_span, n_chord):
        self.node = node
        self.span = span
        self.chord = chord
        self.n_span = n_span
        self.n_chord = n_chord
    def __str__(self):
        Printf('less trailing zeros <%4.2f, %2.2f, %1.1f>', )
        return "geometry class containing node method and 4 attributes: {}, {}, {}, {}".format(self.span, self.chord, self.n_span, self.n_chord)
    def generate_nodes(self):
        index_mat = np.zeros((self.n_span, self.n_chord))
        for i in range(self.n_span):
            for j in range(self.n_chord):
                index_mat[i,j] = i+100*j
        print(index_mat)
        
        point_mat = np.zeros((self.n_span, self.n_chord, 3))
        # y points
        for i in range(self.n_span):
            for j in range(self.n_chord):
                point_mat[i,j,0] = self.span*(-i*(1/(self.n_span-1))+0.5)
        print(point_mat[:,:,0])
        # x points
        for i in range(self.n_span):
            for j in range(self.n_chord):
                point_mat[i,j,1] = self.chord*(i*(1/(self.n_span-1))-0.25)
        print(point_mat[:,:,1])
        # z points
        for i in range(self.n_span):
            for j in range(self.n_chord):
                point_mat[i,2] = 0
        print(point_mat[:,:,2])
        
        for i in range(self.n_span):
            for j in range(self.n_chord):
                idd = ID('node', index_mat[i,j])
#                print(idd)
                ppoint = point(round(point_mat[i,j,0],2), point_mat[i,j,1], point_mat[i,j,2], '{00}')
#                print(ppoint)
                nnode = node(idd,ppoint)
                print(nnode)
            
        
        
    

geom1 = geom(node,1,0.2,6,6)
print(geom1)
geom1.generate_nodes()


#n = 11
#id_ls = []
#for i in range(n):
#    id_ls.append(ID('node',i))
##    print(id_ls[i])
#
#pt_ls = []
#x = np.zeros(n)
#y = np.zeros(n)
#z = np.linspace(0,1,n)
#for i in range(n):
#    pt_ls.append(point(x[i],y[i],z[i],'{00}'))
##    print(pt_ls[i])
#    
#nd_ls = []
#for i in range(n):
#    nd_ls.append(node(id_ls[i], pt_ls[i]))
##    print(nd_ls[i])
#    
#for i in range(n):
#    print(nd_ls[i])

    
#ID_1 = ID('node',2)
##print(ID_1)
#point1 = point(0,0,0,'{00}')
#
#node2 = node(ID_1,point1)
#print(node2.point.x)
#print(node2)


figure10 = fig3D(10)
ax10 = figure10.create_figure()
for i in range(n):
    plot_point =plot3D(ax10,nd_ls[i])
    plot_point.pl()


















