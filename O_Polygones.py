from numpy import pad
from pyparsing import col
import Utility
import tkinter as tk
from tkinter import W, ttk, messagebox
import sqlite3

def setup_notebook_tabs_polygone(viewer):
    """Configurer l'onglet Polygone"""

    # Configurer le style de l'onglet
    style = ttk.Style()
    style.configure('TNotebook.Tab', font=('Arial', 10))  # Onglet normal
    style.map('TNotebook.Tab', font=[('selected', ('Arial', 10, 'bold'))])  # Onglet sélectionné en gras
    
    # Onglet polygone
    viewer.polygone_frame = ttk.Frame(viewer.notebook)
    viewer.notebook.add(viewer.polygone_frame, text="  Polygones  ")

    # Variable pour récuperer les choix de l'utilisateur
    viewer.pol_creation_mode = tk.StringVar(value="points")
    
    # Frame pour tous les radiobuttons
    coord_frame = tk.Frame(viewer.polygone_frame, relief='groove', borderwidth=1)
    coord_frame.pack(fill=tk.X, padx=5, pady=5)

    ttk.Radiobutton(coord_frame, text="Base de données de points", variable=viewer.pol_creation_mode, value="points", command=lambda: update_input_frame(viewer)).pack(anchor='w', padx=5, pady=3)
    ttk.Radiobutton(coord_frame, text="Rectangle", variable=viewer.pol_creation_mode, value="rectangle", command=lambda: update_input_frame(viewer)).pack(anchor='w', padx=5, pady=3)
    ttk.Radiobutton(coord_frame, text="Cercles", variable=viewer.pol_creation_mode, value="cercles", command=lambda: update_input_frame(viewer)).pack(anchor='w', padx=5, pady=3)
    
    # Frame pour les champs de saisie
    viewer.pol_input_frame = tk.Frame(viewer.polygone_frame, relief='groove', borderwidth=1)
    viewer.pol_input_frame.pack(fill=tk.X, padx=5, pady=5)

    # Fonction de formattage de l'entrée selon le mode
    update_input_frame(viewer)

    # Frame Nom polygone + Couleur + Largeur + Remplissage + Bouton créer
    name_frame = ttk.Frame(viewer.polygone_frame, relief=tk.GROOVE, borderwidth=2)
    name_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)

    ttk.Label(name_frame, text="Nom du polygone : ").grid(row=0,column=0, sticky=tk.W, pady=(5,5), padx=(5,5))
    viewer.polygone_name_entry = ttk.Entry(name_frame, width=20)
    viewer.polygone_name_entry.grid(row=0,column=1, pady=(5,5), padx=(5,5),sticky="ew")

    ttk.Label(name_frame, text="Couleur : ").grid(row=1,column=0, sticky=tk.W, padx=(5,5), pady=(5,5))
    colors = ["rouge", "vert", "bleu", "jaune", "orange", "cyan", "magenta", "noir", "blanc"]
    viewer.polygone_color_entry = ttk.Combobox(name_frame, values=colors, state="readonly", width=10)
    viewer.polygone_color_entry.current(0)
    viewer.polygone_color_entry.grid(row=1,column=1, padx=(5,5),sticky="ew", pady=(5,5))

    ttk.Label(name_frame, text="Largeur : ").grid(row=2,column=0, sticky=tk.W, padx=(5,5), pady=(5,5))
    viewer.polygone_width_entry = ttk.Combobox(name_frame, values=[str(i) for i in range(1, 11)], state="readonly", width=5)
    viewer.polygone_width_entry.current(1)
    viewer.polygone_width_entry.grid(row=2,column=1, padx=(5,5),sticky="ew", pady=(5,5))

    ttk.Label(name_frame, text="Remplir : ").grid(row=3,column=0, sticky=tk.W, padx=(5,5), pady=(5,5))
    viewer.polygone_fill_var = tk.IntVar()
    ttk.Checkbutton(name_frame, variable=viewer.polygone_fill_var).grid(row=3,column=1, padx=(5,5),sticky="w", pady=(5,5))

    ttk.Button(name_frame, text="Créer polygone", command=lambda: create_polygone(viewer)).grid(row=4,column=1, sticky='ew', pady=(5,5), padx=(5,5))
    
    #Gestion du treeview des polygones
    tree_frame_manager(viewer)

    # Charger les données initiales
    load_points_polygone(viewer)
    load_polygones(viewer)

    # Bind pour rafraîchir quand l'onglet devient actif
    viewer.notebook.bind("<<NotebookTabChanged>>", lambda e: refresh_on_tab_change_polygone(viewer))

