import simplekml
import sqlite3
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox
import tkinter as tk
import os

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
            
            # Parser la liste de coordonnées (format: "lon,lat,alt lon,lat,alt ...")
            coordinate_groups = points_list.split(' ')
            coords = []
            for coord_group in coordinate_groups:
                coord_group = coord_group.strip()
                if coord_group:
                    # Split lon,lat,alt
                    coord_parts = coord_group.split(',')
                    if len(coord_parts) >= 2:
                        try:
                            lon = float(coord_parts[0])
                            lat = float(coord_parts[1])
                            coords.append((lon, lat))
                        except ValueError:
                            continue
            
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
            
            # Parser la liste de coordonnées (format: "lon,lat,alt lon,lat,alt ...")
            coordinate_groups = points_list.split(' ')
            coords = []
            for coord_group in coordinate_groups:
                coord_group = coord_group.strip()
                if coord_group:
                    # Split lon,lat,alt
                    coord_parts = coord_group.split(',')
                    if len(coord_parts) >= 2:
                        try:
                            lon = float(coord_parts[0])
                            lat = float(coord_parts[1])
                            coords.append((lon, lat))
                        except ValueError:
                            continue
            
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

def parse_kml_file(kml_content):
    """Parse un fichier KML et extrait les objets avec leurs styles"""
    try:
        root = ET.fromstring(kml_content)
        
        # Namespaces KML
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        points = []
        lines = []
        polygons = []
        
        # Fonction pour extraire les styles
        def extract_style(placemark):
            color = "rouge"
            width = 2
            
            # Chercher le style inline ou référencé
            style_elem = placemark.find('.//kml:Style', ns)
            
            # Si pas de style inline, chercher styleUrl
            if style_elem is None:
                style_url_elem = placemark.find('kml:styleUrl', ns)
                if style_url_elem is not None:
                    style_id = style_url_elem.text.replace('#', '')
                    # Chercher le style dans le document
                    style_elem = root.find(f'.//kml:Style[@id="{style_id}"]', ns)
            
            if style_elem is not None:
                # Couleur de ligne
                line_style = style_elem.find('.//kml:LineStyle/kml:color', ns)
                if line_style is not None:
                    kml_color = line_style.text.strip().lower()
                    
                    # Mapping direct des couleurs KML courantes
                    kml_color_map = {
                        'ff0000ff': 'rouge',     # Rouge
                        'ffff0000': 'bleu',      # Bleu  
                        'ff00ff00': 'vert',      # Vert
                        'ff008000': 'vert',      # Vert foncé
                        'ffffff00': 'jaune',     # Jaune
                        'ffff8000': 'orange',    # Orange
                        'ff00ffff': 'cyan',      # Cyan
                        'ffff00ff': 'magenta',   # Magenta
                        'ff000000': 'noir',      # Noir
                        'ffffffff': 'blanc',     # Blanc
                    }
                    
                    if kml_color in kml_color_map:
                        color = kml_color_map[kml_color]
                    else:
                        # Fallback: analyse RGB
                        try:
                            if len(kml_color) == 8:
                                b = int(kml_color[2:4], 16)
                                g = int(kml_color[4:6], 16) 
                                r = int(kml_color[6:8], 16)
                                
                                if g > r and g > b and g > 100:
                                    color = "vert"
                                elif r > g and r > b and r > 100:
                                    color = "rouge"
                                elif b > r and b > g and b > 100:
                                    color = "bleu"
                        except ValueError:
                            pass
                
                # Épaisseur de ligne
                width_elem = style_elem.find('.//kml:LineStyle/kml:width', ns)
                if width_elem is not None:
                    try:
                        width = max(1, int(float(width_elem.text.strip())))
                    except:
                        width = 2
            
            return color, width
        
        # Extraire les points (Placemark avec Point)
        for placemark in root.findall('.//kml:Placemark', ns):
            name_elem = placemark.find('kml:name', ns)
            name = name_elem.text if name_elem is not None else "Point sans nom"
            
            desc_elem = placemark.find('kml:description', ns)
            description = desc_elem.text if desc_elem is not None else ""
            
            point_elem = placemark.find('.//kml:Point/kml:coordinates', ns)
            if point_elem is not None:
                coords = point_elem.text.strip().split(',')
                if len(coords) >= 2:
                    lon, lat = float(coords[0]), float(coords[1])
                    points.append({
                        "type": "Point", "name": name, "lat": lat, "lon": lon, 
                        "description": description
                    })
            
            # Extraire les lignes (LineString)
            line_elem = placemark.find('.//kml:LineString/kml:coordinates', ns)
            if line_elem is not None:
                coords_text = line_elem.text.strip()
                coords_list = []
                for coord_pair in coords_text.split():
                    if ',' in coord_pair:
                        parts = coord_pair.split(',')
                        if len(parts) >= 2:
                            coords_list.append((float(parts[0]), float(parts[1])))
                
                if len(coords_list) >= 2:
                    color, width = extract_style(placemark)
                    lines.append({
                        "type": "Ligne", "name": name, "points": coords_list,
                        "description": description, "color": color, "width": width
                    })
            
            # Extraire les polygones
            poly_elem = placemark.find('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns)
            if poly_elem is not None:
                coords_text = poly_elem.text.strip()
                coords_list = []
                for coord_pair in coords_text.split():
                    if ',' in coord_pair:
                        parts = coord_pair.split(',')
                        if len(parts) >= 2:
                            coords_list.append((float(parts[0]), float(parts[1])))
                
                if len(coords_list) >= 3:
                    color, width = extract_style(placemark)
                    
                    # Vérifier si le polygone a un style de remplissage
                    fill = False
                    style_elem = placemark.find('.//kml:Style', ns)
                    if style_elem is None:
                        style_url_elem = placemark.find('kml:styleUrl', ns)
                        if style_url_elem is not None:
                            style_id = style_url_elem.text.replace('#', '')
                            style_elem = root.find(f'.//kml:Style[@id="{style_id}"]', ns)
                    
                    if style_elem is not None:
                        poly_style = style_elem.find('.//kml:PolyStyle/kml:fill', ns)
                        if poly_style is not None and poly_style.text.strip() == '1':
                            fill = True
                    
                    polygons.append({
                        "type": "Polygone", "name": name, "points": coords_list,
                        "description": description, "color": color, "width": width,
                        "fill": fill
                    })
        
        return points, lines, polygons
    
    except Exception as e:
        print(f"Erreur lors du parsing KML: {e}")
        return [], [], []

def import_kml_to_databases():
    """
    Importe un fichier KML et l'enregistre dans les bases de données
    Propose à l'utilisateur de remplacer ou d'ajouter aux données existantes
    """
    try:
        # Sélectionner le fichier KML
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier KML",
            filetypes=[("Fichiers KML", "*.kml"), ("Tous les fichiers", "*.*")]
        )
        
        if not file_path:
            return False
        
        # Lire le contenu du fichier KML
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                kml_content = f.read()
        except UnicodeDecodeError:
            # Essayer avec d'autres encodages
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    kml_content = f.read()
            except:
                messagebox.showerror("Erreur", "Impossible de lire le fichier KML")
                return False
        
        # Parser le fichier KML
        points, lines, polygons = parse_kml_file(kml_content)
        
        if not points and not lines and not polygons:
            messagebox.showwarning("Attention", "Aucun objet trouvé dans le fichier KML")
            return False
        
        # Afficher le résumé des objets trouvés
        summary = f"Objets trouvés dans le fichier KML:\n"
        summary += f"• Points: {len(points)}\n"
        summary += f"• Lignes: {len(lines)}\n"
        summary += f"• Polygones: {len(polygons)}\n\n"
        summary += "Que voulez-vous faire?"
        
        # Créer une fenêtre de dialogue personnalisée
        dialog = tk.Toplevel()
        dialog.title("Importation KML")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.grab_set()  # Rendre la fenêtre modale
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"400x250+{x}+{y}")
        
        result = {"action": None}
        
        # Label avec le résumé
        label = tk.Label(dialog, text=summary, justify=tk.LEFT, padx=20, pady=20)
        label.pack()
        
        # Frame pour les boutons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def add_to_existing():
            result["action"] = "add"
            dialog.destroy()
        
        def replace_existing():
            result["action"] = "replace"
            dialog.destroy()
        
        def cancel_import():
            result["action"] = "cancel"
            dialog.destroy()
        
        # Boutons
        tk.Button(button_frame, text="Ajouter aux objets existants", 
                 command=add_to_existing, width=25).pack(pady=5)
        tk.Button(button_frame, text="Remplacer les objets existants", 
                 command=replace_existing, width=25).pack(pady=5)
        tk.Button(button_frame, text="Annuler", 
                 command=cancel_import, width=25).pack(pady=5)
        
        # Attendre que l'utilisateur fasse son choix
        dialog.wait_window()
        
        if result["action"] == "cancel" or result["action"] is None:
            return False
        
        # Chemins des bases de données
        points_db = "point.db"
        lines_db = "ligne.db" 
        polygons_db = "polygone.db"
        
        success = True
        
        # Importer les points
        if points:
            success &= import_points_to_db(points, points_db, result["action"] == "replace")
        
        # Importer les lignes
        if lines:
            success &= import_lines_to_db(lines, lines_db, result["action"] == "replace")
        
        # Importer les polygones
        if polygons:
            success &= import_polygons_to_db(polygons, polygons_db, result["action"] == "replace")
        
        if success:
            messagebox.showinfo("Succès", 
                f"Importation terminée avec succès!\n"
                f"• {len(points)} points importés\n"
                f"• {len(lines)} lignes importées\n"
                f"• {len(polygons)} polygones importés")
            return True
        else:
            messagebox.showerror("Erreur", "Erreur lors de l'importation")
            return False
    
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'importation KML: {e}")
        return False

