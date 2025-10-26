import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import xml.etree.ElementTree as ET

def setup_notebook_tabs(app):
    """Configurer l'onglet Fichiers"""
    fichier_frame = ttk.Frame(app.notebook)
    app.notebook.add(fichier_frame, text="  Files  ")
    
    # Section Import
    import_frame = ttk.LabelFrame(fichier_frame, text="Import", padding=10)
    import_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Button(import_frame, text="Importer une carte", 
               command=lambda: import_carte(app)).pack(pady=5)
    
    # Section Export
    export_frame = ttk.LabelFrame(fichier_frame, text="Export", padding=10)
    export_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(export_frame, text="Nom du fichier KML:").pack(anchor=tk.W)
    app.kml_filename_var = tk.StringVar(value="export_points")
    ttk.Entry(export_frame, textvariable=app.kml_filename_var, width=30).pack(pady=5)
    
    ttk.Button(export_frame, text="Exporter points sélectionnés", 
               command=lambda: export_selected_points(app)).pack(pady=5)

def import_carte(app):
    """Importer une carte (fichier MBTiles)"""
    file_path = filedialog.askopenfilename(
        title="Choisir un fichier de carte",
        filetypes=[("MBTiles files", "*.mbtiles"), ("Tous les fichiers", "*.*")]
    )
    
    if file_path:
        app.db_path = file_path
        app.offset_x = 0
        app.offset_y = 0
        app.mbtiles_manager.draw_map()

def export_selected_points(app):
    """Exporter les points sélectionnés du treeview en KML"""
    if not hasattr(app, 'points_tree'):
        messagebox.showwarning("Attention", "Aucun treeview de points trouvé")
        return
    
    selected_items = app.points_tree.selection()
    if not selected_items:
        messagebox.showwarning("Attention", "Aucun point sélectionné")
        return
    
    filename = app.kml_filename_var.get().strip()
    if not filename:
        messagebox.showwarning("Attention", "Veuillez entrer un nom de fichier")
        return
    
    if not filename.endswith('.kml'):
        filename += '.kml'
    
    # Récupérer les données des points sélectionnés
    conn = sqlite3.connect("point.db")
    cursor = conn.cursor()
    
    # Créer le fichier KML
    kml = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
    document = ET.SubElement(kml, "Document")
    ET.SubElement(document, "name").text = "Points exportés"
    
    for item in selected_items:
        point_name = app.points_tree.item(item, "values")[0]
        
        cursor.execute("SELECT Nom, Lat, Lon FROM elements WHERE Nom = ?", (point_name,))
        result = cursor.fetchone()
        
        if result:
            nom, lat, lon = result
            placemark = ET.SubElement(document, "Placemark")
            ET.SubElement(placemark, "name").text = nom
            point = ET.SubElement(placemark, "Point")
            ET.SubElement(point, "coordinates").text = f"{lon},{lat},0"
    
    conn.close()
    
    # Sauvegarder le fichier
    try:
        tree = ET.ElementTree(kml)
        ET.indent(tree, space="  ", level=0)
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        messagebox.showinfo("Succès", f"Points exportés dans {filename}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")