import os, sys
from netCDF4 import Dataset
import numpy as np
import IOverticalGrid
import interp2D
from datetime import datetime, timedelta
from netCDF4 import num2date, date2num
import printObject

""" Get self made modules"""
dir='/Users/trond/Projects/PyLIB'

if os.path.isdir(dir):
    sys.path.append(dir)
import date
import geoProjection
import grd

__author__   = 'Trond Kristiansen'
__email__    = 'trond.kristiansen@imr.no'
__created__  = datetime(2008, 8, 15)
__modified__ = datetime(2008, 8, 19)
__modified__ = datetime(2008, 10, 22)
__version__  = "1.1"
__status__   = "Development"

def find_subset_indices(grdSODA,min_lat,max_lat,min_lon,max_lon):
    """
    Get the indices that covers the new grid, and enables us to only store a subset of
    the large input grid.
    """
    lat=grdSODA.lat[:,0]
    lon=grdSODA.lon[0,:]
    
    distances1 = []
    distances2 = []
    indices=[]
    index=0
    for point in lat:
        s1 = max_lat-point # (vector subtract)
        s2 = min_lat-point # (vector subtract)
        distances1.append((np.dot(s1, s1), point, index))
        distances2.append((np.dot(s2, s2), point, index))
        index=index+1
        
    distances1.sort()
    distances2.sort()
    indices.append(distances1[0])
    indices.append(distances2[0])
    
    distances1 = []
    distances2 = []
    index=0
   
    for point in lon:
        s1 = max_lon-point # (vector subtract)
        s2 = min_lon-point # (vector subtract)
        distances1.append((np.dot(s1, s1), point, index))
        distances2.append((np.dot(s2, s2), point, index))
        index=index+1
       
    distances1.sort()
    distances2.sort()
    indices.append(distances1[0])
    indices.append(distances2[0])
    
    """ Save final product: max_lat_indices,min_lat_indices,max_lon_indices,min_lon_indices"""
      
    grdSODA.minJ=indices[1][2]
    grdSODA.maxJ=indices[0][2]
    grdSODA.minI=indices[3][2]
    grdSODA.maxI=indices[2][2]
    
  
