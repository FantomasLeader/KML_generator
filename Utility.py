import math

def pixel_to_latlon(x, y, offset_x, offset_y, min_col, max_row, zoom):
    """Convertir coordonnées pixel en lat/lon exprimés en degrés décimaux"""
    # Position dans l'image
    image_x = x - offset_x
    image_y = y - offset_y
    
    # Coordonnées de tuile integrant la position du point dans la tuile dans les décimales
    tile_x = image_x / 256 + min_col
    tile_y = max_row - image_y / 256
    
    # Conversion en lat/lon (correction TMS)
    n = 2 ** zoom
    lon = tile_x / n * 360.0 - 180.0    

    # Inverser tile_y pour TMS (Y=0 au pole sud)
    tile_y_corrected = n - 1 - tile_y
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y_corrected / n)))
    lat = math.degrees(lat_rad)
    
    return lat, lon

def decimal_to_dms(decimal):
    """Convertir degrés décimaux en degrés minutes"""
    degrees = int(abs(decimal))
    minutes = (abs(decimal) - degrees) * 60
    return degrees, minutes

def latlon_to_pixel(lat, lon, offset_x, offset_y, min_col, max_row, zoom):
    """Convertir lat/lon en coordonnées pixel dans le canvas"""
    n = 2 ** zoom
    
    # Conversion lon en tile_x
    tile_x = (lon + 180.0) / 360.0 * n
    
    # Conversion lat en tile_y (correction TMS)
    lat_rad = math.radians(lat)
    tile_y_corrected = (1 - math.asinh(math.tan(lat_rad)) / math.pi) / 2 * n
    tile_y = n - 1 - tile_y_corrected
    
    # Position dans l'image
    image_x = (tile_x - min_col) * 256
    image_y = (max_row - tile_y) * 256
    
    # Coordonnées pixel dans le canvas
    x = image_x + offset_x
    y = image_y + offset_y
    
    return x, y

def update_coordinates(x, y, offset_x, offset_y, min_col, max_row, zoom):
    """Récupère les coordonnées du pointeur de la souris en degrés"""
    return pixel_to_latlon(x, y, offset_x, offset_y, min_col, max_row, zoom)

def Cadre_coord(canvas_width, canvas_height, offset_x, offset_y, min_col, max_row, zoom):
    """Renvoie les coordonnées des coins du canvas visible au format image_x, image_y"""
    # Coin haut-gauche du canvas
    min_x = -offset_x
    min_y = -offset_y
    
    # Coin bas-droite du canvas
    max_x = canvas_width - offset_x
    max_y = canvas_height - offset_y
    
    return min_x, min_y, max_x, max_y

def create_point_from_bearing_distance(start_point, distance_km, bearing_deg):
    """Créer un point à partir d'un point de départ, distance et gisement (formule Vincenty)"""
    # Constantes WGS84
    WGS84_A = 6378137.0
    WGS84_F = 1/298.257223563
    WGS84_B = WGS84_A * (1 - WGS84_F)
    
    lat1_rad = math.radians(start_point["lat"])
    lon1_rad = math.radians(start_point["lon"])
    alpha1_rad = math.radians(bearing_deg)
    s = distance_km * 1000  # Convertir en mètres
    
    sin_alpha1, cos_alpha1 = math.sin(alpha1_rad), math.cos(alpha1_rad)
    tan_U1 = (1 - WGS84_F) * math.tan(lat1_rad)
    cos_U1 = 1 / math.sqrt(1 + tan_U1 ** 2)
    sin_U1 = tan_U1 * cos_U1
    
    sigma1 = math.atan2(tan_U1, cos_alpha1)
    sin_alpha = cos_U1 * sin_alpha1
    cos2_alpha = 1 - sin_alpha ** 2
    u2 = cos2_alpha * (WGS84_A ** 2 - WGS84_B ** 2) / (WGS84_B ** 2)
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    
    sigma = s / (WGS84_B * A)
    for _ in range(100):
        cos_2sigma_m = math.cos(2 * sigma1 + sigma)
        sin_sigma, cos_sigma = math.sin(sigma), math.cos(sigma)
        delta_sigma = B * sin_sigma * (cos_2sigma_m + B / 4 * (cos_sigma * (-1 + 2 * cos_2sigma_m ** 2) - B / 6 * cos_2sigma_m * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos_2sigma_m ** 2)))
        sigma_prev = sigma
        sigma = s / (WGS84_B * A) + delta_sigma
        
        if abs(sigma - sigma_prev) < 1e-12:
            break
    
    tmp = sin_U1 * sin_sigma - cos_U1 * cos_sigma * cos_alpha1
    lat2_rad = math.atan2(sin_U1 * cos_sigma + cos_U1 * sin_sigma * cos_alpha1, (1 - WGS84_F) * math.sqrt(sin_alpha ** 2 + tmp ** 2))
    lambda_val = math.atan2(sin_sigma * sin_alpha1, cos_U1 * cos_sigma - sin_U1 * sin_sigma * cos_alpha1)
    C = WGS84_F / 16 * cos2_alpha * (4 + WGS84_F * (4 - 3 * cos2_alpha))
    L = lambda_val - (1 - C) * WGS84_F * sin_alpha * (sigma + C * sin_sigma * (cos_2sigma_m + C * cos_sigma * (-1 + 2 * cos_2sigma_m ** 2)))
    lon2_rad = (lon1_rad + L + 3 * math.pi) % (2 * math.pi) - math.pi
    
    return math.degrees(lat2_rad), math.degrees(lon2_rad)

def convert_calamar_to_gps(x_val, y_val, x_unit, y_unit):
    """Convertit des coordonnées Calamar en GPS"""
    import numpy as np
    
    calamar_points = np.array([
        [0.0, 0.0],
        [683.0, 921.0],
        [284.73, -398.51]
    ])
    
    gps_points = np.array([
        [44.52041351, -1.11661145],
        [44.523935, -1.130166],
        [44.51600897, -1.11683657]
    ])
    
    y_calamar = x_val if x_unit == "mL" else -x_val
    x_calamar = y_val if y_unit == "mD" else -y_val
    
    A = np.column_stack([calamar_points, np.ones(3)])
    lat_params = np.linalg.lstsq(A, gps_points[:, 0], rcond=None)[0]
    lon_params = np.linalg.lstsq(A, gps_points[:, 1], rcond=None)[0]
    
    result_lat = lat_params[0] * y_calamar + lat_params[1] * x_calamar + lat_params[2]
    result_lon = lon_params[0] * y_calamar + lon_params[1] * x_calamar + lon_params[2]
    
    return result_lat, result_lon