def tree_frame_manager(viewer):
        """Gère l'affichage du treeview contenant les objets polygones"""

        # Création d'un frame "tree_frame" pour afficher les polygones existants
        tree_frame = ttk.Frame(viewer.polygone_frame, relief=tk.GROOVE, borderwidth=2)
        tree_frame.pack(fill=tk.X,anchor='n', expand=False,  padx=5, pady=5)

        ttk.Label(tree_frame, text="Polygones :", font=("Arial", 10)).pack(anchor=tk.W,pady=(4,4),padx=5)

        # Création du Treeview dans "tree_frame" pour afficher les polygones
        viewer.polygones_tree = ttk.Treeview(tree_frame, columns=("selected", "Nom", "Color", "Width", "Fill"), show="headings", height=4)
        
        viewer.polygones_tree.heading("selected", text="Export")
        viewer.polygones_tree.heading("Nom", text="Nom")
        viewer.polygones_tree.heading("Color", text="Couleur")
        viewer.polygones_tree.heading("Width", text="Largeur")
        viewer.polygones_tree.heading("Fill", text="Remplir")

        viewer.polygones_tree.column("selected", width=50, anchor="center", stretch=False)
        viewer.polygones_tree.column("Nom", width=50, anchor="center", stretch=True)
        viewer.polygones_tree.column("Color", width=50, anchor="center", stretch=True)
        viewer.polygones_tree.column("Width", width=50, anchor="center", stretch=True)
        viewer.polygones_tree.column("Fill", width=50, anchor="center", stretch=True)

        viewer.polygones_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Création des boutons de gestion du treeview dans "tree_frame"
        btn_select_all = ttk.Button(tree_frame, text="Sélectionner tout", width=15, command=lambda: select_all_polygones_treeview(viewer))
        btn_select_all.pack(side=tk.LEFT, padx=5)
        btn_deselect_all = ttk.Button(tree_frame, text="Désélectionner tout", command=lambda: deselect_all_polygones_treeview(viewer))
        btn_deselect_all.pack(side=tk.LEFT, padx=5)
        btn_delete = ttk.Button(tree_frame, text="Supprimer", command=lambda: delete_selected_polygones(viewer))
        btn_delete.pack(side=tk.LEFT, padx=5)         

        def on_polygones_tree_click(event):
            region = viewer.polygones_tree.identify("region", event.x, event.y)
            if region == "cell":
                col = viewer.polygones_tree.identify_column(event.x)
                if col == "#1":
                    item = viewer.polygones_tree.identify_row(event.y)
                    if item:
                        current_state = viewer.checked_polygones.get(item, {"checked": False})["checked"]
                        new_state = not current_state

                        # Met à jour l'état coché dans le dictionnaire
                        viewer.checked_polygones[item] = {"checked": new_state}
                        
                        #Mise à jour de l'affichage
                        values = list(viewer.polygones_tree.item(item)["values"])
                        values[0] = "✅" if new_state else "⬜"
                        viewer.polygones_tree.item(item, values=values)        

        def select_all_polygones_treeview(viewer):
            for item in viewer.checked_polygones:
                viewer.checked_polygones[item]["checked"] = True
                values = list(viewer.polygones_tree.item(item)["values"])
                values[0] = "✅"
                viewer.polygones_tree.item(item, values=values)

        def deselect_all_polygones_treeview(viewer):
            for item in viewer.checked_polygones:
                viewer.checked_polygones[item]["checked"] = False
                values = list(viewer.polygones_tree.item(item)["values"])
                values[0] = "⬜"
                viewer.polygones_tree.item(item, values=values)

        def delete_selected_polygones(viewer):

            to_delete = [item for item, info in viewer.checked_polygones.items() if info["checked"]]
            if not to_delete:
                messagebox.showwarning("Suppression", "Aucun polygone sélectionné.")
                return
            conn = sqlite3.connect("polygone.db")
            cursor = conn.cursor()
            for item in to_delete:
                name = viewer.polygones_tree.item(item)["values"][1]
                cursor.execute("DELETE FROM polygons WHERE name = ?", (name,))
            conn.commit()
            conn.close()
            load_polygones(viewer)
            messagebox.showinfo("Suppression", f"{len(to_delete)} polygone(s) supprimé(s).")

        # Initialiser le suivi des cases cochées
        viewer.checked_polygones = {}

        #Gestion du clic_gauche sur les cases à cocher du treeview
        viewer.polygones_tree.bind("<Button-1>", on_polygones_tree_click)
        #Gestion du double-clic pour centrer la carte
        viewer.polygones_tree.bind("<Double-1>", lambda event: on_polygones_tree_double_click(viewer, event))

