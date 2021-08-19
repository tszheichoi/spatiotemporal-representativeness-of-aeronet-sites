from datetime import datetime, timedelta
import numpy as np
import netCDF4

EPOCH = datetime(1900, 1, 1, 00, 00, 00)

class SurfaceAOD:
	def __init__(self, path):
		f = netCDF4.Dataset(path, scale = True) 
		self.time = np.asarray(f.variables['time'][:]).astype(float)
		self.time = EPOCH + np.vectorize(timedelta)(hours = self.time) #convert to datetime first
		self.lat = np.asarray(f.variables['latitude'][:])
		self.lon = np.asarray(f.variables['longitude'][:])
		self.aod469 = np.asarray(f.variables['aod469'][:])
		self.aod550 = np.asarray(f.variables['aod550'][:])
		self.aod670 = np.asarray(f.variables['aod670'][:])
		self.aod865 = np.asarray(f.variables['aod865'][:])
		self.aod1240 = np.asarray(f.variables['aod1240'][:])
		self.aods = {469: self.aod469, 550: self.aod550, 670: self.aod670, 865: self.aod865, 1240: self.aod1240}
		assert len(self.lon) == len(self.lat)
		self.dimension = len(self.lon)

	def get_spatial_index(self, lon, lat):
		lon_index = (np.abs(self.lon - lon)).argmin()
		lat_index = (np.abs(self.lat - lat)).argmin()
		return [lon_index, lat_index]

	def get_aod_timeseries(self, wavelength, lon, lat):
		[lon_index, lat_index] = self.get_spatial_index(lon, lat)
		if int(wavelength) in self.aods.keys():
			return self.aods[int(wavelength)][:, lat_index, lon_index]
		else:
			raise Exception('cannot fetch timeseries directly at channels that are not directly provided by the IFS')