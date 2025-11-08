import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import numpy as np
import Utility
import Validate
import gc

def close_db_connections():
    """Force la fermeture de toutes les connexions SQLite ouvertes"""
    gc.collect()  # Force le garbage collection pour fermer les connexions non fermées

def setup_notebook_tabs(viewer):
    """Créer l'onglet point du notebook"""
    
    # Configurer le style de l'onglet
    style = ttk.Style()
    style.configure('TNotebook.Tab', font=('Arial', 10))  # Onglet normal
    style.map('TNotebook.Tab', font=[('selected', ('Arial', 10, 'bold'))])  # Onglet sélectionné en gras
    
    # Onglet points
    points_frame = ttk.Frame(viewer.notebook)
    viewer.notebook.add(points_frame, text="  Points  ")
    
    # Variable pour récuperer les choix de l'utilisateur
    viewer.creation_mode = tk.StringVar(value="coordonnees")
    viewer.coord_type = tk.StringVar(value="Degrés")
    
    # Frame pour tous les radiobuttons
    coord_frame = tk.Frame(points_frame,relief='groove',borderwidth=1)
    coord_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Première ligne : Coordonnées + combobox
    coord_line = tk.Frame(coord_frame)
    coord_line.pack(anchor='w', padx=5, pady=(5,5))
    
    ttk.Radiobutton(coord_line, text="Coordonnées", variable=viewer.creation_mode, value="coordonnees", command=lambda: update_input_frame(viewer)).pack(side=tk.LEFT)
    viewer.coord_combo = ttk.Combobox(coord_line, textvariable=viewer.coord_type, values=["Degrés", "Degrés/Minutes", "Degrés/Minutes/Secondes", "Calamar"], width=40, state="readonly")
    viewer.coord_combo.pack(side=tk.LEFT, padx=(10, 0))
    viewer.coord_combo.bind('<<ComboboxSelected>>', lambda e: update_input_frame(viewer))
    
    # Deuxième ligne : Radial distance
    ttk.Radiobutton(coord_frame, text="Radial distance", variable=viewer.creation_mode, value="radial", command=lambda: update_input_frame(viewer)).pack(anchor='w', padx=5, pady=5)
    
    # Troisième ligne : Click droit
    ttk.Radiobutton(coord_frame, text="Click Droit sur la carte", variable=viewer.creation_mode, value="click", command=lambda: update_input_frame(viewer)).pack(anchor='w', padx=5, pady=5)
    
    # Frame pour les champs de saisie
    viewer.input_frame = tk.Frame(points_frame,relief='groove',borderwidth=1)
    viewer.input_frame.pack(fill=tk.X, padx=5, pady=5)

    # Frame pour le Treeview
    viewer.treeview_frame = tk.Frame(points_frame,relief='groove',borderwidth=1)
    viewer.treeview_frame.pack(fill=tk.X, padx=5, pady=5)

    # Titre du tableau de points
    tk.Label(viewer.treeview_frame, text="Liste des points",anchor="center", font=('Arial', 10, 'bold')).pack(pady=5, fill=tk.X, padx=5)
    
    # Création du Treeview 
    viewer.tree = ttk.Treeview(viewer.treeview_frame, columns=("selected", "nom", "lat", "lon"), show="headings", height=6)
    viewer.tree.heading("selected", text="Export")
    viewer.tree.heading("nom", text="Nom")
    viewer.tree.heading("lat", text="Latitude")
    viewer.tree.heading("lon", text="Longitude")
    
    viewer.tree.column("selected", width=50, anchor="center")
    viewer.tree.column("nom", width=60)
    viewer.tree.column("lat", width=60)
    viewer.tree.column("lon", width=60)
    
    viewer.checked_items = {}
    viewer.tree.bind("<Button-1>", lambda event: on_tree_click(viewer, event))
    viewer.tree.bind("<Double-1>", lambda event: on_tree_double_click(viewer, event))    
    viewer.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
   
    # Création des boutons
    btn_select_all = ttk.Button(viewer.treeview_frame, text="Sélectionner tout", width=15, command=lambda: select_all_treeview(viewer))
    btn_select_all.pack(side=tk.LEFT, padx=5)
    btn_deselect_all = ttk.Button(viewer.treeview_frame, text="Désélectionner tout", command=lambda: deselect_all_treeview(viewer))
    btn_deselect_all.pack(side=tk.LEFT, padx=5)
    btn_delete = ttk.Button(viewer.treeview_frame, text="Supprimer", command=lambda: delete_selected_points(viewer))
    btn_delete.pack(side=tk.LEFT, padx=5)
    
    # Initialiser l'affichage
    update_input_frame(viewer)
    
    # Bind clic droit pour création de point
    viewer.canvas.bind("<Button-3>", lambda event: right_click_get_coordinate(viewer, event))
    
    # Charger les points existants
    load_points(viewer)

