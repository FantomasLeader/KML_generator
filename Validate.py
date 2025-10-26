def validate_coords(viewer):
    """Valider le format des coordonnées en temps réel"""
    lat_text = viewer.lat_entry.get()
    lon_text = viewer.lon_entry.get()
    
    # Validation latitude
    lat_valid = True
    if lat_text:
        try:
            lat = float(lat_text)
            if not (-90 <= lat <= 90):
                lat_valid = False
        except ValueError:
            lat_valid = False
    
    # Validation longitude
    lon_valid = True
    if lon_text:
        try:
            lon = float(lon_text)
            if not (-180 <= lon <= 180):
                lon_valid = False
        except ValueError:
            lon_valid = False
    
    # Changer la couleur selon la validité
    viewer.lat_entry.config(bg="white" if lat_valid else "#ffcccc")
    viewer.lon_entry.config(bg="white" if lon_valid else "#ffcccc")

def validate_deg_min(viewer):
    """Valider le format degrés/minutes"""
    # Validation latitude
    lat_deg_valid = True
    lat_min_valid = True
    
    lat_deg_text = viewer.lat_deg_entry.get()
    lat_min_text = viewer.lat_min_entry.get()
    
    if lat_deg_text:
        try:
            lat_deg = int(lat_deg_text)
            if not (0 <= lat_deg <= 90):
                lat_deg_valid = False
        except ValueError:
            lat_deg_valid = False
    
    if lat_min_text:
        try:
            lat_min = float(lat_min_text)
            if not (0 <= lat_min < 60):
                lat_min_valid = False
        except ValueError:
            lat_min_valid = False
    
    # Validation longitude
    lon_deg_valid = True
    lon_min_valid = True
    
    lon_deg_text = viewer.lon_deg_entry.get()
    lon_min_text = viewer.lon_min_entry.get()
    
    if lon_deg_text:
        try:
            lon_deg = int(lon_deg_text)
            if not (0 <= lon_deg <= 180):
                lon_deg_valid = False
        except ValueError:
            lon_deg_valid = False
    
    if lon_min_text:
        try:
            lon_min = float(lon_min_text)
            if not (0 <= lon_min < 60):
                lon_min_valid = False
        except ValueError:
            lon_min_valid = False
    
    # Changer les couleurs
    viewer.lat_deg_entry.config(bg="white" if lat_deg_valid else "#ffcccc")
    viewer.lat_min_entry.config(bg="white" if lat_min_valid else "#ffcccc")
    viewer.lon_deg_entry.config(bg="white" if lon_deg_valid else "#ffcccc")
    viewer.lon_min_entry.config(bg="white" if lon_min_valid else "#ffcccc")

def validate_deg_min_sec(viewer):
    """Valider le format degrés/minutes/secondes"""
    # Validation latitude
    lat_deg_valid = True
    lat_min_valid = True
    lat_sec_valid = True
    
    lat_deg_text = viewer.lat_deg_entry.get()
    lat_min_text = viewer.lat_min_entry.get()
    lat_sec_text = viewer.lat_sec_entry.get()
    
    if lat_deg_text:
        try:
            lat_deg = int(lat_deg_text)
            if not (0 <= lat_deg <= 90):
                lat_deg_valid = False
        except ValueError:
            lat_deg_valid = False
    
    if lat_min_text:
        try:
            lat_min = int(lat_min_text)
            if not (0 <= lat_min < 60):
                lat_min_valid = False
        except ValueError:
            lat_min_valid = False
    
    if lat_sec_text:
        try:
            lat_sec = float(lat_sec_text)
            if not (0 <= lat_sec < 60):
                lat_sec_valid = False
        except ValueError:
            lat_sec_valid = False
    
    # Validation longitude
    lon_deg_valid = True
    lon_min_valid = True
    lon_sec_valid = True
    
    lon_deg_text = viewer.lon_deg_entry.get()
    lon_min_text = viewer.lon_min_entry.get()
    lon_sec_text = viewer.lon_sec_entry.get()
    
    if lon_deg_text:
        try:
            lon_deg = int(lon_deg_text)
            if not (0 <= lon_deg <= 180):
                lon_deg_valid = False
        except ValueError:
            lon_deg_valid = False
    
    if lon_min_text:
        try:
            lon_min = int(lon_min_text)
            if not (0 <= lon_min < 60):
                lon_min_valid = False
        except ValueError:
            lon_min_valid = False
    
    if lon_sec_text:
        try:
            lon_sec = float(lon_sec_text)
            if not (0 <= lon_sec < 60):
                lon_sec_valid = False
        except ValueError:
            lon_sec_valid = False
    
    # Changer les couleurs
    viewer.lat_deg_entry.config(bg="white" if lat_deg_valid else "#ffcccc")
    viewer.lat_min_entry.config(bg="white" if lat_min_valid else "#ffcccc")
    viewer.lat_sec_entry.config(bg="white" if lat_sec_valid else "#ffcccc")
    viewer.lon_deg_entry.config(bg="white" if lon_deg_valid else "#ffcccc")
    viewer.lon_min_entry.config(bg="white" if lon_min_valid else "#ffcccc")
    viewer.lon_sec_entry.config(bg="white" if lon_sec_valid else "#ffcccc")

def validate_calamar(viewer):
    """Valider le format coordonnées Calamar"""
    y_valid = True
    x_valid = True
    
    y_text = viewer.calamar_y_entry.get()
    x_text = viewer.calamar_x_entry.get()
    
    if y_text:
        try:
            float(y_text)
        except ValueError:
            y_valid = False
    
    if x_text:
        try:
            float(x_text)
        except ValueError:
            x_valid = False
    
    # Changer les couleurs
    viewer.calamar_y_entry.config(bg="white" if y_valid else "#ffcccc")
    viewer.calamar_x_entry.config(bg="white" if x_valid else "#ffcccc")

def validate_radial(viewer):
    """Valider les champs radial distance"""
    distance_valid = True
    bearing_valid = True
    
    distance_text = viewer.radial_distance_entry.get()
    bearing_text = viewer.radial_bearing_entry.get()
    
    if distance_text:
        try:
            distance = float(distance_text)
            if distance <= 0:
                distance_valid = False
        except ValueError:
            distance_valid = False
    
    if bearing_text:
        try:
            bearing = float(bearing_text)
            if not (0 <= bearing < 360):
                bearing_valid = False
        except ValueError:
            bearing_valid = False
    
    # Changer les couleurs
    viewer.radial_distance_entry.config(bg="white" if distance_valid else "#ffcccc")
    viewer.radial_bearing_entry.config(bg="white" if bearing_valid else "#ffcccc")

def validate_click_point(viewer):
    """Valider les champs pour le mode click"""
    nom_valid = True
    lat_valid = True
    lon_valid = True
    
    nom_text = viewer.click_nom_entry.get().strip()
    lat_text = viewer.click_lat_entry.get()
    lon_text = viewer.click_lon_entry.get()
    
    # Validation nom
    if not nom_text:
        nom_valid = False
    
    # Validation latitude
    if lat_text:
        try:
            lat = float(lat_text)
            if not (-90 <= lat <= 90):
                lat_valid = False
        except ValueError:
            lat_valid = False
    else:
        lat_valid = False
    
    # Validation longitude
    if lon_text:
        try:
            lon = float(lon_text)
            if not (-180 <= lon <= 180):
                lon_valid = False
        except ValueError:
            lon_valid = False
    else:
        lon_valid = False
    
    # Changer les couleurs
    viewer.click_nom_entry.config(bg="white" if nom_valid else "#ffcccc")
    
    return nom_valid and lat_valid and lon_valid