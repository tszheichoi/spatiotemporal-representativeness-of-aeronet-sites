import numpy as np
import pandas as pd
import datetime
import os
import utils

AERONET_METADATA_PATH = 'data/aeronet_metadata.csv'
AERONET_DATA_DIR = 'data/aeronet/'

metadata_df = pd.read_csv(AERONET_METADATA_PATH)

class AeronetMeasurements():

	@staticmethod
	def convert_to_datetime(row):
		return datetime.datetime.strptime(row['Date(dd:mm:yyyy)'] + ':' + row['Time(hh:mm:ss)'], '%d:%m:%Y:%H:%M:%S')

	def __init__(self, site_name, wavelengthsWithDirectMeasurements = [440, 500, 675, 870, 1020], verbose = True):
		if verbose: print('reading AERONET ground based measurements...')
		if (file_path := self._get_path_for_site(site_name)) is not None:
			self.df = pd.read_csv(file_path, header = None, names = utils.aeronet_header)
			match = metadata_df[metadata_df['Site Name'] == site_name + ' '] # note the extra space!
			assert not match.empty
			self.longitude = float(match['Long'])
			self.latitude = float(match['Lat'])
		else:
			print('unable to find a match')
			self.df = None
		if self.df is not None:
			self.df['timeStamp'] = self.df.apply(self.convert_to_datetime, axis = 'columns')
			self.df['timeStamp'] = [datetime.datetime.utcfromtimestamp(t) for t in (self.df['timeStamp'] - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')]

	def _get_path_for_site(self, siteName):
		path = AERONET_DATA_DIR + siteName + '.dat'
		if os.path.exists(path):
			print('the identified AERONET file is: %s'%(path))
			return path

	def perform_autocorrection_analysis(self, lags = range(-60, 60)):
		df = self.df.copy()
		df['timeStamp'] = pd.to_datetime(df['timeStamp'])
		df = df.set_index(['timeStamp'])
		for wvl in [440, 443, 412, 400, 490]:
			# _df = df[['AOD_%inm'%(wvl)]]
			_df = df[df['AOD_%inm'%(wvl)] != -999]
			if not _df.empty:
				print(f'using {wvl} nm for ecmwf')
				grouped = _df.groupby(_df.index.floor('d')).resample('T').mean()
				grouped = grouped.rename_axis(['days', 'time'])
				corr_func = lambda df: pd.Series([df['AOD_%inm'%(wvl)].autocorr(i) for i in lags])
				corr = []
				for _, columnData in grouped.groupby(level = 'days').apply(corr_func).iteritems():
					corr.append(np.nanmean(columnData))
				return corr, 
			else:
				print(f'{wvl} nm is unavailable, trying another one...')
