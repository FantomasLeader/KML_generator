import simplekml
import sqlite3

def create_kml_from_databases(kml_filename, points_db, lines_db, polygons_db):
    """
    Génère un fichier KML depuis 3 bases de données SQLite
    
    Args:
        kml_filename: nom du fichier KML à créer
        points_db: chemin vers point.db (name, lat, lon)
        lines_db: chemin vers ligne.db (name, color, width, points_list)
        polygons_db: chemin vers polygone.db (name, color, width, fill, points_list)
    """
    kml = simplekml.Kml()
    
    # Mapping des couleurs
    color_map = {
        "rouge": simplekml.Color.red,
        "vert": simplekml.Color.green,
        "bleu": simplekml.Color.blue,
        "jaune": simplekml.Color.yellow,
        "orange": simplekml.Color.orange,
        "cyan": simplekml.Color.cyan,
        "magenta": simplekml.Color.magenta,
        "noir": simplekml.Color.black,
        "blanc": simplekml.Color.white
    }
    
    # Charger les points
    points_data = {}
    try:
        conn = sqlite3.connect(points_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name, lat, lon FROM points")
        for name, lat, lon in cursor.fetchall():
            points_data[name] = (float(lon), float(lat))
        conn.close()
        
        # Créer dossier points
        if points_data:
            points_folder = kml.newfolder(name="Points")
            for name, (lon, lat) in points_data.items():
                points_folder.newpoint(name=name, coords=[(lon, lat)])
    except:
        pass
    
    # Charger les lignes
    try:
        conn = sqlite3.connect(lines_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name, color, width, points_list FROM lines")
        
        lines_folder = None
        for name, color, width, points_list in cursor.fetchall():
            if not lines_folder:
                lines_folder = kml.newfolder(name="Lignes")
            
            # Parser la liste de points
            point_names = points_list.split(',')
            coords = []
            for point_name in point_names:
                point_name = point_name.strip()
                if point_name in points_data:
                    coords.append(points_data[point_name])
            
            if len(coords) >= 2:
                line = lines_folder.newlinestring(name=name, coords=coords)
                line.style.linestyle.color = color_map.get(color, simplekml.Color.red)
                line.style.linestyle.width = int(width)
        
        conn.close()
    except:
        pass
    
    # Charger les polygones
    try:
        conn = sqlite3.connect(polygons_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name, color, width, fill, points_list FROM polygons")
        
        polygons_folder = None
        for name, color, width, fill, points_list in cursor.fetchall():
            if not polygons_folder:
                polygons_folder = kml.newfolder(name="Polygones")
            
            # Parser la liste de points
            point_names = points_list.split(',')
            coords = []
            for point_name in point_names:
                point_name = point_name.strip()
                if point_name in points_data:
                    coords.append(points_data[point_name])
            
            if len(coords) >= 3:
                # Fermer le polygone
                if coords[0] != coords[-1]:
                    coords.append(coords[0])
                
                poly = polygons_folder.newpolygon(name=name, outerboundaryis=coords)
                poly.style.linestyle.color = color_map.get(color, simplekml.Color.red)
                poly.style.linestyle.width = int(width)
                
                if str(fill).lower() in ['true', '1', 'yes']:
                    base_color = color_map.get(color, simplekml.Color.red)
                    poly.style.polystyle.color = simplekml.Color.changealphaint(150, base_color)
                    poly.style.polystyle.fill = 1
                else:
                    poly.style.polystyle.fill = 0
        
        conn.close()
    except:
        pass
    
    # Sauvegarder le KML
    kml.save(kml_filename)
    return kml_filename

def create_sample_databases():
    """Crée des bases de données d'exemple pour tester"""
    
    # Base points
    conn = sqlite3.connect('points.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS points')
    cursor.execute('''CREATE TABLE points 
                     (name TEXT PRIMARY KEY, lat REAL, lon REAL)''')
    cursor.execute("INSERT INTO points VALUES ('Point1', 44.5204, -1.1166)")
    cursor.execute("INSERT INTO points VALUES ('Point2', 44.5239, -1.1301)")
    cursor.execute("INSERT INTO points VALUES ('Point3', 44.5160, -1.1168)")
    conn.commit()
    conn.close()
    
    # Base lignes
    conn = sqlite3.connect('lines.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS lines 
                     (name TEXT PRIMARY KEY, color TEXT, width INTEGER, points_list TEXT)''')
    cursor.execute("INSERT OR REPLACE INTO lines VALUES ('Ligne1', 'rouge', 3, 'Point1,Point2,Point3')")
    conn.commit()
    conn.close()
    
    # Base polygones
    conn = sqlite3.connect('polygons.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS polygons 
                     (name TEXT PRIMARY KEY, color TEXT, width INTEGER, fill BOOLEAN, points_list TEXT)''')
    cursor.execute("INSERT OR REPLACE INTO polygons VALUES ('Polygone1', 'vert', 2, 1, 'Point1,Point2,Point3')")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Créer des bases d'exemple
    create_sample_databases()
    
    # Générer le KML
    kml_file = create_kml_from_databases(
        "output.kml",
        "points.db", 
        "lines.db", 
        "polygons.db"
    )
    
    print(f"Fichier KML créé: {kml_file}")