def update_input_frame(viewer):
    """MAJ du frame de saisie selon le type de coordonnées choisies"""
    
    # Effacer le contenu de input_frame
    for widget in viewer.input_frame.winfo_children():
        widget.destroy()
    
    # Affiche les widgets en fonction du format des coordonnées
    if viewer.creation_mode.get() == "coordonnees":
        viewer.coord_combo.pack(side=tk.LEFT, padx=(56, 0))
        print(viewer.coord_type.get())
        
        if viewer.coord_type.get() == "Degrés":

            # Nom
            tk.Label(viewer.input_frame, text="Nom :", width=10, anchor="w").grid(row=0, column=0, padx=5, pady=5)
            viewer.nom_entry = tk.Entry(viewer.input_frame, width=20)
            viewer.nom_entry.grid(row=0, column=1, padx=5)
            
            # Latitude
            tk.Label(viewer.input_frame, text="Latitude :", width=10, anchor="w").grid(row=1, column=0, padx=5, pady=5)
            viewer.lat_entry = tk.Entry(viewer.input_frame, width=20)
            viewer.lat_entry.grid(row=1, column=1, padx=5, pady=5)
            
            # Longitude
            tk.Label(viewer.input_frame, text="Longitude :", width=10, anchor="w").grid(row=2, column=0, padx=5, pady=5)
            viewer.lon_entry = tk.Entry(viewer.input_frame, width=20)
            viewer.lon_entry.grid(row=2, column=1, padx=5)
            
            # Bouton créer
            tk.Button(viewer.input_frame, text="Créer le point", command=lambda: create_point_from_coords(viewer)).grid(row=3, column=1, columnspan=2, sticky="ew", pady=5, padx=5)
            
            # Bind pour validation en temps réel
            viewer.lat_entry.bind('<KeyRelease>', lambda e: Validate.validate_coords(viewer))
            viewer.lon_entry.bind('<KeyRelease>', lambda e: Validate.validate_coords(viewer))
            
        elif viewer.coord_type.get() == "Degrés/Minutes":
            # Nom
            tk.Label(viewer.input_frame, text="Nom :").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            viewer.nom_entry = tk.Entry(viewer.input_frame)
            viewer.nom_entry.grid(row=0, column=1, columnspan=4, sticky="ew")
            
            # Latitude
            tk.Label(viewer.input_frame, text="Latitude :").grid(row=1, column=0, sticky="w", padx=5, pady=5)            
            viewer.lat_ns_combo = ttk.Combobox(viewer.input_frame, values=["N", "S"], width=3, state="readonly")
            viewer.lat_ns_combo.grid(row=1, column=1, padx=2,pady=5)
            viewer.lat_ns_combo.set("N")
            viewer.lat_deg_entry = tk.Entry(viewer.input_frame, width=6)
            viewer.lat_deg_entry.grid(row=1, column=2, padx=2,pady=5)
            tk.Label(viewer.input_frame, text="°").grid(row=1, column=3, padx=1, pady=5)
            viewer.lat_min_entry = tk.Entry(viewer.input_frame, width=6)
            viewer.lat_min_entry.grid(row=1, column=4, padx=2, pady=5)
            tk.Label(viewer.input_frame, text="'").grid(row=1, column=5, padx=1, pady=5)
                        
            # Longitude
            tk.Label(viewer.input_frame, text="Longitude :").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            viewer.lon_ew_combo = ttk.Combobox(viewer.input_frame, values=["E", "O"], width=3, state="readonly")
            viewer.lon_ew_combo.grid(row=2, column=1, padx=2,pady=5)
            viewer.lon_ew_combo.set("E")
            viewer.lon_deg_entry = tk.Entry(viewer.input_frame, width=6)
            viewer.lon_deg_entry.grid(row=2, column=2, padx=2,pady=5)
            tk.Label(viewer.input_frame, text="°").grid(row=2, column=3, padx=1, pady=5)
            viewer.lon_min_entry = tk.Entry(viewer.input_frame, width=6)
            viewer.lon_min_entry.grid(row=2, column=4, padx=2, pady=5)
            tk.Label(viewer.input_frame, text="'").grid(row=2, column=5, padx=1)            
            
            # Bouton créer
            tk.Button(viewer.input_frame, text="Créer le point", command=lambda: create_point_from_deg_min(viewer)).grid(row=3, column=1, columnspan=4, pady=10,sticky="ew")
            
            # Bind pour validation
            viewer.lat_deg_entry.bind('<KeyRelease>', lambda e: Validate.validate_deg_min(viewer))
            viewer.lat_min_entry.bind('<KeyRelease>', lambda e: Validate.validate_deg_min(viewer))
            viewer.lon_deg_entry.bind('<KeyRelease>', lambda e: Validate.validate_deg_min(viewer))
            viewer.lon_min_entry.bind('<KeyRelease>', lambda e: Validate.validate_deg_min(viewer))
            
        elif viewer.coord_type.get() == "Degrés/Minutes/Secondes":
            # Nom
            tk.Label(viewer.input_frame, text="Nom :").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            viewer.nom_entry = tk.Entry(viewer.input_frame)
            viewer.nom_entry.grid(row=0, column=1, columnspan=6, sticky="ew")
            
            # Latitude
            tk.Label(viewer.input_frame, text="Latitude :").grid(row=1, column=0, sticky="w", padx=5, pady=5)

            viewer.lat_ns_combo = ttk.Combobox(viewer.input_frame, values=["N", "S"], width=3, state="readonly")
            viewer.lat_ns_combo.grid(row=1, column=1, padx=1, pady=5)
            viewer.lat_ns_combo.set("N")

            viewer.lat_deg_entry = tk.Entry(viewer.input_frame, width=6)
            viewer.lat_deg_entry.grid(row=1, column=2, padx=1, pady=5)

            tk.Label(viewer.input_frame, text="°").grid(row=1, column=3, padx=1, pady=5)

            viewer.lat_min_entry = tk.Entry(viewer.input_frame, width=6)
            viewer.lat_min_entry.grid(row=1, column=4, padx=1, pady=5)

            tk.Label(viewer.input_frame, text="'").grid(row=1, column=5, padx=1, pady=5)

            viewer.lat_sec_entry = tk.Entry(viewer.input_frame, width=6)
            viewer.lat_sec_entry.grid(row=1, column=6, padx=1, pady=5)

            tk.Label(viewer.input_frame, text='"').grid(row=1, column=7, padx=1, pady=5)
            
            
            # Longitude
            tk.Label(viewer.input_frame, text="Longitude :").grid(row=2, column=0, sticky="w", padx=5, pady=5)

            viewer.lon_ew_combo = ttk.Combobox(viewer.input_frame, values=["E", "O"], width=3, state="readonly")
            viewer.lon_ew_combo.grid(row=2, column=1, padx=1)
            viewer.lon_ew_combo.set("E")

            viewer.lon_deg_entry = tk.Entry(viewer.input_frame, width=6)
            viewer.lon_deg_entry.grid(row=2, column=2, padx=1)

            tk.Label(viewer.input_frame, text="°").grid(row=2, column=3, padx=1)

            viewer.lon_min_entry = tk.Entry(viewer.input_frame, width=6)
            viewer.lon_min_entry.grid(row=2, column=4, padx=1)

            tk.Label(viewer.input_frame, text="'").grid(row=2, column=5, padx=1)

            viewer.lon_sec_entry = tk.Entry(viewer.input_frame, width=6)
            viewer.lon_sec_entry.grid(row=2, column=6, padx=1)

            tk.Label(viewer.input_frame, text='"').grid(row=2, column=7, padx=1)
            
            
            # Bouton créer
            tk.Button(viewer.input_frame, text="Créer le point", command=lambda: create_point_from_deg_min_sec(viewer)).grid(row=3, column=1, columnspan=6,sticky='ew', pady=10)
            
            # Bind pour validation
            viewer.lat_deg_entry.bind('<KeyRelease>', lambda e: Validate.validate_deg_min_sec(viewer))
            viewer.lat_min_entry.bind('<KeyRelease>', lambda e: Validate.validate_deg_min_sec(viewer))
            viewer.lat_sec_entry.bind('<KeyRelease>', lambda e: Validate.validate_deg_min_sec(viewer))
            viewer.lon_deg_entry.bind('<KeyRelease>', lambda e: Validate.validate_deg_min_sec(viewer))
            viewer.lon_min_entry.bind('<KeyRelease>', lambda e: Validate.validate_deg_min_sec(viewer))
            viewer.lon_sec_entry.bind('<KeyRelease>', lambda e: Validate.validate_deg_min_sec(viewer))
            
        elif viewer.coord_type.get() == "Calamar":
            # Nom
            tk.Label(viewer.input_frame, text="Nom :").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            viewer.nom_entry = tk.Entry(viewer.input_frame )
            viewer.nom_entry.grid(row=0, column=1, columnspan=2, sticky="ew")
            
            # Axe X (correspond à Y dans Calamar)
            tk.Label(viewer.input_frame, text="Axe Y :").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            viewer.calamar_x_entry = tk.Entry(viewer.input_frame, width=12)
            viewer.calamar_x_entry.grid(row=1, column=1, padx=5)
            viewer.calamar_x_combo = ttk.Combobox(viewer.input_frame, values=["mD", "mG"], width=5, state="readonly")
            viewer.calamar_x_combo.grid(row=1, column=2, padx=5)
            viewer.calamar_x_combo.set("mD")

            # Axe Y (correspond à X dans Calamar)
            tk.Label(viewer.input_frame, text="Axe X :").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            viewer.calamar_y_entry = tk.Entry(viewer.input_frame, width=12)
            viewer.calamar_y_entry.grid(row=2, column=1, padx=5, pady=5)
            viewer.calamar_y_combo = ttk.Combobox(viewer.input_frame, values=["mL", "mC"], width=5, state="readonly")
            viewer.calamar_y_combo.grid(row=2, column=2, padx=5, pady=5)
            viewer.calamar_y_combo.set("mL")
                                    
            # Bouton créer
            tk.Button(viewer.input_frame, text="Créer le point", command=lambda: create_point_from_calamar(viewer)).grid(row=3, column=1, columnspan=2, pady=10,sticky="ew")
            
            # Bind pour validation
            viewer.calamar_y_entry.bind('<KeyRelease>', lambda e: Validate.validate_calamar(viewer))
            viewer.calamar_x_entry.bind('<KeyRelease>', lambda e: Validate.validate_calamar(viewer))

    elif viewer.creation_mode.get() == "radial":
        # Vérifier s'il y a des points disponibles
        conn = sqlite3.connect("point.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM points")
        points = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if points:
            # Nom du nouveau point
            tk.Label(viewer.input_frame, text="Nom :").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            viewer.nom_entry = tk.Entry(viewer.input_frame, width=20)
            viewer.nom_entry.grid(row=0, column=1, columnspan=2, padx=5, sticky="w")
            
            # Point de départ
            tk.Label(viewer.input_frame, text="Point de départ :").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            viewer.radial_point_combo = ttk.Combobox(viewer.input_frame, values=points, width=18, state="readonly")
            viewer.radial_point_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")
            if points:
                viewer.radial_point_combo.set(points[0])
            
            # Distance
            tk.Label(viewer.input_frame, text="Distance :").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            viewer.radial_distance_entry = tk.Entry(viewer.input_frame, width=10)
            viewer.radial_distance_entry.grid(row=2, column=1, padx=5)
            viewer.radial_distance_combo = ttk.Combobox(viewer.input_frame, values=["mètres", "nautiques"], width=8, state="readonly")
            viewer.radial_distance_combo.grid(row=2, column=2, padx=5)
            viewer.radial_distance_combo.set("mètres")
            
            # Gisement
            tk.Label(viewer.input_frame, text="Gisement (°) :").grid(row=3, column=0, sticky="w", padx=5, pady=5)
            viewer.radial_bearing_entry = tk.Entry(viewer.input_frame, width=10)
            viewer.radial_bearing_entry.grid(row=3, column=1, padx=5, pady=5)
            tk.Label(viewer.input_frame, text="0-359").grid(row=3, column=2, padx=5, pady=5, sticky="w")
            
            # Bouton créer
            tk.Button(viewer.input_frame, text="Créer le point", command=lambda: create_point_from_radial(viewer)).grid(row=4, column=1, columnspan=2, pady=10)
            
            # Bind pour validation
            viewer.radial_distance_entry.bind('<KeyRelease>', lambda e: Validate.validate_radial(viewer))
            viewer.radial_bearing_entry.bind('<KeyRelease>', lambda e: Validate.validate_radial(viewer))
        else:
            tk.Label(viewer.input_frame, text="Créez d'abord un point de référence", fg="gray").pack(pady=(10,10))
    
    elif viewer.creation_mode.get() == "click":
        # Nom
        tk.Label(viewer.input_frame, text="Nom :", width=10, anchor="w").grid(row=0, column=0, padx=5, pady=5)
        viewer.click_nom_entry = tk.Entry(viewer.input_frame, width=20)
        viewer.click_nom_entry.grid(row=0, column=1, padx=5)
        
        # Latitude (lecture seule)
        tk.Label(viewer.input_frame, text="Latitude :", width=10, anchor="w").grid(row=1, column=0, padx=5, pady=5)
        viewer.click_lat_entry = tk.Entry(viewer.input_frame, width=20, state="readonly")
        viewer.click_lat_entry.grid(row=1, column=1, padx=5)
        
        # Longitude (lecture seule)
        tk.Label(viewer.input_frame, text="Longitude :", width=10, anchor="w").grid(row=2, column=0, padx=5, pady=5)
        viewer.click_lon_entry = tk.Entry(viewer.input_frame, width=20, state="readonly")
        viewer.click_lon_entry.grid(row=2, column=1, padx=5)
        
        # Bouton créer
        tk.Button(viewer.input_frame, text="Créer le point", command=lambda: create_point_from_click(viewer)).grid(row=3, column=1, columnspan=1, sticky="ew", pady=5, padx=5)
        
        # Bind pour validation
        viewer.click_nom_entry.bind('<KeyRelease>', lambda e: Validate.validate_click_point(viewer))
                            
    else:
        viewer.coord_combo.pack_forget()

