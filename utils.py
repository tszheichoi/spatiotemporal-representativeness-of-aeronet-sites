import os
import fnmatch
from math import pi, cos, radians
import numpy as np

def reproject(latitude, longitude):
    """Returns the x and y coordinates in meters using a sinusoidal projection"""
    earth_radius = 6371.009 # in meters
    lat_dist = pi * earth_radius / 180.0

    y = [lat * lat_dist for lat in latitude]
    x = [long * lat_dist * cos(radians(lat)) 
                for lat, long in zip(latitude, longitude)]
    return x, y

def RGB_to_Hex(rgba):
    strs = '#'
    for i in rgba[:3]:
        num = int(i)
        strs += str(hex(num))[-2:].replace('x','0').upper()
    assert type(strs) == str
    return strs

def area_of_polygon(x, y):
    """Calculates the area of an arbitrary polygon given its verticies"""
    area = 0.0
    for i in range(-1, len(x)-1):
        area += x[i] * (y[i+1] - y[i-1])
    return abs(area) / 2.0

def get_nc_files_recursively(base_path):
    return [os.path.join(dirpath, f)
            for dirpath, dirnames, files in os.walk(base_path)
            for f in fnmatch.filter(files, '*.nc')]

def get_nc_files_recursively_with_starting_name(base_path, starting_name):
    allNCPathsToCheck = get_nc_files_recursively(base_path)
    return [(p, p.split('/')[-1].split('_')[-2], p.split('/')[-1].split('_')[-1].split('.')[0]) for p in allNCPathsToCheck if '_'.join(p.split('/')[-1].split('_')[:-2]) == starting_name]

def get_area_of_polygon(lons, lats):
    x, y = reproject(lons, lats)
    return area_of_polygon(x, y)

def nan_helper(y):
    return np.isnan(y), lambda z: z.nonzero()[0]

aeronet_header = ['AERONET_Site','Date(dd:mm:yyyy)','Time(hh:mm:ss)','Day_of_Year','Day_of_Year(Fraction)',
                'AOD_1640nm','AOD_1020nm','AOD_870nm','AOD_865nm','AOD_779nm','AOD_675nm','AOD_667nm','AOD_620nm',
                'AOD_560nm','AOD_555nm','AOD_551nm','AOD_532nm','AOD_531nm','AOD_510nm','AOD_500nm','AOD_490nm',
                'AOD_443nm','AOD_440nm','AOD_412nm','AOD_400nm','AOD_380nm','AOD_340nm','Precipitable_Water(cm)',
                'AOD_681nm','AOD_709nm','AOD_Empty_1','AOD_Empty_2','AOD_Empty_3','AOD_Empty_4','AOD_Empty_5',
                'Triplet_Variability_1640','Triplet_Variability_1020','Triplet_Variability_870','Triplet_Variability_865',
                'Triplet_Variability_779','Triplet_Variability_675','Triplet_Variability_667','Triplet_Variability_620',
                'Triplet_Variability_560','Triplet_Variability_555','Triplet_Variability_551','Triplet_Variability_532',
                'Triplet_Variability_531','Triplet_Variability_510','Triplet_Variability_500','Triplet_Variability_490',
                'Triplet_Variability_443','Triplet_Variability_440','Triplet_Variability_412','Triplet_Variability_400',
                'Triplet_Variability_380','Triplet_Variability_340','Triplet_Variability_Precipitable_Water(cm)',
                'Triplet_Variability_681','Triplet_Variability_709','Triplet_Variability_AOD_Empty_1','Triplet_Variability_AOD_Empty_2',
                'Triplet_Variability_AOD_Empty_3','Triplet_Variability_AOD_Empty_4','Triplet_Variability_AOD_Empty_5',
                '440-870_Angstrom_Exponent','380-500_Angstrom_Exponent','440-675_Angstrom_Exponent',
                '500-870_Angstrom_Exponent','340-440_Angstrom_Exponent','440-675_Angstrom_Exponent[Polar]',
                'Data_Quality_Level','AERONET_Instrument_Number','AERONET_Site_Name',
                'Site_Latitude(Degrees)','Site_Longitude(Degrees)','Site_Elevation(m)','Solar_Zenith_Angle(Degrees)',
                'Optical_Air_Mass','Sensor_Temperature(Degrees_C)','Ozone(Dobson)','NO2(Dobson)',
                'Last_Date_Processed','Number_of_Wavelengths','Exact_Wavelengths_of_AOD(um)_1640nm',
                'Exact_Wavelengths_of_AOD(um)_1020nm','Exact_Wavelengths_of_AOD(um)_870nm','Exact_Wavelengths_of_AOD(um)_865nm',
                'Exact_Wavelengths_of_AOD(um)_779nm','Exact_Wavelengths_of_AOD(um)_675nm','Exact_Wavelengths_of_AOD(um)_667nm',
                'Exact_Wavelengths_of_AOD(um)_620nm','Exact_Wavelengths_of_AOD(um)_560nm','Exact_Wavelengths_of_AOD(um)_555nm',
                'Exact_Wavelengths_of_AOD(um)_551nm','Exact_Wavelengths_of_AOD(um)_532nm','Exact_Wavelengths_of_AOD(um)_531nm',
                'Exact_Wavelengths_of_AOD(um)_510nm','Exact_Wavelengths_of_AOD(um)_500nm','Exact_Wavelengths_of_AOD(um)_490nm',
                'Exact_Wavelengths_of_AOD(um)_443nm','Exact_Wavelengths_of_AOD(um)_440nm','Exact_Wavelengths_of_AOD(um)_412nm',
                'Exact_Wavelengths_of_AOD(um)_400nm','Exact_Wavelengths_of_AOD(um)_380nm','Exact_Wavelengths_of_AOD(um)_340nm',
                'Exact_Wavelengths_of_PW(um)_935nm','Exact_Wavelengths_of_AOD(um)_681nm','Exact_Wavelengths_of_AOD(um)_709nm',
                'Exact_Wavelengths_of_AOD(um)_Empty_1','Exact_Wavelengths_of_AOD(um)_Empty_2','Exact_Wavelengths_of_AOD(um)_Empty_3',
                'Exact_Wavelengths_of_AOD(um)_Empty_4','Exact_Wavelengths_of_AOD(um)_Empty_5']
