import matplotlib
matplotlib.use('Agg')

from utils import get_nc_files_recursively_with_starting_name, get_area_of_polygon, nan_helper
import matplotlib.pyplot as plt
import numpy as np
import ecmwf
import aeronet
from scipy import stats
import matplotlib.path as mplPath
import json
import plotly.graph_objects as go
from visualisation import visualise_spatiotemporal_correlation_results

season_converter = {'12': 'DJF', '01': 'DJF', '02': 'DJF', '03': 'MAM', '04': 'MAM', '05': 'MAM', '06': 'JJA', '07': 'JJA', '08': 'JJA', '09': 'SON', '10': 'SON', '11': 'SON'}

spatial_contour_levels = list(np.arange(0.6, 1.0, 0.025)) + [0.99] # these are the correlation levels at which we will compute the contour lines spatially

temporal_lags = list(range(-60, 60)) # in minutes

def determine_variability_at_site(site_name, season = 'ALL', json_dump_results = False):
	"""
	Determine the spatiotemporal variability of a given aeronet site

	Input
		site_name (str): name of aeronet site
		season (str): one of ['ALL', 'DJF', 'MAM', 'JJA', 'SON']
		json_dump_results (bool): whether or not to save the json out to results
	Return
		results (dict): dictionary of spatial and temporal correlation results
	"""
	assert season in ['ALL', 'DJF', 'MAM', 'JJA', 'SON']

	print(f'processing site: {site_name}')
	site_characteristics = {'site_name': site_name}
	
	matched_paths = get_nc_files_recursively_with_starting_name('data/ecmwf', site_name)
	if len(matched_paths) == 0:
		print('Unable to find any corresponding ecmwf .nc files')
		site_characteristics['success'] = False
		return

	aeronet_obs = aeronet.AeronetMeasurements(site_name)
	lon, lat = aeronet_obs.longitude, aeronet_obs.latitude
	if aeronet_obs.df.empty: # unable to find a match
		print('Unable to find any corresponding aeronet observation')
		site_characteristics['success'] = False
		return

	site_characteristics['site_lon'], site_characteristics['site_lat'] = lon, lat

	selected_paths = {}
	for mp in matched_paths:
		year, month = mp[1], '{:02d}'.format(int(mp[2]))
		year_month = year + month
		if (season == 'ALL') or (season == season_converter[month]):
			selected_paths[year_month] = mp[0]

	if len(selected_paths) == 0:
		print(f'No ecmwf .nc files after sub-selecting by season {season}')

	site_characteristics['success'] = True
	site_characteristics['num_of_matched_months'] = len(selected_paths)
		
	print('determining spatial variability...')
	grid_timeseries, spot_timeseries = [], []
	for _, path in selected_paths.items():
		ecmwf_surface_aod = ecmwf.SurfaceAOD(path)
		spot_timeseries.extend(ecmwf_surface_aod.get_aod_timeseries(469, lon, lat))
		grid_timeseries.extend(ecmwf_surface_aod.aod469) 
	grid_timeseries = np.ndarray.tolist((np.asarray(grid_timeseries).transpose())) # [time][lat][lon] -> [lon][lat][time]
	
	pearson_r = np.zeros((ecmwf_surface_aod.dimension, ecmwf_surface_aod.dimension))
	p_val = np.zeros((ecmwf_surface_aod.dimension, ecmwf_surface_aod.dimension))
	for i in range(0, ecmwf_surface_aod.dimension):
		for j in range(0, ecmwf_surface_aod.dimension):
			assert len(spot_timeseries) == len(grid_timeseries[j][i])
			(pearson_r[j][i], p_val[j][i]) = stats.pearsonr(spot_timeseries, grid_timeseries[j][i])

	site_characteristics['spatial_corr'] = np.squeeze(pearson_r.transpose()).tolist()
	site_characteristics['p_vals'] = np.squeeze(p_val.transpose()).tolist()
	site_characteristics['longitudes'] = ecmwf_surface_aod.lon.tolist()
	site_characteristics['latitudes'] = ecmwf_surface_aod.lat.tolist()

	contours = plt.contour(ecmwf_surface_aod.lon, ecmwf_surface_aod.lat, pearson_r.transpose(), levels = spatial_contour_levels)
	
	site_characteristics['contours'] = {}
	for cs, threshold in zip(reversed(contours.collections), reversed(spatial_contour_levels)):
		if len(cs.get_paths()) == 1: #closed path available
			_lons, _lats = list(cs.get_paths()[0].vertices[:,0]), list(cs.get_paths()[0].vertices[:,1])
			area = get_area_of_polygon(_lons, _lats)
			if mplPath.Path(list(map(list, zip(*[_lons, _lats])))).contains_point((site_characteristics['site_lon'], site_characteristics['site_lat'])) or threshold == 0.99:
				print(f'contour threshold {float(threshold)} has {len(cs.get_paths())} paths with enclosed area {area}')
				site_characteristics['contours'][threshold] = {'lon': _lons, 'lat': _lats, 'area': area}
			else: # path does not enclose the site, ignoring
				pass
		else: #clipped path, ignoring
			pass

	print('determining temporal variability...')
	corr = aeronet_obs.perform_autocorrection_analysis(temporal_lags)
	site_characteristics['temporal_corr'] = {'corr': corr[0], 'lags': temporal_lags}

	if json_dump_results:
		print('json dumping results...')
		with open('results/%s.json'%(site_name), 'w') as outfile:
			json.dump(site_characteristics, outfile)

	return site_characteristics

if __name__ == "__main__":
	site = 'Tamanrasset_TMP'
	results = determine_variability_at_site(site, json_dump_results = True)
	go.Figure(visualise_spatiotemporal_correlation_results(results)).write_image(f'plots/{site}.png', scale = 2)