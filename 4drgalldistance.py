import os
import sys
import numpy as np
import nibabel as nib
from scipy.spatial.distance import pdist


img=nib.load("rest.nii.gz") 
data=img.get_data()



def region_growing(image,coordinate,number,measurement):
    """
    Give a coordinate ,return a region.
    """
    nt = number
    tmp_image = np.zeros_like(image[:,:,:,0])     #initialize all 0 image
    image_shape = image.shape
       
    x = coordinate[0]
    y = coordinate[1]
    z = coordinate[2]
    
    
    inside = (x>=0)and(x<image_shape[0])and(y>=0)and\
             (y<image_shape[1])and(z>=0)and(z<image_shape[2])
    if inside!=True:
        print "The coordinate is out of the image range."
        return False

    region_mean = image[x,y,z,:]     #the mean value

    region_size = 0              #the size of region
    voxel_distance = 0.0        #difference in neighbor_voxels

    neighbor_free = 10000      #longth of free space for list
    neighbor_pos = -1          #the position of seed voxel in list 
    neighbor_list = np.zeros((neighbor_free,4))   #create a list with 10000x4 

    neighbors  = [[1,0,0],\
                 [-1,0,0],\
                 [0,1,0],\
                 [0,-1,0],\
                 [0,0,-1],\
                 [0,0,1],\
                 [1,1,0],\
                 [1,1,1],\
                 [1,1,-1],\
                 [0,1,1],\
                 [-1,1,1],\
                 [1,0,1],\
                 [1,-1,1],\
                 [-1,-1,0],\
                 [-1,-1,-1],\
                 [-1,-1,1],\
                 [0,-1,-1],\
                 [1,-1,-1],\
                 [-1,0,-1],\
                 [-1,1,-1],\
                 [0,1,-1],\
                 [0,-1,1],\
                 [1,0,-1],\
                 [1,-1,0],\
                 [-1,0,1],\
                 [-1,1,0]]

    while region_size < nt:       # the size of region < nt
        
        for i in range(6):        #do it for 6 times
            xn = x + neighbors[i][0]
            yn = y + neighbors[i][1]
            zn = z + neighbors[i][2]
   
            inside = (xn>=0)and(xn<image_shape[0])and(yn>=0)and(yn<image_shape[1])and(zn>=0)and(zn<image_shape[2])       #coordinate is not out of range
        
            
            if inside and tmp_image[xn,yn,zn]==0:     #the original flag 0 is not changed
                neighbor_pos = neighbor_pos+1        #the position of new voxel in list
                X=[image[xn,yn,zn,:],region_mean]
                neighbor_list[neighbor_pos] = [xn,yn,zn,pdist(X,measurement)]   #put (x,y,z,value) into 4-dimensions list
                tmp_image[xn,yn,zn] = 1            #voxel in 4-dimensions list with flag 1
                
       
        
        if (neighbor_pos+100 > neighbor_free):   #if the longth of list is not enough
            neighbor_free +=10000                #add another 10000 
            new_list = np.zeros((10000,4))
      
            neighbor_list = np.vstack((neighbor_list,new_list))   #connect the two lists
        
        distance = neighbor_list[:neighbor_pos+1,3]
       #n+1 neighbor_voxels' value - n+1 mean values      
        
        voxel_distance = distance.min() #choose the min difference voxel
        index = distance.argmin()    #the index of min difference voxel 
      
        
        tmp_image[x,y,z] = 2   #segmental region with flag 2
        region_size += 1      #increase the region_size
        
        x = neighbor_list[index][0]   #
        y = neighbor_list[index][1]
        z = neighbor_list[index][2]
        
        region_mean = (region_mean*region_size+image[x,y,z,:])/(region_size+1)   #refresh the mean value
       
        
        neighbor_list[index] = neighbor_list[neighbor_pos]   #the head of list ---> the min difference voxel in the list
        neighbor_pos -= 1  #the number of voxels in the neighbor_list decrease 1

   
    for i in range(image_shape[0]):
        for j in range(image_shape[1]):
            for k in range(image_shape[2]):
                if tmp_image[i,j,k]!=2:
                    image[i,j,k]=0    #only segmental region with flag 2(>1)
    return image,region_size

print "there are ten measurement standards to choose,('euclidean', 'cityblock' ,'seuclidean', 'sqeuclidean' , 'cosine' , 'correlation' , 'hamming' , 'jaccard' , 'chebyshev' , 'canberra' , 'braycurtis')"
output1=raw_input("input the measurement standard:")
region,num = region_growing(data,(22,22,9),100,output1)   #use the function
img._data= region
output2=raw_input("input your file name : ")
nib.save(img,output2+".nii.gz")

