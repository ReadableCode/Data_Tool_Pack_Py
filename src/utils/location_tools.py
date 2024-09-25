# %%
# Running Imports #

import math
import os
import pickle  # Import pickle for cache persistence
import sys

import folium
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

# append grandparent
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_utils import data_dir  # noqa: F401

# %%
# Variables #

cache_file_path = os.path.join(
    data_dir, "location_cache.pkl"
)  # Define the path to the cache file

# Load existing cache if available
if os.path.exists(cache_file_path):
    with open(cache_file_path, "rb") as f:
        dict_location_coords = pickle.load(f)
        print("Cache loaded from file.")
else:
    dict_location_coords = {}
    print("No cache file found, starting with an empty cache.")

# Initialize Nominatim API and rate limit
geolocator = Nominatim(user_agent="te_metrics")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# %%
# Functions #


def save_cache():
    """
    Saves the current location cache to a file.
    """
    with open(cache_file_path, "wb") as f:
        pickle.dump(dict_location_coords, f)
    print("Cache saved to file.")


def get_coordinates(location_name):
    """
    Retrieves the geographic coordinates (latitude and longitude) for a given location name.

    The function checks if the coordinates are cached; if not, it queries the Nominatim API.
    Caches the result for future use.

    Args:
        location_name (str): The name of the location to retrieve coordinates for.

    Returns:
        tuple or None: A tuple (latitude, longitude) if found, otherwise `None`.

    Example:
        >>> get_coordinates("San Francisco California")
        (37.7792588, -122.4193286)
    """
    if location_name in dict_location_coords:
        return dict_location_coords[location_name]

    print(f"Location {location_name} not found in cache, querying Nominatim API")

    location = geocode(location_name)
    if location is None:
        print(f"Location {location_name} not found in Nominatim API")
        dict_location_coords[location_name] = (None, None)
        save_cache()
        return None, None
    else:
        dict_location_coords[location_name] = (location.latitude, location.longitude)

        # Save the cache after updating
        save_cache()

        return location.latitude, location.longitude


def get_miles_from_km(km):
    """
    Converts kilometers to miles.

    Args:
        km (float): The distance in kilometers.

    Returns:
        float: The distance in miles.
    """
    return km * 0.621371


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the great-circle distance between two points on the Earth's surface.

    This function uses the Haversine formula to compute the shortest distance over the Earth's surface
    between two latitude/longitude points, assuming a spherical Earth.

    Args:
        lat1 (float): Latitude of the first point in decimal degrees.
        lon1 (float): Longitude of the first point in decimal degrees.
        lat2 (float): Latitude of the second point in decimal degrees.
        lon2 (float): Longitude of the second point in decimal degrees.

    Returns:
        float: Distance between the two points in kilometers.

    Example:
        >>> haversine_distance(37.7749, -122.4194, 34.0522, -118.2437)
        559.1205770615534
    """
    # Radius of the Earth in kilometers (mean radius)
    EARTH_RADIUS = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = EARTH_RADIUS * c

    return distance


def get_nearest_location(lat, lon, dict_locs):
    """
    Finds the nearest location from a dictionary of locations to the specified latitude and longitude.

    Calculates the great-circle distance between a given point (latitude and longitude) and a set of predefined
    locations. Returns the name of the nearest location and the distance to it.

    Args:
        lat (float): Latitude of the reference point.
        lon (float): Longitude of the reference point.
        dict_locs (dict): A dictionary of locations, where each key is the location's name and the value is a
            dictionary containing location details, including 'coordinates' as a tuple (latitude, longitude).

            Example format:
            {
            "8 Vreeland Ave, Totowa, NJ": {
                "property_type": "HelloFresh Properties",
                "is_dc": "TRUE",
                "city": "Totowa",
                "state": "NJ",
                "country": "US",
                "location_string": "8 Vreeland Ave, Totowa, NJ (DC)",
                "coordinates": "(40.9019486481544, -74.2381174722316)",
                "latitude": 40.90194865,
                "longitude": -74.23811747
            },
            "60 Lister Ave, Newark, NJ": {
                "property_type": "HelloFresh Properties",
                ...
            }

    Returns:
        tuple: A tuple containing:
            - str: The name of the nearest location.
            - float: The distance to the nearest location in kilometers.
            - float: The latitude of the nearest location.
            - float: The longitude of the nearest location.
    """
    nearest_location = None
    nearest_distance = None
    nearest_loc_lat = None
    nearest_loc_lon = None

    for loc, loc_data in dict_locs.items():
        coords = loc_data["coordinates"]
        if coords:
            loc_lat, loc_lon = loc_data["coordinates"]
            distance = haversine_distance(lat, lon, loc_lat, loc_lon)
            if nearest_distance is None or distance < nearest_distance:
                nearest_location = loc
                nearest_distance = distance
                nearest_loc_lat = loc_lat
                nearest_loc_lon = loc_lon

    return nearest_location, nearest_distance, nearest_loc_lat, nearest_loc_lon


def get_map_of_coords(ls_coords, ls_names=None, center_map_at=None):
    """
    Generates a map with markers for a list of coordinates.

    Creates a map using the Folium library and adds markers for each set of coordinates in the list.

    Args:
        ls_coords (list): A list of tuples containing the latitude and longitude of each location.
        ls_names (list): A list of location names corresponding to the coordinates.
        center_map_at (tuple): A tuple containing the latitude and longitude to center the map at.

    Returns:
        folium.Map: A Folium map object with markers for each set of coordinates.
    """
    # Create a map centered at the specified location
    if center_map_at:
        map_center = center_map_at
    else:
        # center of US
        map_center = (39.8283, -98.5795)

    m = folium.Map(location=map_center, zoom_start=5)

    for i, (lat, lon) in enumerate(ls_coords):
        if ls_names and i < len(ls_names):
            name = ls_names[i]
        else:
            name = f"Location {i+1}"

        folium.Marker([lat, lon], popup=name).add_to(m)

    return m


# %%
