from geopy.distance import geodesic

def calculate_distance(dataframe, tuple):
    lat1 = dataframe.loc[tuple[0], 'latitude']
    lon1 = dataframe.loc[tuple[0], 'longitude']
    lat2 = dataframe.loc[tuple[1], 'latitude']
    lon2 = dataframe.loc[tuple[1], 'longitude']
    return tuple[0], tuple[1], geodesic((lat1, lon1), (lat2, lon2)).km
