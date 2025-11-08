import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import io
from PIL import Image, ImageTk
import Utility
import O_Infos

class MbtilesManager:
    def draw_polygones(self):
        """Dessiner tous les polygones sur la carte"""
        viewer = self.viewer
        if not hasattr(viewer, 'min_col') or not hasattr(viewer, 'max_row'):
            return
        viewer.canvas.delete("polygone")

        # Charger les polygones
        try:
            conn_poly = sqlite3.connect("polygone.db")
            cursor_poly = conn_poly.cursor()
            cursor_poly.execute("SELECT name, color, width, fill, points_list FROM polygons")
            polygones = cursor_poly.fetchall()
            conn_poly.close()
        except Exception as e:
            print(f"Erreur chargement polygones: {e}")
            return

        color_map = {
            "rouge": "red",
            "vert": "green",
            "bleu": "blue",
            "jaune": "yellow",
            "orange": "orange",
            "cyan": "cyan",
            "magenta": "magenta",
            "noir": "black",
            "blanc": "white"
        }
        for name, color, width, fill, points_list in polygones:
            try:
                # Dans la base, les polygones sont maintenant enregistrés avec des coordonnées:
                # "lon,lat,0 lon2,lat2,0 ..." (séparées par des espaces)
                pixel_points = []
                if points_list:
                    coord_tokens = [tok.strip() for tok in points_list.split() if tok.strip()]
                    for tok in coord_tokens:
                        parts = tok.split(',')
                        if len(parts) >= 2:
                            try:
                                lon = float(parts[0])
                                lat = float(parts[1])
                            except ValueError:
                                continue
                            px = Utility.latlon_to_pixel(lat, lon, viewer.offset_x, viewer.offset_y, viewer.min_col, viewer.max_row, viewer.zoom)
                            pixel_points.append(px)

                if len(pixel_points) >= 3:
                    tk_color = color_map.get(str(color).strip().lower(), "red")
                    outline_color = tk_color
                    fill_color = tk_color if int(fill) else ""
                    # Transparence 50% avec Pillow
                    if int(fill):
                        # Déterminer la bounding box du polygone
                        xs = [pt[0] for pt in pixel_points]
                        ys = [pt[1] for pt in pixel_points]
                        min_x, max_x = int(min(xs)), int(max(xs))
                        min_y, max_y = int(min(ys)), int(max(ys))
                        w, h = max_x - min_x + 1, max_y - min_y + 1
                        if w < 1 or h < 1:
                            continue
                        # Créer une image RGBA transparente
                        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                        from PIL import ImageDraw
                        draw = ImageDraw.Draw(img)
                        # Couleur de remplissage avec alpha 128
                        rgb = viewer.canvas.winfo_rgb(tk_color)
                        r = int(rgb[0] / 256)
                        g = int(rgb[1] / 256)
                        b = int(rgb[2] / 256)
                        fill_rgba = (r, g, b, 128)
                        # Décaler les points pour l'image locale
                        local_points = [(x - min_x, y - min_y) for x, y in pixel_points]
                        draw.polygon(local_points, fill=fill_rgba)
                        # Convertir en PhotoImage et afficher
                        photo = ImageTk.PhotoImage(img)
                        viewer.canvas.create_image(min_x, min_y, image=photo, anchor=tk.NW, tags="polygone")
                        if not hasattr(viewer.canvas, "_poly_images"):
                            viewer.canvas._poly_images = []
                        viewer.canvas._poly_images.append(photo)
                    # Dessiner la bordure opaque
                    viewer.canvas.create_polygon(*[coord for point in pixel_points for coord in point], fill="", outline=outline_color, width=int(width), tags="polygone")
            except Exception as e:
                print(f"Erreur polygone '{name}': points_list={points_list} | Exception: {e}")
                continue

    def draw_lines(self):
        """Dessiner toutes les lignes sur la carte (points_list = noms de points)"""
        viewer = self.viewer
        if not hasattr(viewer, 'min_col') or not hasattr(viewer, 'max_row'):
            return
        viewer.canvas.delete("line")
        # Charger tous les points dans un dict {nom: (lat, lon)}
        conn_points = sqlite3.connect("point.db")
        cursor_points = conn_points.cursor()
        cursor_points.execute("SELECT name, lat, lon FROM points")
        points_data = {name: (lat, lon) for name, lat, lon in cursor_points.fetchall()}
        conn_points.close()

        # Charger les lignes
        conn_lines = sqlite3.connect("ligne.db")
        cursor_lines = conn_lines.cursor()
        cursor_lines.execute("SELECT name, color, width, points_list FROM lines")
        lines = cursor_lines.fetchall()
        conn_lines.close()

        color_map = {
            "rouge": "red",
            "vert": "green",
            "bleu": "blue",
            "jaune": "yellow",
            "orange": "orange",
            "cyan": "cyan",
            "magenta": "magenta",
            "noir": "black",
            "blanc": "white"
        }
        for name, color, width, points_list in lines:
            try:
                # Dans la base, les lignes sont enregistrées avec des coordonnées:
                # "lon,lat,0 lon2,lat2,0 ..." (séparées par des espaces)
                pixel_points = []
                if points_list:
                    coord_tokens = [tok.strip() for tok in points_list.split() if tok.strip()]
                    for tok in coord_tokens:
                        parts = tok.split(',')
                        if len(parts) >= 2:
                            try:
                                lon = float(parts[0])
                                lat = float(parts[1])
                            except ValueError:
                                continue
                            px = Utility.latlon_to_pixel(lat, lon, viewer.offset_x, viewer.offset_y, viewer.min_col, viewer.max_row, viewer.zoom)
                            pixel_points.append(px)

                if len(pixel_points) >= 2:
                    tk_color = color_map.get(str(color).strip().lower(), "red")
                    viewer.canvas.create_line(*[coord for point in pixel_points for coord in point], fill=tk_color, width=int(width), tags="line")
            except Exception as e:
                print(f"Erreur ligne '{name}': points_list={points_list} | Exception: {e}")
                continue

    def draw_points(self):
        """Dessiner tous les points sur la carte"""
        viewer = self.viewer
        if not hasattr(viewer, 'min_col') or not hasattr(viewer, 'max_row'):
            return
        # Effacer les points existants
        viewer.canvas.delete("point")
        # Récupérer tous les points de la base de données
        conn = sqlite3.connect("point.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, lat, lon FROM points")
        points = cursor.fetchall()
        conn.close()
        # Dessiner chaque point
        for nom, lat, lon in points:
            x, y = Utility.latlon_to_pixel(lat, lon, viewer.offset_x, viewer.offset_y, viewer.min_col, viewer.max_row, viewer.zoom)
            # Vérifier si le point est visible dans le canvas
            canvas_width = viewer.canvas.winfo_width()
            canvas_height = viewer.canvas.winfo_height()
            if 0 <= x <= canvas_width and 0 <= y <= canvas_height:
                # Dessiner le point (cercle rouge)
                radius = 4
                viewer.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                                      fill="red", outline="darkred", width=2, tags="point")
                # Ajouter le nom du point
                viewer.canvas.create_text(x, y-10, text=nom, fill="black", 
                                      font=("Arial", 8, "bold"), tags="point")
                
    def center_map_on_point(self, lat, lon):
        """Centrer la carte sur un point donné en latitude/longitude"""
        viewer = self.viewer
        
        if not viewer.db_path or not hasattr(viewer, 'min_col') or not hasattr(viewer, 'max_row'):
            return
        
        # Obtenir les dimensions du canvas
        canvas_width = viewer.canvas.winfo_width()
        canvas_height = viewer.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 800, 600
        
        # Convertir lat/lon en coordonnées pixel pour le niveau de zoom actuel
        target_x, target_y = Utility.latlon_to_pixel(
            lat, lon, 
            viewer.offset_x, viewer.offset_y, 
            viewer.min_col, viewer.max_row, viewer.zoom
        )
        
        # Calculer le décalage nécessaire pour centrer le point
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Ajuster les offsets pour que le point soit au centre
        viewer.offset_x += center_x - target_x
        viewer.offset_y += center_y - target_y
        
        # Redessiner la carte
        self.draw_map()

    def __init__(self, viewer):
        self.viewer = viewer
    
    def open_mbtiles(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner fichier MBTiles",
            filetypes=[("MBTiles", "*.mbtiles"), ("Tous", "*.*")]
        )
        
        if file_path:
            self.viewer.db_path = file_path
            self.viewer.offset_x = 0
            self.viewer.offset_y = 0
            self.draw_map()            
    
    def start_drag(self, event):
        self.viewer.drag_start_x = event.x
        self.viewer.drag_start_y = event.y
        
    def drag(self, event):
        if hasattr(self.viewer, 'drag_start_x'):
            dx = event.x - self.viewer.drag_start_x
            dy = event.y - self.viewer.drag_start_y
            
            self.viewer.offset_x += dx
            self.viewer.offset_y += dy
            
            self.viewer.drag_start_x = event.x
            self.viewer.drag_start_y = event.y
            
            self.draw_map()
    
    def zoom_map(self, event):
        if not self.viewer.db_path:
            return
        
        mouse_x = event.x
        mouse_y = event.y
        
        conn = sqlite3.connect(self.viewer.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT zoom_level FROM tiles ORDER BY zoom_level")
        available_zooms = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not available_zooms:
            return
            
        current_idx = available_zooms.index(self.viewer.zoom) if self.viewer.zoom in available_zooms else 0
        old_zoom_level = available_zooms[current_idx]
        
        if event.delta > 0 and current_idx < len(available_zooms) - 1:
            new_zoom_level = available_zooms[current_idx + 1]
        elif event.delta < 0 and current_idx > 0:
            new_zoom_level = available_zooms[current_idx - 1]
        else:
            return
        
        zoom_factor = 2 ** (new_zoom_level - old_zoom_level)
        
        old_min_col = self.viewer.min_col
        old_max_row = self.viewer.max_row
        
        abs_x = (mouse_x - self.viewer.offset_x) / 256 + old_min_col
        abs_y = old_max_row - (mouse_y - self.viewer.offset_y) / 256
        
        self.viewer.zoom = new_zoom_level
        
        conn = sqlite3.connect(self.viewer.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(tile_column), MAX(tile_column), MIN(tile_row), MAX(tile_row) FROM tiles WHERE zoom_level=?", (self.viewer.zoom,))
        new_bounds = cursor.fetchone()
        conn.close()
        
        if new_bounds and new_bounds[0] is not None:
            new_min_col, new_max_col, new_min_row, new_max_row = new_bounds
            
            new_abs_x = abs_x * zoom_factor
            new_abs_y = abs_y * zoom_factor
            
            new_image_x = (new_abs_x - new_min_col) * 256
            new_image_y = (new_max_row - new_abs_y) * 256
            
            self.viewer.offset_x = mouse_x - new_image_x
            self.viewer.offset_y = mouse_y - new_image_y
        
        self.viewer.tile_cache.clear()
        self.draw_map()
        
    def draw_map(self):
        # Dessine la carte avec les Objets lignes,polygones et points
        if not self.viewer.db_path:
            return
            
        self.viewer.canvas.delete("all")
        
        try:
            # Determine la taille de l'espace d'affichage
            canvas_width = self.viewer.canvas.winfo_width()
            canvas_height = self.viewer.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 800, 600
            
            # Définit la taille de l'image a creer en fonction de la taille du canvas + un buffer
            visible_left = -self.viewer.offset_x - 256
            visible_right = -self.viewer.offset_x + canvas_width + 256
            visible_top = -self.viewer.offset_y - 256
            visible_bottom = -self.viewer.offset_y + canvas_height + 256
            
            conn = sqlite3.connect(self.viewer.db_path)
            cursor = conn.cursor()
            
            # Récupère les bornes des tuiles disponibles pour le niveau de zoom actuel (9 par défaut)
            cursor.execute("SELECT MIN(tile_column), MAX(tile_column), MIN(tile_row), MAX(tile_row) FROM tiles WHERE zoom_level=?", (self.viewer.zoom,))
            bounds = cursor.fetchone()
            
            if not bounds or bounds[0] is None:
                self.viewer.status_bar.config(text=f"Aucune tuile au zoom {self.viewer.zoom}")
                conn.close()
                return
            
            min_col, max_col, min_row, max_row = bounds
            self.viewer.min_col = min_col
            self.viewer.max_row = max_row
            self.viewer.min_row = min_row
            self.viewer.max_col = max_col
            
            start_col = max(min_col, int(visible_left // 256) + min_col)
            end_col = min(max_col, int(visible_right // 256) + min_col + 1)
            start_row = max(min_row, max_row - int(visible_bottom // 256))
            end_row = min(max_row, max_row - int(visible_top // 256) + 1)
            
            self.viewer.canvas.image = []
            tiles_loaded = 0
            
            for col in range(start_col, end_col + 1):
                for row in range(start_row, end_row + 1):
                    cache_key = (self.viewer.zoom, col, row)
                    if cache_key in self.viewer.tile_cache:
                        photo = self.viewer.tile_cache[cache_key]
                    else:
                        cursor.execute("SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?", (self.viewer.zoom, col, row))
                        result = cursor.fetchone()
                        
                        if not result:
                            continue
                            
                        try:
                            image = Image.open(io.BytesIO(result[0]))
                            photo = ImageTk.PhotoImage(image)
                            if len(self.viewer.tile_cache) < 100:
                                self.viewer.tile_cache[cache_key] = photo
                        except:
                            continue
                    
                    x = (col - min_col) * 256 + self.viewer.offset_x
                    y = (max_row - row) * 256 + self.viewer.offset_y
                    
                    self.viewer.canvas.create_rectangle(x, y, x+256, y+256, outline="black", width=1, fill="")
                    self.viewer.canvas.create_image(x, y, image=photo, anchor=tk.NW)
                    self.viewer.canvas.image.append(photo)
                    tiles_loaded += 1
            
            conn.close()
            self.viewer.update_status(tiles_loaded)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")
        
    def mouse_motion(self, event):
        if not self.viewer.db_path or not hasattr(self.viewer, 'min_col') or not hasattr(self.viewer, 'max_row'):
            return
        
        lat, lon = Utility.update_coordinates(event.x, event.y, self.viewer.offset_x, self.viewer.offset_y, self.viewer.min_col, self.viewer.max_row, self.viewer.zoom)
                
        if lat is not None and lon is not None:
            O_Infos.update_info_panel(self.viewer)
            coord_text = f"{lat:.4f}°{lon:.4f}°   "
            offset=f"({self.viewer.offset_x}, {self.viewer.offset_y})"
            tiles_count = len([item for item in self.viewer.canvas.find_all() if self.viewer.canvas.type(item) == 'image'])
            self.viewer.status_bar.config(text=f"Zoom: {self.viewer.zoom} | Tuiles: {tiles_count} | {coord_text} | Offset: {offset}")