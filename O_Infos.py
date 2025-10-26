import tkinter as tk
from tkinter import ttk
import sqlite3

def setup_notebook_tabs(viewer):
    """ Gestion de l'onglet Infos"""
    info_frame = ttk.Frame(viewer.notebook)
    viewer.notebook.add(info_frame, text="  Infos  ")
    
    ttk.Label(info_frame, text="Informations", font=('Arial', 10, 'bold')).pack(pady=5)
    
    viewer.info_text = tk.Text(info_frame, height=15, width=35, wrap=tk.WORD)
    viewer.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    update_info_panel(viewer)
    

def update_layers_info(viewer):
    """Mettre à jour les informations des couches"""
        
    if viewer.db_path:
        info = "CARTE MBTILES\n"        
        info += f"• Zoom actuel: {viewer.zoom}\n"
        
        # Informations de la base de données
        try:
            conn = sqlite3.connect(viewer.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tiles")
            total_tiles = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(zoom_level), MAX(zoom_level) FROM tiles")
            min_z, max_z = cursor.fetchone()
            
            info += f"• Tuiles totales: {total_tiles}\n"
            info += f"• Niveaux de zoom: {min_z}-{max_z}\n"
            info += f"• Col: {viewer.min_col} to {viewer.max_col}\n"
            info += f"• Row: {viewer.min_row} to {viewer.max_row}\n"
            
            conn.close()
        except:
            pass
    else:
        info = "CARTE MBTILES\n"
        info += "• Aucune carte chargée\n"
        info += "• Charger une carte par le menu Fichier\n"

    viewer.info_text.insert(tk.END, info)

def update_info_panel(viewer):
    """Mettre à jour le panneau d'informations"""
    viewer.info_text.delete(1.0, tk.END)
    
    info = "VISUALISATEUR MBTILES\n"
    info += "=" * 20 + "\n\n"
    info += "CONTRÔLES:\n"
    info += "• Glisser: Déplacer la carte\n"
    info += "• Molette: Zoomer/Dézoomer\n"
    info += "• Survol: Voir coordonnées\n\n"
    info += "FORMATS SUPPORTÉS:\n"
    info += "• Tuiles raster (PNG/JPEG)\n"
    info += "• Format: MBTiles (SQLite)\n"
    info += "• Projection: Web Mercator\n\n"
    
    viewer.info_text.insert(1.0, info)
    update_layers_info(viewer)