def visualise_spatiotemporal_correlation_results(results):

	spatial_plot = {'z': results['spatial_corr'], 'x': results['longitudes'], 'y': results['latitudes'], 'type': 'contour', 'xaxis': 'x1', 'yaxis': 'y1', 
					'colorscale': 'plasma', 'zmax': 1, 'zmin': 0.5, 'colorbar': {'title': 'Corr', 'thickness': 10},
					'showlegend': False, 'contours': {'showlabels': True, 'labelfont': {'size': 6, 'color': 'black'}}}
	temporal_plot = {'x': results['temporal_corr']['lags'], 'y': results['temporal_corr']['corr'], 
					'marker': {'color': '#0E5A8A'}, 'xaxis': 'x2', 'yaxis': 'y2', 'showlegend': False}

	return {'data': [spatial_plot, temporal_plot], 'config': {'responsive': True}, 'layout': {'title': '<b>' + results['site_name'].replace('_', ' ') + '</b>', 
		'grid': {'rows': 2, 'columns': 1, 'pattern': 'independent'}, 
		'showlegend': False,
		'yaxis': {'domain': [0.4, 1], 'nticks': 5, 'tickfont': {'size': 10}, 'title': {'text': 'Latitude', 'font': {'size': 12}}, 'anchor': 'x1', 'scaleratio': 1},
		'xaxis2': {'anchor': 'y2', 'tickfont': {'size': 10}, 'title': {'text': 'Lag (Minutes)', 'font': {'size': 12}}},
		'xaxis': {'anchor': 'y1', 'nticks': 5, 'tickfont': {'size': 10}, 'title': {'text': 'Longitude', 'font': {'size': 12}}},
		'yaxis2': {'domain': [0, 0.2], 'tickfont': {'size': 10}, 'title': {'text': 'Correlation', 'font': {'size': 12}}, 'rangemode': 'tozero'},
		'autosize': True, 'width': 400}}