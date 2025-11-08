import tkinter as tk
from tkinter import ttk
import Utility
import O_Points
import O_Infos
import O_Fichier
import O_Lignes
import O_Polygones
from Mbtiles_manager import MbtilesManager
import os
import sqlite3
from Menu import MenuBar

#pyinstaller --noconsole Visualisateur.py

class MBTilesViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("MPME")
        self.root.geometry("350x700")  # Taille réduite au démarrage (cohérente avec hide_canvas)
        
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
        
        # Flag pour savoir si une carte est chargée
        self.carte_chargee = False
               
        self.mbtiles_manager = MbtilesManager(self)
        self.create_database()
        self.setup_ui()
        self.bind_events()
        self.setup_menu()
        
        # Gérer la fermeture du programme
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_menu(self):        
        """Gestion des options du menu"""
        def importer_raster():
            O_Fichier.import_carte(self)

        def exporter_kml():
            O_Fichier.export_kml(self)
        
        def importer_kml():
            # Importer la fonction depuis kml_manager
            from kml_manager import import_kml_to_databases
            if import_kml_to_databases():
                # Recharger les données dans l'interface après importation
                self.refresh_all_tabs()
        
        def fermer_carte():
            self.hide_canvas()
            self.db_path = None

        MenuBar(self.root, importer_raster, exporter_kml, importer_kml, fermer_carte)

    def setup_ui(self):
        # Frame principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook à gauche
        self.notebook = ttk.Notebook(self.main_frame, width=350)
        self.notebook.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=(10, 5))
        
        # Canvas à droite (créé mais pas affiché au démarrage)
        self.canvas = tk.Canvas(self.main_frame, bg="lightgray", relief=tk.GROOVE, borderwidth=2)

        #Status Bar     
        self.status_bar = tk.Label(self.root, text="Ouvrez un fichier MBTiles", 
                                  bd=1, relief=tk.SUNKEN, anchor=tk.E)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
                  
        # Onglet Points
        O_Points.setup_notebook_tabs(self)
        
        # Onglet Lignes
        O_Lignes.setup_notebook_tabs(self)
        
        #Onglet Polygones
        O_Polygones.setup_notebook_tabs_polygone(self)

        # Onglet Infos
        O_Infos.setup_notebook_tabs(self)
        
    def bind_events(self):
        # Événements pour le notebook
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
    def bind_canvas_events(self):
        """Lier les événements du canvas après qu'il soit affiché"""
        self.canvas.bind("<Button-1>", self.mbtiles_manager.start_drag)
        self.canvas.bind("<B1-Motion>", self.mbtiles_manager.drag)
        self.canvas.bind("<MouseWheel>", self.mbtiles_manager.zoom_map)
        self.canvas.bind("<Motion>", self.mbtiles_manager.mouse_motion)
    
    def show_canvas(self):
        """Afficher le canvas et agrandir la fenêtre"""
        if not self.carte_chargee:
            self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            self.root.geometry("900x700")  # Agrandir la fenêtre
            self.carte_chargee = True
            self.bind_canvas_events()
    
    def hide_canvas(self):
        """Masquer le canvas et réduire la fenêtre"""
        if self.carte_chargee:
            self.canvas.pack_forget()
            self.root.geometry("350x700")  # Réduire la fenêtre
            self.carte_chargee = False
    
    def create_database(self):
        """Créer les bases de données SQLite point.db, ligne.db, polygone.db"""
        # Base point.db
        conn = sqlite3.connect("point.db")
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS points')
        cursor.execute('''CREATE TABLE points 
                     (name TEXT PRIMARY KEY, lat REAL, lon REAL)''')
        conn.commit()
        conn.close()
        
        # Base ligne.db
        conn = sqlite3.connect("ligne.db")
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS lines')
        cursor.execute('''CREATE TABLE lines 
                     (name TEXT PRIMARY KEY, color TEXT, width INTEGER, points_list TEXT)''')
        conn.commit()
        conn.close()
        
        # Base polygone.db
        conn = sqlite3.connect("polygone.db")
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS polygons')
        cursor.execute('''CREATE TABLE polygons 
                     (name TEXT PRIMARY KEY, color TEXT, width INTEGER, fill BOOLEAN, points_list TEXT)''')
        conn.commit()
        conn.close()

    def on_tab_changed(self, event):
        """Gérer le changement d'onglet"""
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        print(f"Tab text: '{tab_text}'")
        
        if tab_text == "Infos":
            O_Infos.update_info_panel(self)
        elif tab_text == "  Lignes  ":
            O_Lignes.refresh_on_tab_change(self)
        elif tab_text == "  Polygones  ":
            print(f"Tab text: '{tab_text}'")
            O_Polygones.refresh_on_tab_change_polygone(self)
    
    def update_infos_after_load(self):
        """Mettre à jour l'onglet Infos après chargement"""
        O_Infos.update_infos_tab(self)
    
    def refresh_all_tabs(self):
        """Rafraîchir tous les onglets après importation de données"""
        try:
            # Rafraîchir l'onglet Points
            if hasattr(self, 'points_listbox'):
                O_Points.load_points(self)
            
            # Rafraîchir l'onglet Lignes  
            if hasattr(self, 'lines_listbox'):
                O_Lignes.load_lines(self)
            
            # Rafraîchir l'onglet Polygones
            if hasattr(self, 'polygones_listbox'):
                O_Polygones.load_polygones(self)
            
            # Rafraîchir l'onglet Infos
            O_Infos.update_info_panel(self)
            
            # Redessiner la carte avec les nouveaux objets
            if hasattr(self, 'mbtiles_manager'):
                self.mbtiles_manager.draw_points()
                self.mbtiles_manager.draw_lines() 
                self.mbtiles_manager.draw_polygones()
                
        except Exception as e:
            print(f"Erreur lors du rafraîchissement: {e}")
    
    # ...existing code...
            
    def update_status(self, tiles_loaded):
        """Mettre à jour la barre d'état"""
        self.status_bar.config(text=f"Zoom: {self.zoom} | Tuiles visibles: {tiles_loaded}")
        # Redessiner tous les objets après mise à jour de la carte
        self.mbtiles_manager.draw_points()
        self.mbtiles_manager.draw_lines()
        self.mbtiles_manager.draw_polygones()
    
    def on_closing(self):
        """Gérer la fermeture du programme en supprimant les bases de données"""
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