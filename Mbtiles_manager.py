import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import io
from PIL import Image, ImageTk
import Utility
import O_Infos

class MbtilesManager:
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
            self.viewer.draw_points()
            
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