def right_click_get_coordinate(viewer, event):
    """Gérer le clic droit sur la carte pour renvoyer les coordonneés si mode Click droit"""
    if viewer.creation_mode.get() != "click":
        return
    
    # Convertir coordonnées pixel en lat/lon
    lat, lon = Utility.pixel_to_latlon(
        event.x, event.y, 
        viewer.offset_x, viewer.offset_y,
        viewer.min_col, viewer.max_row, viewer.zoom
    )
    
    # Mettre à jour les champs dans l'interface
    if hasattr(viewer, 'click_lat_entry') and hasattr(viewer, 'click_lon_entry'):
        viewer.click_lat_entry.config(state="normal")
        viewer.click_lat_entry.delete(0, tk.END)
        viewer.click_lat_entry.insert(0, f"{lat:.6f}")
        viewer.click_lat_entry.config(state="readonly")
        
        viewer.click_lon_entry.config(state="normal")
        viewer.click_lon_entry.delete(0, tk.END)
        viewer.click_lon_entry.insert(0, f"{lon:.6f}")
        viewer.click_lon_entry.config(state="readonly")

def create_point_from_click(viewer):
    """Créer un point dans la base de donnée à partir du mode click"""
    if not Validate.validate_click_point(viewer):
        messagebox.showerror("Erreur", "Le nom du point est obligatoire")
        return
    
    nom = viewer.click_nom_entry.get().strip()
    lat_text = viewer.click_lat_entry.get()
    lon_text = viewer.click_lon_entry.get()
    
    if not lat_text or not lon_text:
        messagebox.showerror("Erreur", "Cliquez d'abord sur la carte pour sélectionner les coordonnées")
        return
    
    try:
        lat = float(lat_text)
        lon = float(lon_text)
    except ValueError:
        messagebox.showerror("Erreur", "Coordonnées invalides")
        return
    
    # Ajouter à la base de données
    try:
        close_db_connections()  # Fermer toutes les connexions ouvertes
        conn = sqlite3.connect("point.db", timeout=10.0)
        cursor = conn.cursor()    
        cursor.execute(
            "INSERT INTO points (name, lat, lon) VALUES (?, ?, ?)",
            (nom, lat, lon)
        )
        conn.commit()
        conn.close()
        
        # Recharger la liste des points
        load_points(viewer)
        messagebox.showinfo("Succès", f"Point '{nom}' créé avec succès")
        
        # Réinitialiser les champs
        viewer.click_nom_entry.delete(0, tk.END)
        viewer.click_lat_entry.delete(0, tk.END)
        viewer.click_lon_entry.delete(0, tk.END)
        
    except sqlite3.IntegrityError:
        messagebox.showerror("Erreur", f"Un point avec le nom '{nom}' existe déjà")
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création du point: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def create_point_from_coords(viewer):
    """Créer un point à partir des coordonnées saisies"""
    nom = viewer.nom_entry.get().strip()
    lat_text = viewer.lat_entry.get().strip()
    lon_text = viewer.lon_entry.get().strip()
    
    # Vérifications
    if not nom:
        messagebox.showerror("Erreur", "Le nom du point est obligatoire")
        return
    
    if not lat_text or not lon_text:
        messagebox.showerror("Erreur", "Les coordonnées sont obligatoires")
        return
    
    try:
        lat = float(lat_text)
        lon = float(lon_text)
        
        if not (-90 <= lat <= 90):
            messagebox.showerror("Erreur", "La latitude doit être entre -90 et 90")
            return
        
        if not (-180 <= lon <= 180):
            messagebox.showerror("Erreur", "La longitude doit être entre -180 et 180")
            return
            
    except ValueError:
        messagebox.showerror("Erreur", "Format de coordonnées invalide")
        return
    
    # Ajouter à la base de données
    try:
        conn = sqlite3.connect("point.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO points (name, lat, lon) VALUES (?, ?, ?)",
            (nom, lat, lon)
        )
        conn.commit()
        conn.close()
        
        # Recharger la liste des points
        load_points(viewer)
        messagebox.showinfo("Succès", f"Point '{nom}' créé avec succès")
        
        # Réinitialiser les champs
        viewer.nom_entry.delete(0, tk.END)
        viewer.lat_entry.delete(0, tk.END)
        viewer.lon_entry.delete(0, tk.END)
        
    except sqlite3.IntegrityError:
        messagebox.showerror("Erreur", f"Un point avec le nom '{nom}' existe déjà")
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création du point: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def create_point_from_deg_min(viewer):
    """Créer un point à partir des coordonnées degrés/minutes"""
    nom = viewer.nom_entry.get().strip()
    
    if not nom:
        messagebox.showerror("Erreur", "Le nom du point est obligatoire")
        return
    
    try:
        # Latitude
        lat_deg = int(viewer.lat_deg_entry.get())
        lat_min = float(viewer.lat_min_entry.get())
        lat_ns = viewer.lat_ns_combo.get()
        
        # Longitude
        lon_deg = int(viewer.lon_deg_entry.get())
        lon_min = float(viewer.lon_min_entry.get())
        lon_ew = viewer.lon_ew_combo.get()
        
        # Conversion en degrés décimaux
        lat = lat_deg + lat_min / 60
        if lat_ns == "S":
            lat = -lat
            
        lon = lon_deg + lon_min / 60
        if lon_ew == "O":
            lon = -lon
        
        # Vérifications
        if not (0 <= lat_deg <= 90) or not (0 <= lat_min < 60):
            messagebox.showerror("Erreur", "Latitude invalide")
            return
            
        if not (0 <= lon_deg <= 180) or not (0 <= lon_min < 60):
            messagebox.showerror("Erreur", "Longitude invalide")
            return
            
    except ValueError:
        messagebox.showerror("Erreur", "Format de coordonnées invalide")
        return
    
    # Ajouter à la base de données
    try:
        conn = sqlite3.connect("point.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO points (name, lat, lon) VALUES (?, ?, ?)",
            (nom, lat, lon)
        )
        conn.commit()
        conn.close()
        
        # Recharger la liste des points
        load_points(viewer)
        messagebox.showinfo("Succès", f"Point '{nom}' créé avec succès")
        
        # Réinitialiser les champs
        viewer.nom_entry.delete(0, tk.END)
        viewer.lat_deg_entry.delete(0, tk.END)
        viewer.lat_min_entry.delete(0, tk.END)
        viewer.lon_deg_entry.delete(0, tk.END)
        viewer.lon_min_entry.delete(0, tk.END)
        
    except sqlite3.IntegrityError:
        messagebox.showerror("Erreur", f"Un point avec le nom '{nom}' existe déjà")
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création du point: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    
def create_point_from_deg_min_sec(viewer):
    """Créer un point à partir des coordonnées degrés/minutes/secondes"""
    nom = viewer.nom_entry.get().strip()
    
    if not nom:
        messagebox.showerror("Erreur", "Le nom du point est obligatoire")
        return
    
    try:
        # Latitude
        lat_deg = int(viewer.lat_deg_entry.get())
        lat_min = int(viewer.lat_min_entry.get())
        lat_sec = float(viewer.lat_sec_entry.get())
        lat_ns = viewer.lat_ns_combo.get()
        
        # Longitude
        lon_deg = int(viewer.lon_deg_entry.get())
        lon_min = int(viewer.lon_min_entry.get())
        lon_sec = float(viewer.lon_sec_entry.get())
        lon_ew = viewer.lon_ew_combo.get()
        
        # Conversion en degrés décimaux
        lat = lat_deg + lat_min / 60 + lat_sec / 3600
        if lat_ns == "S":
            lat = -lat
            
        lon = lon_deg + lon_min / 60 + lon_sec / 3600
        if lon_ew == "O":
            lon = -lon
        
        # Vérifications
        if not (0 <= lat_deg <= 90) or not (0 <= lat_min < 60) or not (0 <= lat_sec < 60):
            messagebox.showerror("Erreur", "Latitude invalide")
            return
            
        if not (0 <= lon_deg <= 180) or not (0 <= lon_min < 60) or not (0 <= lon_sec < 60):
            messagebox.showerror("Erreur", "Longitude invalide")
            return
            
    except ValueError:
        messagebox.showerror("Erreur", "Format de coordonnées invalide")
        return
    
    # Ajouter à la base de données
    try:
        conn = sqlite3.connect("point.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO points (name, lat, lon) VALUES (?, ?, ?)",
            (nom, lat, lon)
        )
        conn.commit()
        conn.close()
        
        # Recharger la liste des points
        load_points(viewer)
        messagebox.showinfo("Succès", f"Point '{nom}' créé avec succès")
        
        # Réinitialiser les champs
        viewer.nom_entry.delete(0, tk.END)
        viewer.lat_deg_entry.delete(0, tk.END)
        viewer.lat_min_entry.delete(0, tk.END)
        viewer.lat_sec_entry.delete(0, tk.END)
        viewer.lon_deg_entry.delete(0, tk.END)
        viewer.lon_min_entry.delete(0, tk.END)
        viewer.lon_sec_entry.delete(0, tk.END)
        
    except sqlite3.IntegrityError:
        messagebox.showerror("Erreur", f"Un point avec le nom '{nom}' existe déjà")
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création du point: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    load_points(viewer)