def convertSODA2ROMS(years,IDS):
    """
    Initial global path names etc.
    """
    log=True
  
    fileNameOut="/Users/trond/ROMS/GoM/grid/gom_grd.nc"
    #fileNameOut="/Users/trond/Projects/arcwarm/nordic/AA_10km_grid.nc"
    sodapath="/Volumes/HankRaid/SODA/"
    sodapath="/Users/trond/Projects/arcwarm/SODA/DATA/"
    missing=["SODA_2.0.2_1958_8.cdf", "SODA_2.0.2_1958_9.cdf", "SODA_2.0.2_1959_8.cdf", "SODA_2.0.2_1959_9.cdf", "SODA_2.0.2_1981_44.cdf","SODA_2.0.2_1958_53.cdf","SODA_2.0.2_1958_63.cdf"]
    fileNameIn=sodapath+"SODA_2.0.2_1963_1.cdf"
    
    
    """First time in loop, get the essential old grid information"""
    """SODA data already at Z-levels. No need to interpolate to fixed depths, but we use the one we have"""
    
    grdSODA = grd.grdClass(fileNameIn,"SODA",log)
    IOverticalGrid.get_z_levels(grdSODA)
            
    #print printObject.dumpObj(grdSODA)
    
    
    grdROMS = grd.grdClass(fileNameOut,"ROMS",log)
    IOverticalGrid.calculate_z_r(grdROMS)
    IOverticalGrid.calculate_z_w(grdROMS)
    
    #print printObject.dumpObj(grdROMS)

    """Now we want to subset the data to avoid storing more information than we need.
    We do this by finding the indices of maximum and minimum latitude and longitude in the matrixes"""
    find_subset_indices(grdSODA,min_lat=30, max_lat=90, min_lon=0, max_lon=360)
    
    
    
    grdSODA.lat=grdSODA.lat[grdSODA.minJ:grdSODA.maxJ,grdSODA.minI:grdSODA.maxI]
    grdSODA.lon=grdSODA.lon[grdSODA.minJ:grdSODA.maxJ,grdSODA.minI:grdSODA.maxI]
    """Convert values larger than 180 into negative values (West)"""
    grdSODA.lon[:,:]=np.where(grdSODA.lon>180,grdSODA.lon[:,:]-360.,grdSODA.lon[:,:])

    
    
    if grdSODA.log is True:
        print "\nSelected area in output file spans from (longitude=%3.2f,latitude=%3.2f) to (longitude=%3.2f,latitude=%3.2f)"%(grdROMS.lon_rho.min(),grdROMS.lat_rho.min(),grdROMS.lon_rho.max(),grdROMS.lat_rho.max())
        print "Selected area in input file spans from  (longitude=%3.2f,latitude=%3.2f) to (longitude=%3.2f,latitude=%3.2f)\n"%(grdSODA.lon.min(),grdSODA.lat.min(),grdSODA.lon.max(),grdSODA.lat.max())
    
    """
    Create a date object to keep track of Julian dates etc.
    Also create a reference date starting at 1948/01/01.
    """
    date_obj = date.Date()
    ref_date = date.Date()
    ref_date.day=1
    ref_date.month=1
    ref_date.year=1948
    jdref=ref_date.ToJDNumber()
    
       
    """
    Project the input grid onto the output grid to enable a straight-forward bilinear interpolation
    """
    map=geoProjection.stereographic_wedge(-65.0,52.0,-71.0,47.2,0.15)
         
   
    if grdSODA.log is True:
        print "Reference date is set to: (%s,%s,%s) => julian day: %s"%(ref_date.year,ref_date.month,ref_date.day,jdref)
    for year in years:
        print "Working on year %s"%(year)
        
        firstRun = True
        time=0
        
        for ID in IDS:
            file="SODA_2.0.2_"+str(year)+"_"+str(ID)+".cdf"
            filename=sodapath+file
         
            if file not in missing:
             
                cdf = Dataset(filename)

                """Each SODA file consist only of one time step. Get the subset data selected, and
                store that time step in a new array:"""
                temp        = np.array(cdf.variables["TEMP"][:,:,grdSODA.minJ:grdSODA.maxJ,grdSODA.minI:grdSODA.maxI])
                salt        = np.array(cdf.variables["SALT"][:,:,grdSODA.minJ:grdSODA.maxJ,grdSODA.minI:grdSODA.maxI])
                uvel        = np.array(cdf.variables["U"][:,:,grdSODA.minJ:grdSODA.maxJ,grdSODA.minI:grdSODA.maxI])
                vvel        = np.array(cdf.variables["V"][:,:,grdSODA.minJ:grdSODA.maxJ,grdSODA.minI:grdSODA.maxI])
             
                cdf.close()
                
                if firstRun is True:
                    firstRun = False
                    indexSODA = (len(IDS),temp.shape[1],temp.shape[2],temp.shape[3])
                    indexROMS = (len(IDS),temp.shape[1],grdROMS.depth.shape[0],grdROMS.depth.shape[1])
                    print indexROMS
                    
                    grdSODA.t=np.zeros((indexSODA),float)
                    grdSODA.s=np.zeros((indexSODA),float)
                    grdSODA.u=np.zeros((indexSODA),float)
                    grdSODA.v=np.zeros((indexSODA),float)
                    
                    grdROMS.t=np.zeros((indexROMS),float)
                    grdROMS.s=np.zeros((indexROMS),float)
                    grdROMS.u=np.zeros((indexROMS),float)
                    grdROMS.v=np.zeros((indexROMS),float)
                    
                grdSODA.t[time,:,:,:]=temp
                grdSODA.s[time,:,:,:]=salt
                grdSODA.u[time,:,:,:]=uvel
                grdSODA.v[time,:,:,:]=vvel
                time+=1
                
        interp2D.doInterpolation(grdROMS,grdSODA.t,grdSODA.lon,grdSODA.lat,grdROMS.Lp,grdROMS.Mp,map,time,len(grdSODA.depth))
        ID=1
   

def main():
    
    start_year=1960
    end_year=1961
    start_day_in_start_year=10
    end_day_in_end_year=65
    
    years=[(int(start_year)+kk) for kk in range(int(end_year)-int(start_year))]
    
   # IDS=[(math.ceil(start_day_in_start_year/5.0)+i) for i in range(73)]
    IDS=[(i+1) for i in range(1)]
    
    convertSODA2ROMS(years,IDS)
             

if __name__ == "__main__":
    import profile
    
    try:
        import psyco
        psyco.log()
        psyco.profile(0.2)

    except ImportError:
        pass
    #profile.run('main()')
    
    main()