def update_input_frame(viewer):
    """Met à jour le contenu du frame de saisie selon le mode sélectionné"""    
    
    # Effacer le contenu actuel
    for widget in viewer.pol_input_frame.winfo_children():
        widget.destroy()
     
    # Affiche les widgets en fonction du format des coordonnées
    mode = viewer.pol_creation_mode.get()
    if mode == "points":
        print("Mode Points sélectionné")

        # Frame principal avec deux colonnes
        viewer.p_frame = ttk.Frame(viewer.pol_input_frame, relief=tk.GROOVE, borderwidth=2)
        viewer.p_frame.pack(fill=tk.BOTH, expand=True)
        # Fixer la largeur minimale de la colonne des labels pour aligner les champs
        viewer.p_frame.grid_columnconfigure(0, minsize=130, weight=0)

        # Frame gauche pour les points disponibles
        left_frame = ttk.Frame(viewer.p_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(left_frame, text="Points :", font=("Arial", 10)).pack(anchor=tk.W,padx=(5,5))
        viewer.points_listbox_poly = tk.Listbox(left_frame, height=8)
        viewer.points_listbox_poly.pack(fill=tk.BOTH, expand=False, pady=(5, 5), padx=(5,5))

        # Recharge la listbox des points à chaque sélection du mode 'points'
        load_points_polygone(viewer)

        # Frame central pour les boutons
        viewer.center_frame = ttk.Frame(viewer.p_frame, width=50)
        viewer.center_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        viewer.center_frame.pack_propagate(False)
        ttk.Button(viewer.center_frame, text=">>", command=lambda: add_point_to_polygone(viewer), width=6).pack(pady=(50, 5))
        ttk.Button(viewer.center_frame, text="<<", command=lambda: remove_point_from_polygone(viewer), width=6).pack(pady=5)

        # Frame droite pour le polygone en cours
        right_frame = ttk.Frame(viewer.p_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        ttk.Label(right_frame, text="Polygone:", font=("Arial", 10)).pack(anchor=tk.W)
        viewer.polygone_points_listbox = tk.Listbox(right_frame, height=8)
        viewer.polygone_points_listbox.pack(fill=tk.BOTH, expand=False, pady=(5, 5), padx=(5,5))      # Liste des points disponibles
    
    elif mode == "rectangle":
        print("Mode Rectangle sélectionné")
        viewer.p_frame = ttk.Frame(viewer.pol_input_frame, relief=tk.GROOVE, borderwidth=2)
        viewer.p_frame.pack(fill=tk.BOTH, expand=True)

        # Sélection du centre du rectangle
        ttk.Label(viewer.p_frame, text="Centre du rectangle :", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        # Récupérer les points depuis la base
        try:
            conn = sqlite3.connect("point.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM points ORDER BY name")
            points = [row[0] for row in cursor.fetchall()]
            conn.close()
        except sqlite3.Error:
            points = []
        viewer.rectangle_center_combo = ttk.Combobox(viewer.p_frame, values=points, state="readonly", width=14)
        if points:
            viewer.rectangle_center_combo.current(0)
        viewer.rectangle_center_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

        # Largeur et longueur
        ttk.Label(viewer.p_frame, text="Longueur :", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        viewer.rectangle_length_entry = ttk.Entry(viewer.p_frame, width=14)
        viewer.rectangle_length_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        viewer.rectangle_length_unit = ttk.Combobox(viewer.p_frame, values=["m", "Nm"], state="readonly", width=7)
        viewer.rectangle_length_unit.current(0)
        viewer.rectangle_length_unit.grid(row=1, column=2, sticky='ew',padx=5, pady=5)

        ttk.Label(viewer.p_frame, text="Largeur :", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        viewer.rectangle_width_entry = ttk.Entry(viewer.p_frame, width=14)
        viewer.rectangle_width_entry.grid(row=2, column=1, sticky='ew',padx=5, pady=5)
        viewer.rectangle_width_unit = ttk.Combobox(viewer.p_frame, values=["m", "Nm"], state="readonly", width=7)
        viewer.rectangle_width_unit.current(0)
        viewer.rectangle_width_unit.grid(row=2, column=2, sticky='ew', padx=5, pady=5)

        # Orientation
        ttk.Label(viewer.p_frame, text="Orientation (degrés) :", font=("Arial", 10)).grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        viewer.rectangle_orientation_entry = ttk.Entry(viewer.p_frame, width=14)
        viewer.rectangle_orientation_entry.grid(row=5, column=1, sticky='ew', padx=5, pady=5)

        # Ajouter flèche d'orientation
        ttk.Label(viewer.p_frame, text="Ajouter fleche :", font=("Arial", 10)).grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        viewer.rectangle_add_arrow_var = tk.IntVar()
        ttk.Checkbutton(viewer.p_frame, variable=viewer.rectangle_add_arrow_var).grid(row=6, column=1, sticky='w', padx=5, pady=5)

        # Fixer la largeur de la colonne 1 pour tous les widgets
        viewer.p_frame.grid_columnconfigure(1, minsize=80, weight=0)
    
    elif mode == "cercles":
        print("Mode Cercles sélectionné")
        viewer.p_frame = ttk.Frame(viewer.pol_input_frame, relief=tk.GROOVE, borderwidth=2)
        viewer.p_frame.pack(fill=tk.BOTH, expand=True)
        viewer.p_frame.grid_columnconfigure(0, minsize=150, weight=0)

        # Sélection du centre du cercle
        ttk.Label(viewer.p_frame, text="Centre du cercle :", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        # Récupérer les points depuis la base
        try:
            conn = sqlite3.connect("point.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM points ORDER BY name")
            points = [row[0] for row in cursor.fetchall()]
            conn.close()
        except sqlite3.Error:
            points = []
        viewer.cercle_center_combo = ttk.Combobox(viewer.p_frame, values=points, state="readonly", width=14)
        if points:
            viewer.cercle_center_combo.current(0)
        viewer.cercle_center_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

        # Rayon
        ttk.Label(viewer.p_frame, text="Rayon :", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        viewer.cercle_rayon_entry = ttk.Entry(viewer.p_frame, width=14)
        viewer.cercle_rayon_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        viewer.cercle_rayon_unit = ttk.Combobox(viewer.p_frame, values=["m", "Nm"], state="readonly", width=7)
        viewer.cercle_rayon_unit.current(0)
        viewer.cercle_rayon_unit.grid(row=1, column=2, sticky='ew', padx=5, pady=5)

        # Nombre de segments
        ttk.Label(viewer.p_frame, text="Nombre de segments :", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        viewer.cercle_segments_entry = ttk.Entry(viewer.p_frame, width=14)
        viewer.cercle_segments_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)

        # Arc de cercle
        viewer.cercle_arc_var = tk.IntVar()
        viewer.cercle_arc_radio = ttk.Checkbutton(viewer.p_frame, text="Arc de cercle", variable=viewer.cercle_arc_var, command=lambda: update_arc_fields(viewer))
        viewer.cercle_arc_radio.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        # Frame pour les champs d'arc (affiché si arc sélectionné)
        viewer.arc_fields_frame = ttk.Frame(viewer.p_frame)
        viewer.arc_fields_frame.grid(row=4, column=0, columnspan=3, sticky='ew', pady=5)        
        # Fixer la largeur et l'extension de la colonne 1 pour les champs cercles et arc
        viewer.arc_fields_frame.grid_columnconfigure(0, minsize=150, weight=0)
        
        def update_arc_fields(viewer):
            # Efface le contenu du frame arc_fields_frame
            for widget in viewer.arc_fields_frame.winfo_children():
                widget.destroy()
            if viewer.cercle_arc_var.get():
                # Angle de début
                ttk.Label(viewer.arc_fields_frame, text="Angle de début :", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
                viewer.arc_start_entry = ttk.Entry(viewer.arc_fields_frame, width=14)
                viewer.arc_start_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
                # Angle de fin
                ttk.Label(viewer.arc_fields_frame, text="Angle de fin :", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
                viewer.arc_end_entry = ttk.Entry(viewer.arc_fields_frame, width=14)
                viewer.arc_end_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
                # Relier au centre
                viewer.arc_relie_var = tk.IntVar()
                viewer.arc_relie_radio = ttk.Checkbutton(viewer.arc_fields_frame, text="Relier au centre", variable=viewer.arc_relie_var)
                viewer.arc_relie_radio.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        # Initialiser l'affichage des champs d'arc
        update_arc_fields(viewer)
    
    # Mettre à jour les combobox de sélection de points après création de l'interface
    if hasattr(viewer, 'notebook'):  # Vérifier que l'interface est initialisée
        update_point_combos(viewer)
        
def load_points_polygone(app):
    """Charger tous les points depuis point.db"""
    app.points_listbox_poly.delete(0, tk.END)
    try:
        conn = sqlite3.connect("point.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM points ORDER BY name")
        points = cursor.fetchall()
        conn.close()
        
        for point in points:
            app.points_listbox_poly.insert(tk.END, point[0])
    except sqlite3.Error:
        pass

def add_point_to_polygone(app):
    """Ajouter un point sélectionné au polygone"""
    selection = app.points_listbox_poly.curselection()
    if selection:
        point_name = app.points_listbox_poly.get(selection[0])
        app.polygone_points_listbox.insert(tk.END, point_name)

def remove_point_from_polygone(app):
    """Retirer un point sélectionné du polygone"""
    selection = app.polygone_points_listbox.curselection()
    if selection:
        app.polygone_points_listbox.delete(selection[0])

def create_polygone(app):
    """Créer un nouveau polygone et l'enregistrer dans polygone.db"""
    polygone_name = app.polygone_name_entry.get().strip()
    color = app.polygone_color_entry.get().strip() or "rouge"
    width = app.polygone_width_entry.get().strip() or "2"
    fill = app.polygone_fill_var.get()
    if not polygone_name:
        messagebox.showerror("Erreur", "Veuillez entrer un nom pour le polygone")
        return
    
    mode = app.pol_creation_mode.get()
    coordinates_list = []
    
    try:
        if mode == "points":
            # Récupérer les noms des points du polygone
            point_names = [app.polygone_points_listbox.get(i) for i in range(app.polygone_points_listbox.size())]
            if len(point_names) < 3:
                messagebox.showerror("Erreur", "Un polygone doit contenir au moins 3 points")
                return
            
            # Récupérer les coordonnées des points depuis point.db
            conn_points = sqlite3.connect("point.db")
            cursor_points = conn_points.cursor()
            
            for point_name in point_names:
                cursor_points.execute("SELECT lat, lon FROM points WHERE name = ?", (point_name,))
                result = cursor_points.fetchone()
                if result:
                    lat, lon = result
                    # Stocker les coordonnées au format "lon,lat,0" (z=0 par défaut)
                    coordinates_list.append(f"{lon},{lat},0")
                else:
                    messagebox.showerror("Erreur", f"Point '{point_name}' introuvable dans la base de données")
                    conn_points.close()
                    return
            
            conn_points.close()
            
        elif mode == "rectangle":
            # Récupérer les paramètres du rectangle
            center_name = app.rectangle_center_combo.get().strip()
            if not center_name:
                messagebox.showerror("Erreur", "Veuillez sélectionner un point centre")
                return
                
            length_str = app.rectangle_length_entry.get().strip()
            width_str = app.rectangle_width_entry.get().strip()
            orientation_str = app.rectangle_orientation_entry.get().strip() or "0"
            
            if not length_str or not width_str:
                messagebox.showerror("Erreur", "Veuillez entrer la longueur et la largeur")
                return
            
            try:
                length = float(length_str)
                width = float(width_str)
                orientation = float(orientation_str)
            except ValueError:
                messagebox.showerror("Erreur", "Valeurs numériques invalides")
                return
            
            # Convertir les unités en kilomètres si nécessaire
            length_unit = app.rectangle_length_unit.get()
            width_unit = app.rectangle_width_unit.get()
            
            if length_unit == "Nm":
                length = length * 1.852  # Conversion miles nautiques vers km
            elif length_unit == "m":
                length = length / 1000  # Conversion mètres vers km
                
            if width_unit == "Nm":
                width = width * 1.852  # Conversion miles nautiques vers km
            elif width_unit == "m":
                width = width / 1000  # Conversion mètres vers km
            
            # Récupérer les coordonnées du point centre
            conn_points = sqlite3.connect("point.db")
            cursor_points = conn_points.cursor()
            cursor_points.execute("SELECT lat, lon FROM points WHERE name = ?", (center_name,))
            center_result = cursor_points.fetchone()
            conn_points.close()
            
            if not center_result:
                messagebox.showerror("Erreur", f"Point centre '{center_name}' introuvable")
                return
            
            center_lat, center_lon = center_result
            
            # Calculer les points du rectangle
            rectangle_points = Utility.calculate_rectangle_points(center_lat, center_lon, length, width, orientation)
            
            # Convertir au format attendu pour la base de données
            for lon, lat in rectangle_points:
                coordinates_list.append(f"{lon},{lat},0")
            
            # Ajouter la flèche d'orientation si demandée
            add_arrow = app.rectangle_add_arrow_var.get()
            if add_arrow:
                arrow_points = Utility.calculate_arrow_points(center_lat, center_lon, length, orientation, width)
                # Ajouter les points de la flèche après le rectangle
                for lon, lat in arrow_points:
                    coordinates_list.append(f"{lon},{lat},0")
        
        elif mode == "cercles":
            # Récupérer les paramètres du cercle
            center_name = app.cercle_center_combo.get().strip()
            if not center_name:
                messagebox.showerror("Erreur", "Veuillez sélectionner un point centre")
                return
            
            radius_str = app.cercle_rayon_entry.get().strip()
            segments_str = app.cercle_segments_entry.get().strip() or "32"
            
            if not radius_str:
                messagebox.showerror("Erreur", "Veuillez entrer le rayon")
                return
            
            try:
                radius = float(radius_str)
                segments = int(segments_str)
            except ValueError:
                messagebox.showerror("Erreur", "Valeurs numériques invalides")
                return
            
            # Convertir les unités en kilomètres si nécessaire
            radius_unit = app.cercle_rayon_unit.get()
            if radius_unit == "Nm":
                radius = radius * 1.852  # Conversion miles nautiques vers km
            elif radius_unit == "m":
                radius = radius / 1000  # Conversion mètres vers km
            
            # Récupérer les coordonnées du point centre
            conn_points = sqlite3.connect("point.db")
            cursor_points = conn_points.cursor()
            cursor_points.execute("SELECT lat, lon FROM points WHERE name = ?", (center_name,))
            center_result = cursor_points.fetchone()
            conn_points.close()
            
            if not center_result:
                messagebox.showerror("Erreur", f"Point centre '{center_name}' introuvable")
                return
            
            center_lat, center_lon = center_result
            
            # Vérifier s'il s'agit d'un arc
            is_arc = app.cercle_arc_var.get()
            
            if is_arc:
                # Récupérer les paramètres de l'arc
                try:
                    start_angle = float(app.arc_start_entry.get().strip() or "0")
                    end_angle = float(app.arc_end_entry.get().strip() or "360")
                    close_arc = app.arc_relie_var.get()
                except (ValueError, AttributeError):
                    messagebox.showerror("Erreur", "Paramètres d'arc invalides")
                    return
                
                # Calculer les points de l'arc
                circle_points = Utility.calculate_circle_points(
                    center_lat, center_lon, radius, segments, 
                    is_arc=True, start_angle_deg=start_angle, 
                    end_angle_deg=end_angle, close_arc=close_arc
                )
            else:
                # Calculer les points du cercle complet
                circle_points = Utility.calculate_circle_points(
                    center_lat, center_lon, radius, segments, is_arc=False
                )
            
            # Convertir au format attendu pour la base de données
            for lon, lat in circle_points:
                coordinates_list.append(f"{lon},{lat},0")
        
        # Vérifier que nous avons des coordonnées
        if not coordinates_list:
            messagebox.showerror("Erreur", "Aucune coordonnée générée")
            return
        
        conn = sqlite3.connect("polygone.db")
        cursor = conn.cursor()
        # Vérifier si le nom existe déjà
        cursor.execute("SELECT name FROM polygons WHERE name = ?", (polygone_name,))
        if cursor.fetchone():
            messagebox.showerror("Erreur", "Un polygone avec ce nom existe déjà")
            conn.close()
            return
        # Insérer le nouveau polygone avec les coordonnées
        points_str = " ".join(coordinates_list)
        cursor.execute("INSERT INTO polygons (name, color, width, fill, points_list) VALUES (?, ?, ?, ?, ?)",
                      (polygone_name, color, int(width), int(fill), points_str))
        conn.commit()
        conn.close()
        
        # Réinitialiser l'interface
        app.polygone_name_entry.delete(0, tk.END)
        app.polygone_color_entry.delete(0, tk.END)
        app.polygone_width_entry.delete(0, tk.END)
        if mode == "points":
            app.polygone_points_listbox.delete(0, tk.END)
        elif mode == "rectangle":
            app.rectangle_length_entry.delete(0, tk.END)
            app.rectangle_width_entry.delete(0, tk.END)
            app.rectangle_orientation_entry.delete(0, tk.END)
            app.rectangle_add_arrow_var.set(0)
        elif mode == "cercles":
            app.cercle_rayon_entry.delete(0, tk.END)
            app.cercle_segments_entry.delete(0, tk.END)
            if hasattr(app, 'arc_start_entry'):
                app.arc_start_entry.delete(0, tk.END)
            if hasattr(app, 'arc_end_entry'):
                app.arc_end_entry.delete(0, tk.END)
        app.polygone_fill_var.set(0)
        
        # Recharger la liste des polygones
        load_polygones(app)
        messagebox.showinfo("Succès", f"Polygone '{polygone_name}' créé avec succès")
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création du polygone: {e}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur inattendue: {e}")

def load_polygones(app):
    """Charger tous les polygones depuis polygone.db"""
    for item in app.polygones_tree.get_children():
        app.polygones_tree.delete(item)
    app.checked_polygones = {}
    try:
        conn = sqlite3.connect("polygone.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, color, width, fill FROM polygons ORDER BY name")
        polygones = cursor.fetchall()
        conn.close()
        for polygone in polygones:
            item_id = app.polygones_tree.insert("", tk.END, values=("⬜", polygone[0], polygone[1], polygone[2], polygone[3]))
            app.checked_polygones[item_id] = {"checked": False}
    except sqlite3.Error:
        pass

def on_polygones_tree_double_click(viewer, event):
    """Gérer le double-clic sur le treeview pour centrer la carte sur le premier point du polygone"""
    # Identifier l'élément double-cliqué
    item = viewer.polygones_tree.identify_row(event.y)
    
    if item and item in viewer.checked_polygones:
        # Récupérer le nom du polygone
        polygone_name = viewer.polygones_tree.item(item)["values"][1]
        
        try:
            # Récupérer les coordonnées du polygone depuis polygone.db
            conn = sqlite3.connect("polygone.db")
            cursor = conn.cursor()
            cursor.execute("SELECT points_list FROM polygons WHERE name = ?", (polygone_name,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                # Récupérer le premier point du polygone
                points_str = result[0]
                coordinates_list = points_str.split()
                
                if coordinates_list:
                    # Prendre le premier point (format: "lon,lat,0")
                    first_point = coordinates_list[0].split(',')
                    if len(first_point) >= 2:
                        lon = float(first_point[0])
                        lat = float(first_point[1])
                        
                        # Vérifier qu'on a une carte chargée avant de centrer
                        if hasattr(viewer, 'mbtiles_manager') and viewer.db_path:
                            # Centrer la carte sur ce point
                            viewer.mbtiles_manager.center_map_on_point(lat, lon)
                            
                            # Optionnel : afficher un message pour confirmer l'action
                            print(f"Carte centrée sur le premier point du polygone '{polygone_name}' ({lat:.6f}, {lon:.6f})")
                        else:
                            print("Aucune carte chargée - impossible de centrer")
                    else:
                        print(f"Format de coordonnées invalide pour le polygone '{polygone_name}'")
                else:
                    print(f"Aucun point trouvé dans le polygone '{polygone_name}'")
            else:
                print(f"Polygone '{polygone_name}' non trouvé ou sans points")
                
        except Exception as e:
            print(f"Erreur lors de la récupération des coordonnées du polygone: {e}")

def refresh_on_tab_change_polygone(app):
    """Rafraîchir les données quand on change d'onglet"""
    selected_tab = app.notebook.select()
    tab_text = app.notebook.tab(selected_tab, "text")
    print(f"Tab text 2: '{tab_text}'")
    if tab_text == "  Polygones  ":
        load_points_polygone(app)
        load_polygones(app)
        # Mettre à jour les combobox de sélection de points pour rectangle et cercles
        update_point_combos(app)

def update_point_combos(app):
    """Met à jour les combobox de sélection de points pour rectangle et cercles"""
    try:
        conn = sqlite3.connect("point.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM points ORDER BY name")
        points = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Mettre à jour le combobox du rectangle si il existe
        if hasattr(app, 'rectangle_center_combo'):
            current_value = app.rectangle_center_combo.get()
            app.rectangle_center_combo['values'] = points
            if current_value in points:
                app.rectangle_center_combo.set(current_value)
            elif points:
                app.rectangle_center_combo.current(0)
        
        # Mettre à jour le combobox du cercle si il existe
        if hasattr(app, 'cercle_center_combo'):
            current_value = app.cercle_center_combo.get()
            app.cercle_center_combo['values'] = points
            if current_value in points:
                app.cercle_center_combo.set(current_value)
            elif points:
                app.cercle_center_combo.current(0)
                
    except sqlite3.Error:
        pass
