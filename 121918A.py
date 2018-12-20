# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 17:07:50 2018

@author: jay smith
"""
import numpy as np
# nodes dims:  n_span, n_chord+2 (this includes two panels after the wing: 1 for kutta, 1 for wake particle stability)
# control point dims:  n_span-1, n_chord (includes 1 control point after wing for enforcement of kutta condition)
# np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})

np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})

span = 4
chord = 2
n_span = 5
n_chord = 4
alpha   = 0.1

class panel():
    def __init__(self, span, chord, n_span, n_chord, n_wake, alpha):
        self.span = span
        self.chord = chord
        self.n_span = n_span
        self.n_chord = n_chord
        self.n_wake = n_wake
        self.alpha = alpha        
        # node matrix
        self.np_nodes = np.zeros((n_span, n_chord+1+n_wake, 4))
        self.np_ctp = np.zeros((n_span-1, n_chord, 4))
        # control point matrix size [n_span-1, n_chord-1]
        self.camberline =-alpha*np.ones((n_span-1, n_chord-1))
        self.wash_lv_horz = np.zeros((n_span-1, n_chord-1))
        self.wash_lv_vert = np.zeros((n_span-1, n_chord-1))
        self.RHS = self.camberline - self.wash_lv_horz - self.wash_lv_vert
        self.IOB = np.zeros((n_span-1, n_chord-1))
        self.IOT_horz = np.zeros((n_span-1, n_chord-1))
        self.IOT_vert = np.zeros((n_span-1, n_chord-1))
        
        # generated-doublet-matrix (1 more chord panel for kutta condition) [n_span-1, n_chord]
        self.mu_gen = np.zeros((n_span-1,n_chord))
        self.mu_total = np.zeros((n_span-1,n_chord))
        
        # matrix of horizontally oriented lienar vortex [n_span-1, n_chord+1+n_wake]
        # [index, strength, x1, y1, z1, x2, y2, z2]
        self.np_lv_horz = np.zeros((n_span-1, n_chord+1+n_wake, 8))
        # matrix of vertically oriented linear vortex [n_span, n_chord+n_wake]
        self.np_lv_vert = np.zeros((n_span, n_chord+n_wake, 8))
        
        # influence for line vortex on control points
        self.infl_lv_horz = np.zeros((n_span-1, n_chord-1, n_span-1, n_chord+1+n_wake, 3))
        self.infl_lv_vert = np.zeros((n_span-1, n_chord-1, n_span, n_chord+n_wake, 3))
        self.infl_ctp     = np.zeros((n_span-1, n_chord-1, n_span-1, n_chord, 3))  # includes influence of doublet at control point behind trailing edge
        self.infl_ctp_ii  = np.zeros((n_span-1, n_chord-1, 3))  # does not include doublet at control point behind trailing edge
        
# simple rectangular wing GEOMETRY ############################################
        
        # nodes. i,j iteration order switched for easy math
        for j in range(n_chord+1+n_wake):
            for i in range(n_span):
                self.np_nodes[i,j,0] = i+100*j    
                self.np_nodes[i,j,1] = span*i/(n_span-1)-span/2       #-y
                self.np_nodes[i,j,2] =-chord*j/(n_chord-1)+0.25*chord # x
                self.np_nodes[i,j,3] = 0; # z     
        print('np_nodes index')
        print(self.np_nodes[:,:,0])
                
        # control points. i,j iteration order switched for easy math
        for j in range(n_chord):
            for i in range(n_span-1):
                self.np_ctp[i,j,0] = i+100*j    
                self.np_ctp[i,j,1] = span*i/(n_span-1)-span/2 + span/(n_span-1)/2       #-y
                self.np_ctp[i,j,2] =-chord*j/(n_chord-1)+0.25*chord - chord/(n_chord-1)/2 # x
                self.np_ctp[i,j,3] = 0; # z     
        print('np_ctp index')
        print(self.np_ctp[:,:,0])

        # horizontal line vortex matrix
        for i in range(n_span-1):
            for j in range(n_chord+1+n_wake):
                self.np_lv_horz[i,j,0] = 1000+i+100*j
        
                self.np_lv_horz[i,j,2] = self.np_nodes[i,j,1]
                self.np_lv_horz[i,j,3] = self.np_nodes[i,j,2]
                self.np_lv_horz[i,j,4] = self.np_nodes[i,j,3]
        
                self.np_lv_horz[i,j,5] = self.np_nodes[i+1,j,1]
                self.np_lv_horz[i,j,6] = self.np_nodes[i+1,j,2]
                self.np_lv_horz[i,j,7] = self.np_nodes[i+1,j,3]

        
        # verticle line vortex matrix
        for i in range(n_span):
            for j in range(n_chord+n_wake):
                self.np_lv_vert[i,j,0] = 2000+i+100*j
        
                self.np_lv_vert[i,j,2] = self.np_nodes[i,j,1]
                self.np_lv_vert[i,j,3] = self.np_nodes[i,j,2]
                self.np_lv_vert[i,j,4] = self.np_nodes[i,j,3]
        
                self.np_lv_vert[i,j,5] = self.np_nodes[i,j+1,1]
                self.np_lv_vert[i,j,6] = self.np_nodes[i,j+1,2]
                self.np_lv_vert[i,j,7] = self.np_nodes[i,j+1,3]
        
# LIN_VORT ####################################################################
        
        def lin_vort(xp,yp,zp, x1,y1,z1, x2,y2,z2):
            r1xr2_x = (yp-y1)*(zp-z2)-(zp-z1)*(yp-y2)
            r1xr2_y =-(xp-x1)*(zp-z2)+(zp-z1)*(xp-x2)
            r1xr2_z = (xp-x1)*(yp-y2)-(yp-y1)*(xp-x2)
            abs2    = ( (r1xr2_x)**2 + (r1xr2_y)**2 + (r1xr2_z)**2 )
            # step 2: calculate distances r1,r2:
            r1= np.sqrt( (xp-x1)**2 + (yp-y1)**2 + (zp-z1)**2 )
            r2= np.sqrt( (xp-x2)**2 + (yp-y2)**2 + (zp-z2)**2 )
            # step 4: calculate the dot product:
            r0r1= (x2-x1)*(xp-x1) + (y2-y1)*(yp-y1) + (z2-z1)*(zp-z1)
            r0r2= (x2-x1)*(xp-x2) + (y2-y1)*(yp-y2) + (z2-z1)*(zp-z2)
            # step 5: the resulting velocity components
            K= (1/(4*3.14*abs2))*(r0r1/r1 - r0r2/r2)
            u=K*r1xr2_x; v=K*r1xr2_y; w=K*r1xr2_z
            pert = [u,v,w]
            return pert
        
        
# INFLUENCE ###################################################################
        # horizontal line vortex influence on control point matrix
        # creates 4dim matrix with dims:  ctp_matrix x lv_horz
        for i in range(n_span-1):
            for j in range(n_chord-1):
                xp = self.np_ctp[i,j,1];  yp = self.np_ctp[i,j,2];  zp = self.np_ctp[i,j,3]
                for k in range(n_span-1):
                    for l in range(n_chord+1+n_wake):
                        x1 = self.np_lv_horz[k,l,2];  y1 = self.np_lv_horz[k,l,3];  z1 = self.np_lv_horz[k,l,4]
                        x2 = self.np_lv_horz[k,l,5];  y2 = self.np_lv_horz[k,l,6];  z2 = self.np_lv_horz[k,l,7]
        
                        pert = lin_vort(xp,yp,zp, x1,y1,z1, x2,y2,z2)
                
                        self.infl_lv_horz[i,j,k,l,0] = pert[0]  # u
                        self.infl_lv_horz[i,j,k,l,1] = pert[1]  # v
                        self.infl_lv_horz[i,j,k,l,2] = pert[2]  # w
#        print('infl_lv_horz[0,0,:,:,2]')
#        print(self.infl_lv_horz[0,0,:,:,2])
        

        # verticle line vortex influence on control point matrix
        # creates 4dim matrix with dims:  ctp_matrix x lv_horz
        for i in range(n_span-1):
            for j in range(n_chord-1):
                xp = self.np_ctp[i,j,1];  yp = self.np_ctp[i,j,2];  zp = self.np_ctp[i,j,3]
                for k in range(n_span):
                    for l in range(n_chord+1):
                        x1 = self.np_lv_vert[k,l,2];  y1 = self.np_lv_vert[k,l,3];  z1 = self.np_lv_vert[k,l,4]
                        x2 = self.np_lv_vert[k,l,5];  y2 = self.np_lv_vert[k,l,6];  z2 = self.np_lv_vert[k,l,7]
        
                        pert = lin_vort(xp,yp,zp, x1,y1,z1, x2,y2,z2)
                
                        self.infl_lv_vert[i,j,k,l,0] = pert[0]  # u
                        self.infl_lv_vert[i,j,k,l,1] = pert[1]  # v
                        self.infl_lv_vert[i,j,k,l,2] = pert[2]  # w
#        print('infl_lv_vert[0,0,:,:,2]')
#        print(self.infl_lv_vert[0,0,:,:,2])

        # doublet-influence-on-control-points (positive downwash) (doublets are located at control points)
        # creates 4dim matrix with dims:  np_ctp {n_span-1, n_chord-1} x np_ctp fist wake doublet {n_span-1, n_chord}.  first wake doublet negative of trailing edge doublet
        for i in range(n_span-1):
            for j in range(n_chord-1):
                for k in range(n_span-1):
                    for l in range(n_chord):
                        for m in range(3):
                            self.infl_ctp[i,j,k,l,m] = self.infl_lv_horz[i,j,k,l,m] - self.infl_lv_horz[i,j,k,l+1,m] - self.infl_lv_vert[i,j,k,l,m] + self.infl_lv_vert[i,j,k+1,l,m]
#        print('infl_ctp')
#        print(infl_ctp[1,1,:,:,2])

        # implify the doublet-influence-on-control-points matrix to diagonal elements. influence of doublet on its co-located control point.  initial value for iteration that solves for generated-doublet-distribution (GDD).
        for i in range(n_span-1):
            for j in range(n_chord-1):
                self.infl_ctp_ii[i,j,0] = self.infl_ctp[i,j,i,j,0]
                self.infl_ctp_ii[i,j,1] = self.infl_ctp[i,j,i,j,1]
                self.infl_ctp_ii[i,j,2] = self.infl_ctp[i,j,i,j,2]
#        print('infl_ctp_ii[:,:,2]')
#        print(self.infl_ctp_ii[:,:,2])
        
        
# PLOT-2D #####################################################################
    def plot(self):
        plt.close()
        fig, ax = plt.subplots(figsize=(20,10))
        ax.set_xlim(-0.75*span,0.75*span)
        ax.set_ylim(-3*chord,chord)
        ax.set_aspect('equal')
        # plot nodes
        ax.plot(self.np_nodes[:,:,1], self.np_nodes[:,:,2], 'o', color='blue')
        for i in range(self.n_span):
            for j in range(self.n_chord+1+self.n_wake):
                ax.text(self.np_nodes[i,j,1]+0.04, self.np_nodes[i,j,2], int(self.np_nodes[i,j,0]), size=8)
                # plot control points
                ax.plot(self.np_ctp[:,:,1], self.np_ctp[:,:,2], 'o', color='red')
        for i in range(n_span-1):
            for j in range(n_chord):
                ax.text(self.np_ctp[i,j,1]+0.04, self.np_ctp[i,j,2], int(self.np_ctp[i,j,0]), size=8)
        # plot horizontal line segments
        for i in range(self.n_span-1):
            for j in range(self.n_chord+1+self.n_wake):
                ax.plot( ([self.np_lv_horz[i,j,2], self.np_lv_horz[i,j,5]]), ([self.np_lv_horz[i,j,3], self.np_lv_horz[i,j,6]]), color='orange')
                ax.text( (self.np_lv_horz[i,j,2] + self.np_lv_horz[i,j,5])/2, (self.np_lv_horz[i,j,3] + self.np_lv_horz[i,j,6])/2, int(self.np_lv_horz[i,j,0]), size=8, color='orange')
        # plot vertical line segments
        for i in range(n_span):
            for j in range(self.n_chord+self.n_wake):
                ax.plot( ([self.np_lv_vert[i,j,2], self.np_lv_vert[i,j,5]]), ([self.np_lv_vert[i,j,3], self.np_lv_vert[i,j,6]]), color='orange')
                ax.text( (self.np_lv_vert[i,j,2] + self.np_lv_vert[i,j,5])/2, (self.np_lv_vert[i,j,3] + self.np_lv_vert[i,j,6])/2, int(self.np_lv_vert[i,j,0]), size=8, color='orange')
        return
    
    
# CALCULATE ################################################################### 
    
    def sum_ctp_wash(self):
        np_wash_sum = np.zeros((self.n_span-1, self.n_chord-1))
        for i in range(self.n_span-1):
            for j in range(self.n_chord-1):
                wash = 0
                wash_sum = 0
                for k in range(self.n_span-1):
                    for l in range(self.n_chord):
                        wash = self.mu_total[k,l]*self.infl_ctp[i,j,k,l,:]
                        wash_sum = wash_sum+wash
#                        print('k')
#                        print(k)
#                        print('l')
#                        print(l)
#                        print('infl')
#                        print(infl)
#                        print(influence_sum)
                np_wash_sum[i,j]= wash_sum[2]
        return(np_wash_sum)
        
    
    def calc_doublet(self):
    # step 1. calculate the doublet distribution
        n = 20
        wash_sum = np.zeros((n_span-1, n_chord-1))
        for i in range(n):
#            print('i')
#            print(i)
#            print('self.RHS')
#            print(self.RHS)
#            print('wash_sum')
#            print(wash_sum)
            diff_mat = self.RHS - wash_sum
#            print('diff_mat')
#            print(diff_mat)
#            print('infl_ctp_ii')
#            print(self.infl_ctp_ii[:, 0:n_chord-1, 2])
            self.mu_gen = diff_mat/self.infl_ctp_ii[:, 0:n_chord-1, 2]
#            print('mu_gen')
#            print(self.mu_gen)
            # add the generated-doublet-distribution to the existing doublet distribution
            self.mu_total[:, 0:n_chord-1] = self.mu_total[:, 0:n_chord-1] + 0.6*self.mu_gen[:, 0:n_chord-1]
            
            # enforce kutta contition by creating first wake doublet with negative sign from trailing edge doublet
            self.mu_total[:, n_chord-1]   = self.mu_total[:, n_chord-2]
#            print('mu_total')
#            print(self.mu_total)
            wash_sum = self.sum_ctp_wash()
#            print('\nwash_sum')
#            print(wash_sum)
            
        print('\nmu_total')
        print(self.mu_total)
        return 
    
    # move the horizontal wake vortex lines strength back 1 row.  effectively translate the 2D wake strength matrix (index3 = 1) down 1 row in the lv_horz matrix
    def move_horz_wake_down_1_row(self):
        for i in range(self.n_wake+1):
            q = self.n_chord+self.n_wake-i
#            print('q')
#            print(q)
#            print('lv-horz')
#            print(self.np_lv_horz[:,q,1])
            self.np_lv_horz[:,q,1] = self.np_lv_horz[:,q-1,1]
        print('np_lv_horz wake moved down 1 row')
        print(self.np_lv_horz[:,:,1])
            
            
    def move_vert_wake_down_1_row(self):
        # step 4A. translate the trailing vert vortex down 1 time-step
        for i in range(self.n_chord+self.n_wake):
            q = n_chord-i
            if q == 0:
                self.np_lv_vert[:,q] = 0
            else:
                self.np_lv_vert[:,q] = self.np_lv_vert[:,q-1]
        print('\ntrail_vert moved 1 t_step')
        print(self.np_lv_vert[:,:,1])

        
    def doublet_to_horz(self):
        # step 2B. calculate the horizontal line vortex from doublets
        for i in range(self.n_span-1):
            for j in range(self.n_chord+1):
                if j == 0:
                    self.np_lv_horz[i,j,1] = self.np_lv_horz[i,j,1] + self.mu_total[i,j] 
                elif j < n_chord:
                    self.np_lv_horz[i,j,1] = self.np_lv_horz[i,j,1] + self.mu_total[i,j] - self.mu_total[i,j-1]
                elif j == n_chord:
                    self.np_lv_horz[i,j,1] = self.np_lv_horz[i,j,1] - self.mu_total[i,j-1]
                else:
                    print('error')
        
        print('np_lv_horz')
        print(self.np_lv_horz[:,:,1])
        
    
    def doublet_to_vert(self):
    # step 3. calculate the trailing vertical line-vortex from the generated doublets
        for i in range(self.n_span):
            for j in range(self.n_chord):
                if i == 0:
                    self.np_lv_vert[i,j,1] = self.np_lv_vert[i,j,1] - self.mu_total[i,j]
                elif i < n_chord:
                    self.np_lv_vert[i,j,1] = self.np_lv_vert[i,j,1] - self.mu_total[i,j] + self.mu_total[i-1,j]
                elif i == n_chord:
                    self.np_lv_vert[i,j,1] = self.np_lv_vert[i,j,1] + self.mu_total[i-1,j]
                else:
                    print('error')
        print('np_lv_vert')
        print(self.np_lv_vert[:,:,1])
    
        
    def fill_in_horseShoe_from_bound(self):
    # step 4B. fill in horseshoe from bound
        for i in range(self.n_span):
            for j in range(self.n_chord):
                if i == 0:
                    self.np_lv_vert[i,j] = self.np_lv_vert[i,j] - self.np_lv_horz[i,j]
                elif i < n_chord:
                    self.np_lv_vert[i,j] = self.np_lv_vert[i,j] - self.np_lv_horz[i,j] + self.np_lv_horz[i-1,j]
                elif i == n_chord:
                    self.np_lv_vert[i,j] = self.np_lv_vert[i,j] + self.np_lv_horz[i-1,j]
                else:
                    print('error')
        print('\nfill in horse shoe from bound')
        print(self.np_lv_vert[:,:,1])
        
# UPDATE WASH #################################################################
    # calculate wash from horizontal and verticle line vortex on control points
    # (line_vortex_stregth)*(influence_matrix_value)
    
    def update_wash_lv_horz(self):  
        for i in range(self.n_span-1):
            for j in range(self.n_chord-1):
                wash_sum = 0
                for k in range(self.n_span-1):
                    for l in range(self.n_chord+1+self.n_wake):
                        wash = (self.np_lv_horz[k,l,1])*(self.infl_lv_horz[i,j,k,l,2]) # np_lv_horz 3rd index = 1 for vortex strength
#                        print('wash')
#                        print(wash)
                        wash_sum = wash_sum + wash
                self.wash_lv_horz[i,j] = wash_sum
        print('\nwash_lv_horz')
        print(self.wash_lv_horz)
                
    def update_wash_lv_vert(self):
#        print('trail_horz')
#        print(self.trail_horz)
        for i in range(self.n_span-1):
            for j in range(self.n_chord-1):
                wash_sum = 0
                for k in range(self.n_span-1):
                    for l in range(self.n_chord+self.n_wake):
                        wash = (self.np_lv_horz[k,l,1])*(self.infl_lv_horz[i,j,k,l,2])
                        wash_sum = wash_sum + wash
                self.wash_lv_vert[i,j] = wash_sum
        print('\nwash_lv_vert')
        print(self.wash_lv_vert)
        
    def update_RHS(self):
        self.RHS = self.camberline - self.wash_lv_horz - self.wash_lv_vert
        print('\nRHS')
        print(self.RHS)
        


panel1 = panel(4,2,5,4,4,0.1)
panel1.plot()


for i in range(5):
    
    panel1.calc_doublet()
    panel1.doublet_to_horz()
    panel1.doublet_to_vert()
    panel1.move_horz_wake_down_1_row()
    panel1.move_vert_wake_down_1_row()
    panel1.fill_in_horseShoe_from_bound()
    panel1.update_wash_lv_horz()
    panel1.update_wash_lv_vert()
    panel1.update_RHS()








































