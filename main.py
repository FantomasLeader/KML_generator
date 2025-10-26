import tkinter as tk
from tkinter import ttk
import Utility
import O_Points
import O_Infos
import O_Fichier
import O_Lignes
from Mbtiles_manager import MbtilesManager
import os
import sqlite3

#pyinstaller --noconsole Visualisateur.py

class MBTilesViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("MPME")
        self.root.geometry("800x600")
        
        self.db_path = None
        self.zoom = 11
        self.offset_x = 0
        self.offset_y = 0
        
        # Cache des tuiles contenant les images déjà chargées
        self.tile_cache = {}
        self.min_col = 0
        self.max_col = 0
        self.min_row = 0
        self.max_row = 0        
               
        self.mbtiles_manager = MbtilesManager(self)
        self.create_database()
        self.setup_ui()
        self.bind_events()
        
        # Gérer la fermeture du programme
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        # Frame principal avec panneau latéral
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook à gauche
        self.notebook = ttk.Notebook(main_frame, width=350)
        self.notebook.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=(10, 5))
                       
        # Canvas à droite
        self.canvas = tk.Canvas(main_frame, bg="lightgray",relief=tk.GROOVE, borderwidth=2)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        #Status Bar     
        self.status_bar = tk.Label(self.root, text="Ouvrez un fichier MBTiles", 
                                  bd=1, relief=tk.SUNKEN, anchor=tk.E)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
        # Onglet Fichiers
        O_Fichier.setup_notebook_tabs(self)
        
        # Onglet Points
        O_Points.setup_notebook_tabs(self)
        
        # Onglet Lignes
        O_Lignes.setup_notebook_tabs(self)
        
        # Onglet Infos
        O_Infos.setup_notebook_tabs(self)
        
    def bind_events(self):
        self.canvas.bind("<Button-1>", self.mbtiles_manager.start_drag)
        self.canvas.bind("<B1-Motion>", self.mbtiles_manager.drag)
        self.canvas.bind("<MouseWheel>", self.mbtiles_manager.zoom_map)
        self.canvas.bind("<Motion>", self.mbtiles_manager.mouse_motion)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def create_database(self):
        """Créer les bases de données SQLite point.db, ligne.db, polygone.db"""
        # Base point.db
        conn = sqlite3.connect("point.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                lat REAL,
                lon REAL
            )
        ''')
        conn.commit()
        conn.close()
        
        # Base ligne.db
        conn = sqlite3.connect("ligne.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                color TEXT,
                width INTEGER,
                points_list TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
        # Base polygone.db
        conn = sqlite3.connect("polygone.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                color TEXT,
                width INTEGER,
                fill BOOLEAN,
                points_list TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def on_tab_changed(self, event):
        """Gérer le changement d'onglet"""
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        
        if tab_text == "Infos":
            O_Infos.update_info_panel(self)
        elif tab_text == "Ligne":
            O_Lignes.refresh_on_tab_change(self)
    
    def update_infos_after_load(self):
        """Mettre à jour l'onglet Infos après chargement"""
        O_Infos.update_infos_tab(self)
    
    def draw_points(self):
        """Dessiner tous les points sur la carte"""
        if not hasattr(self, 'min_col') or not hasattr(self, 'max_row'):
            return
        
        # Effacer les points existants
        self.canvas.delete("point")
        
        # Récupérer tous les points de la base de données
        conn = sqlite3.connect("point.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, lat, lon FROM elements")
        points = cursor.fetchall()
        conn.close()
        
        # Dessiner chaque point
        for nom, lat, lon in points:
            x, y = Utility.latlon_to_pixel(lat, lon, self.offset_x, self.offset_y, self.min_col, self.max_row, self.zoom)
            
            # Vérifier si le point est visible dans le canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if 0 <= x <= canvas_width and 0 <= y <= canvas_height:
                # Dessiner le point (cercle rouge)
                radius = 4
                self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                                      fill="red", outline="darkred", width=2, tags="point")
                
                # Ajouter le nom du point
                self.canvas.create_text(x, y-10, text=nom, fill="black", 
                                      font=("Arial", 8, "bold"), tags="point")            
            
    def update_status(self, tiles_loaded):
        """Mettre à jour la barre d'état"""
        self.status_bar.config(text=f"Zoom: {self.zoom} | Tuiles visibles: {tiles_loaded}")
        # Redessiner les points après mise à jour de la carte
        self.draw_points()
    
    def on_closing(self):
        """Gérer la fermeture du programme"""
        try:
            for db_file in ["point.db", "ligne.db", "polygone.db"]:
                if os.path.exists(db_file):
                    os.remove(db_file)
        except PermissionError:
            pass
        self.root.destroy()

def main():
    root = tk.Tk()
    app = MBTilesViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()