def create_point_from_calamar(viewer):
    """Créer un point à partir des coordonnées Calamar"""
    nom = viewer.nom_entry.get().strip()
    
    if not nom:
        messagebox.showerror("Erreur", "Le nom du point est obligatoire")
        return
    
    try:
        y_val = float(viewer.calamar_x_entry.get())
        x_val = float(viewer.calamar_y_entry.get())
        y_unit = viewer.calamar_x_combo.get()
        x_unit = viewer.calamar_y_combo.get()
        
        # Conversion en GPS
        lat, lon = Utility.convert_calamar_to_gps(x_val, y_val, x_unit, y_unit)
        
    except ValueError:
        messagebox.showerror("Erreur", "Format de coordonnées invalide")
        return
    
    # Ajouter à la base de données
    conn = sqlite3.connect("point.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO points (name, lat, lon) VALUES (?, ?, ?)",
        (nom, lat, lon)
    )
    conn.commit()
    conn.close()
        
    # Vider les champs
    viewer.nom_entry.delete(0, tk.END)
    viewer.calamar_y_entry.delete(0, tk.END)
    viewer.calamar_x_entry.delete(0, tk.END)
    viewer.calamar_y_combo.set("mL")
    viewer.calamar_x_combo.set("mD")
    
    # Recharger la liste des points
    load_points(viewer)