def import_points_to_db(points, db_path, replace_existing=False):
    """Importe les points dans la base de données"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Créer la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS points (
                name TEXT PRIMARY KEY,
                lat REAL,
                lon REAL
            )
        """)
        
        # Vider la table si demandé
        if replace_existing:
            cursor.execute("DELETE FROM points")
        
        # Insérer les points
        for point in points:
            try:
                cursor.execute(
                    "INSERT OR REPLACE INTO points (name, lat, lon) VALUES (?, ?, ?)",
                    (point["name"], point["lat"], point["lon"])
                )
            except Exception as e:
                print(f"Erreur insertion point {point['name']}: {e}")
                continue
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        print(f"Erreur importation points: {e}")
        return False

def import_lines_to_db(lines, db_path, replace_existing=False):
    """Importe les lignes dans la base de données"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Créer la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lines (
                name TEXT PRIMARY KEY,
                color TEXT,
                width INTEGER,
                points_list TEXT
            )
        """)
        
        # Vider la table si demandé
        if replace_existing:
            cursor.execute("DELETE FROM lines")
        
        # Insérer les lignes
        for line in lines:
            try:
                # Convertir la liste de points en format string
                points_str = " ".join([f"{lon},{lat},0" for lon, lat in line["points"]])
                
                cursor.execute(
                    "INSERT OR REPLACE INTO lines (name, color, width, points_list) VALUES (?, ?, ?, ?)",
                    (line["name"], line["color"], line["width"], points_str)
                )
            except Exception as e:
                print(f"Erreur insertion ligne {line['name']}: {e}")
                continue
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        print(f"Erreur importation lignes: {e}")
        return False

def import_polygons_to_db(polygons, db_path, replace_existing=False):
    """Importe les polygones dans la base de données"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Créer la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS polygons (
                name TEXT PRIMARY KEY,
                color TEXT,
                width INTEGER,
                fill BOOLEAN,
                points_list TEXT
            )
        """)
        
        # Vider la table si demandé
        if replace_existing:
            cursor.execute("DELETE FROM polygons")
        
        # Insérer les polygones
        for polygon in polygons:
            try:
                # Convertir la liste de points en format string
                points_str = " ".join([f"{lon},{lat},0" for lon, lat in polygon["points"]])
                
                cursor.execute(
                    "INSERT OR REPLACE INTO polygons (name, color, width, fill, points_list) VALUES (?, ?, ?, ?, ?)",
                    (polygon["name"], polygon["color"], polygon["width"], polygon["fill"], points_str)
                )
            except Exception as e:
                print(f"Erreur insertion polygone {polygon['name']}: {e}")
                continue
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        print(f"Erreur importation polygones: {e}")
        return False