def create_point_from_radial(viewer):
    """Créer un point à partir d'un relèvement/distance"""
    nom = viewer.nom_entry.get().strip()
    point_depart_nom = viewer.radial_point_combo.get()
    
    if not nom:
        messagebox.showerror("Erreur", "Le nom du point est obligatoire")
        return
    
    if not point_depart_nom:
        messagebox.showerror("Erreur", "Sélectionnez un point de départ")
        return
    
    try:
        distance_val = float(viewer.radial_distance_entry.get())
        bearing_deg = float(viewer.radial_bearing_entry.get())
        distance_unit = viewer.radial_distance_combo.get()
        
        if distance_val <= 0:
            messagebox.showerror("Erreur", "La distance doit être positive")
            return
        
        if not (0 <= bearing_deg < 360):
            messagebox.showerror("Erreur", "Le gisement doit être entre 0 et 359°")
            return
        
    except ValueError:
        messagebox.showerror("Erreur", "Valeurs numériques invalides")
        return
    
    # Récupérer le point de départ
    conn = sqlite3.connect("point.db")
    cursor = conn.cursor()
    cursor.execute("SELECT lat, lon FROM points WHERE name = ?", (point_depart_nom,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        messagebox.showerror("Erreur", "Point de départ introuvable")
        return
    
    start_point = {"lat": result[0], "lon": result[1]}
    
    # Convertir la distance en km
    distance_km = distance_val * 1.852 if distance_unit == "nautiques" else distance_val / 1000
    
    # Calculer le nouveau point
    new_lat, new_lon = Utility.create_point_from_bearing_distance(start_point, distance_km, bearing_deg)
    
    # Ajouter à la base de données
    conn = sqlite3.connect("point.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO points (name, lat, lon) VALUES (?, ?, ?)",
        (nom, new_lat, new_lon)
    )
    conn.commit()
    conn.close()
        
    # Vider les champs
    viewer.nom_entry.delete(0, tk.END)
    viewer.radial_distance_entry.delete(0, tk.END)
    viewer.radial_bearing_entry.delete(0, tk.END)
    
    # Recharger la liste des points
    load_points(viewer)

def load_points(viewer):
    """Afficher les points sur la carte"""
    for item in viewer.tree.get_children():
        viewer.tree.delete(item)
    
    viewer.checked_items = {}
    conn = sqlite3.connect("point.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, lat, lon FROM points")
    for row in cursor.fetchall():
        item_id = viewer.tree.insert("", tk.END, values=("⬜", row[0], f"{row[1]:.6f}", f"{row[2]:.6f}"))
        viewer.checked_items[item_id] = {"checked": False, "data": row}
    conn.close()
    
    # Mettre à jour l'affichage sur la carte
    viewer.mbtiles_manager.draw_points()

def on_tree_click(viewer, event):
    """Gérer le clic sur le treeview"""
    region = viewer.tree.identify_region(event.x, event.y)
    if region == "cell":
        item = viewer.tree.identify_row(event.y)
        column = viewer.tree.identify_column(event.x)
        
        if column == "#1" and item in viewer.checked_items:
            toggle_checkbox(viewer, item)

def on_tree_double_click(viewer, event):
    """Gérer le double-clic sur le treeview pour centrer la carte"""
    # Identifier l'élément double-cliqué
    item = viewer.tree.identify_row(event.y)
    
    if item and item in viewer.checked_items:
        # Récupérer les données du point
        point_data = viewer.checked_items[item]["data"]
        name, lat, lon = point_data
        
        # Vérifier qu'on a une carte chargée avant de centrer
        if hasattr(viewer, 'mbtiles_manager') and viewer.db_path:
            # Centrer la carte sur ce point
            viewer.mbtiles_manager.center_map_on_point(lat, lon)
            
            # Optionnel : afficher un message pour confirmer l'action
            print(f"Carte centrée sur le point '{name}' ({lat:.6f}, {lon:.6f})")
        else:
            print("Aucune carte chargée - impossible de centrer")

def toggle_checkbox(viewer, item):
    """Basculer l'état de la case à cocher"""
    current_state = viewer.checked_items[item]["checked"]
    new_state = not current_state
    viewer.checked_items[item]["checked"] = new_state
    
    values = list(viewer.tree.item(item)["values"])
    values[0] = "✅" if new_state else "⬜"
    viewer.tree.item(item, values=values)

def select_all_treeview(viewer):
    """Cocher toutes les cases du treeview"""
    for item in viewer.checked_items:
        viewer.checked_items[item]["checked"] = True
        values = list(viewer.tree.item(item)["values"])
        values[0] = "✅"
        viewer.tree.item(item, values=values)

def deselect_all_treeview(viewer):
    """Décocher toutes les cases du treeview"""
    for item in viewer.checked_items:
        viewer.checked_items[item]["checked"] = False
        values = list(viewer.tree.item(item)["values"])
        values[0] = "⬜"
        viewer.tree.item(item, values=values)

def delete_selected_points(viewer):
    """Supprimer les points cochés de la base de données et du treeview"""
    to_delete = [item for item, info in viewer.checked_items.items() if info["checked"]]
    if not to_delete:
        messagebox.showwarning("Suppression", "Aucun point sélectionné.")
        return
    
    try:
        conn = sqlite3.connect("point.db")
        cursor = conn.cursor()
        for item in to_delete:
            name = viewer.tree.item(item)["values"][1]
            cursor.execute("DELETE FROM points WHERE name = ?", (name,))
        conn.commit()
        conn.close()
        
        load_points(viewer)
        messagebox.showinfo("Suppression", f"{len(to_delete)} point(s) supprimé(s).")
        
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    