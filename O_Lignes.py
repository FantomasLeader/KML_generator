import re
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def setup_notebook_tabs(app):
    """Appellé depuis main.py créé l'onglet Ligne"""
    
    # Création de l'onglet Ligne dans "ligne_frame"
    ligne_frame = ttk.Frame(app.notebook)
    app.notebook.add(ligne_frame, text="  Lignes  ")

    # Création d'un Frame "main_frame" pour afficher : Liste de points - Boutons - Points de la ligne
    main_frame = tk.Frame(ligne_frame, relief=tk.GROOVE, borderwidth=2)
    main_frame.pack(fill=tk.BOTH, pady=(5,0))
    
    left_frame = tk.Frame(main_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tk.Label(left_frame, text="Points :", font=("Arial", 10)).pack(anchor=tk.W,padx=(5,5))
    app.points_listbox = tk.Listbox(left_frame, height=8)
    app.points_listbox.pack(fill=tk.BOTH, expand=False, pady=(5, 5), padx=(5,5))
    
    center_frame = tk.Frame(main_frame, width=50)
    center_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
    center_frame.pack_propagate(False)
    tk.Button(center_frame, text=">>", command=lambda: add_point_to_line(app), width=6).pack(pady=(50,20))
    tk.Button(center_frame, text="<<", command=lambda: remove_point_from_line(app), width=6).pack(pady=5)

    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
    tk.Label(right_frame, text="Ligne:", font=("Arial", 10)).pack(anchor=tk.W,padx=(5,5))
    app.line_points_listbox = tk.Listbox(right_frame, height=8)
    app.line_points_listbox.pack(fill=tk.BOTH, expand=False, pady=(5, 5), padx=(5,5))

    # Création d'un Frame "name_frame" pour les attributs de la ligne et le bouton créer
    name_frame = tk.Frame(ligne_frame, relief=tk.GROOVE, borderwidth=2)
    name_frame.pack(fill=tk.X, expand=False, pady=(5,0))

    tk.Label(name_frame, text="Nom de la ligne : ").grid(row=0,column=0, sticky=tk.W, pady=(5,5), padx=(5,5))
    app.line_name_entry = tk.Entry(name_frame,width=15)
    app.line_name_entry.grid(row=0,column=1, pady=(5,5), padx=(5,5),sticky="ew")
    
    tk.Label(name_frame, text="Epaisseur de la ligne : ").grid(row=1,column=0, sticky=tk.W, pady=(5,5), padx=(5,5))
    app.line_width_entry = ttk.Combobox(name_frame, values=[str(i) for i in range(1, 11)], state="readonly",width=15,justify="center")
    app.line_width_entry.current(1)
    app.line_width_entry.grid(row=1,column=1, pady=(5,5), padx=(5,5),sticky="ew")

    tk.Label(name_frame, text="Couleur de la ligne : ").grid(row=2,column=0, sticky=tk.W, pady=(5,5), padx=(5,5))
    colors = ["rouge", "vert", "bleu", "jaune", "orange", "cyan", "magenta", "noir", "blanc"]
    app.line_color_entry = ttk.Combobox(name_frame, values=colors, state="readonly",width=15,justify="center")
    app.line_color_entry.current(0)
    app.line_color_entry.grid(row=2,column=1, pady=(5,5), padx=(5,5),sticky="ew")

    tk.Button(name_frame, text=" Créer ligne ", command=lambda: create_line(app)).grid(row=3,column=1, sticky='ew', pady=(5,5), padx=(5,5))

    # Création d'un frame "tree_frame" pour afficher le TreeView et ses boutons
    app.tree_frame = tk.Frame(ligne_frame, relief=tk.GROOVE, borderwidth=2)
    app.tree_frame.pack(fill=tk.X, padx=5, pady=5)

    tk.Label(app.tree_frame, text="Lignes existantes:", font=("Arial", 10)).pack(anchor=tk.W,pady=(4,4))

    app.lines_tree = ttk.Treeview(app.tree_frame, columns=("selected", "Nom", "Color", "Width"), show="headings", height=8)
    app.lines_tree.heading("selected", text="Export")
    app.lines_tree.heading("Nom", text="Nom")
    app.lines_tree.heading("Color", text="Couleur")
    app.lines_tree.heading("Width", text="Largeur")

    app.lines_tree.column("selected", width=50, anchor="center")
    app.lines_tree.column("Nom", anchor="center", width=60)
    app.lines_tree.column("Color", anchor="center",  width=60)
    app.lines_tree.column("Width", anchor="center",  width=60)

    scrollbar_lines = ttk.Scrollbar(app.tree_frame, orient=tk.VERTICAL, command=app.lines_tree.yview)
    app.lines_tree.configure(yscrollcommand=scrollbar_lines.set)

    app.lines_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    scrollbar_lines.pack(side=tk.RIGHT, fill=tk.Y)

    btn_select_all = ttk.Button(app.tree_frame, text="Sélectionner tout", width=15, command=lambda: select_all_lines_treeview(app))
    btn_select_all.pack(side=tk.LEFT, padx=5)
    btn_deselect_all = ttk.Button(app.tree_frame, text="Désélectionner tout", command=lambda: deselect_all_lines_treeview(app))
    btn_deselect_all.pack(side=tk.LEFT, padx=5)
    btn_delete = ttk.Button(app.tree_frame, text="Supprimer", command=lambda: delete_selected_lines(app))
    btn_delete.pack(side=tk.LEFT, padx=5)
    
    app.checked_lines = {}
    app.lines_tree.bind("<Button-1>", lambda event: on_lines_tree_click(app, event))
    app.lines_tree.bind("<Double-1>", lambda event: on_lines_tree_double_click(app, event))

    # Charger les données initiales
    load_points(app)
    load_lines(app)

    # Bind pour rafraîchir quand l'onglet devient actif
    app.notebook.bind("<<NotebookTabChanged>>", lambda e: refresh_on_tab_change(app))

def load_points(app):
    """Charger tous les points depuis point.db"""
    app.points_listbox.delete(0, tk.END)
    try:
        conn = sqlite3.connect("point.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM points ORDER BY name")
        points = cursor.fetchall()
        conn.close()
        
        for point in points:
            app.points_listbox.insert(tk.END, point[0])
    except sqlite3.Error:
        pass

def add_point_to_line(app):
    """Ajouter un point sélectionné à la ligne"""
    selection = app.points_listbox.curselection()
    if selection:
        point_name = app.points_listbox.get(selection[0])
        app.line_points_listbox.insert(tk.END, point_name)

def remove_point_from_line(app):
    """Retirer un point sélectionné de la ligne"""
    selection = app.line_points_listbox.curselection()
    if selection:
        app.line_points_listbox.delete(selection[0])

def create_line(app):
    """Créer une nouvelle ligne et l'enregistrer dans ligne.db"""
    line_name = app.line_name_entry.get().strip()
    if not line_name:
        messagebox.showerror("Erreur", "Veuillez entrer un nom pour la ligne")
        return
    
    # Récupérer les noms des points de la ligne
    point_names = [app.line_points_listbox.get(i) for i in range(app.line_points_listbox.size())]
    if len(point_names) < 2:
        messagebox.showerror("Erreur", "Une ligne doit contenir au moins 2 points")
        return
    
    try:
        # Récupérer les coordonnées des points depuis point.db
        conn_points = sqlite3.connect("point.db")
        cursor_points = conn_points.cursor()
        
        coordinates_list = []
        for point_name in point_names:
            cursor_points.execute("SELECT lat, lon FROM points WHERE name = ?", (point_name,))
            result = cursor_points.fetchone()
            if result:
                lat, lon = result
                # Stocker les coordonnées au format "lat,lon,0" (z=0 par défaut)
                coordinates_list.append(f"{lon},{lat},0")
            else:
                messagebox.showerror("Erreur", f"Point '{point_name}' introuvable dans la base de données")
                conn_points.close()
                return
        
        conn_points.close()
        
        conn = sqlite3.connect("ligne.db")
        cursor = conn.cursor()

        # Vérifier si le nom existe déjà
        cursor.execute("SELECT name FROM lines WHERE name = ?", (line_name,))
        if cursor.fetchone():
            messagebox.showerror("Erreur", "Une ligne avec ce nom existe déjà")
            conn.close()
            return

        # Insérer la nouvelle ligne avec les coordonnées
        points_str = " ".join(coordinates_list)
        line_color = app.line_color_entry.get()
        line_width = int(app.line_width_entry.get())
        cursor.execute("INSERT INTO lines (name, color, width, points_list) VALUES (?, ?, ?, ?)",
                      (line_name, line_color, line_width, points_str))
        conn.commit()
        conn.close()

        # Réinitialiser l'interface
        app.line_name_entry.delete(0, tk.END)
        app.line_points_listbox.delete(0, tk.END)

        # Recharger la liste des lignes
        load_lines(app)

        messagebox.showinfo("Succès", f"Ligne '{line_name}' créée avec succès")

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création de la ligne: {e}")

def load_lines(app):
    """Charger toutes les lignes depuis ligne.db"""
    for item in app.lines_tree.get_children():
        app.lines_tree.delete(item)
        app.checked_lines = {}
    try:
        conn = sqlite3.connect("ligne.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, color, width FROM lines ORDER BY name")
        lines = cursor.fetchall()
        conn.close()
        for line in lines:
            item_id = app.lines_tree.insert("", tk.END, values=("⬜", line[0], line[1], line[2]))
            app.checked_lines[item_id] = {"checked": False, "data": line}
    except sqlite3.Error:
        pass

def refresh_on_tab_change(app):
    """Rafraîchir les données quand on change d'onglet"""
    selected_tab = app.notebook.select()
    tab_text = app.notebook.tab(selected_tab, "text")
    
    if tab_text == "  Lignes  ":
        load_points(app)
        load_lines(app)

# Fonctions similaires à O_Points pour gérer les cases à cocher et les boutons
def on_lines_tree_click(app, event):
    region = app.lines_tree.identify_region(event.x, event.y)
    if region == "cell":
        item = app.lines_tree.identify_row(event.y)
        column = app.lines_tree.identify_column(event.x)
        if column == "#1" and item in app.checked_lines:
            toggle_lines_checkbox(app, item)

def on_lines_tree_double_click(app, event):
    """Gérer le double-clic sur le treeview pour centrer la carte sur le premier point de la ligne"""
    # Identifier l'élément double-cliqué
    item = app.lines_tree.identify_row(event.y)
    
    if item and item in app.checked_lines:
        # Récupérer le nom de la ligne
        line_name = app.lines_tree.item(item)["values"][1]
        
        try:
            # Récupérer les coordonnées de la ligne depuis ligne.db
            conn = sqlite3.connect("ligne.db")
            cursor = conn.cursor()
            cursor.execute("SELECT points_list FROM lines WHERE name = ?", (line_name,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                # Récupérer le premier point de la ligne
                points_str = result[0]
                coordinates_list = points_str.split()
                
                if coordinates_list:
                    # Prendre le premier point (format: "lon,lat,0")
                    first_point = coordinates_list[0].split(',')
                    if len(first_point) >= 2:
                        lon = float(first_point[0])
                        lat = float(first_point[1])
                        
                        # Vérifier qu'on a une carte chargée avant de centrer
                        if hasattr(app, 'mbtiles_manager') and app.db_path:
                            # Centrer la carte sur ce point
                            app.mbtiles_manager.center_map_on_point(lat, lon)
                            
                            # Optionnel : afficher un message pour confirmer l'action
                            print(f"Carte centrée sur le premier point de la ligne '{line_name}' ({lat:.6f}, {lon:.6f})")
                        else:
                            print("Aucune carte chargée - impossible de centrer")
                    else:
                        print(f"Format de coordonnées invalide pour la ligne '{line_name}'")
                else:
                    print(f"Aucun point trouvé dans la ligne '{line_name}'")
            else:
                print(f"Ligne '{line_name}' non trouvée ou sans points")
                
        except Exception as e:
            print(f"Erreur lors de la récupération des coordonnées de la ligne: {e}")

def toggle_lines_checkbox(app, item):
    current_state = app.checked_lines[item]["checked"]
    new_state = not current_state
    app.checked_lines[item]["checked"] = new_state
    values = list(app.lines_tree.item(item)["values"])
    values[0] = "✅" if new_state else "⬜"
    app.lines_tree.item(item, values=values)

def select_all_lines_treeview(app):
    for item in app.checked_lines:
        app.checked_lines[item]["checked"] = True
        values = list(app.lines_tree.item(item)["values"])
        values[0] = "✅"
        app.lines_tree.item(item, values=values)

def deselect_all_lines_treeview(app):
    for item in app.checked_lines:
        app.checked_lines[item]["checked"] = False
        values = list(app.lines_tree.item(item)["values"])
        values[0] = "⬜"
        app.lines_tree.item(item, values=values)

def delete_selected_lines(app):
    to_delete = [item for item, info in app.checked_lines.items() if info["checked"]]
    if not to_delete:
        messagebox.showwarning("Suppression", "Aucune ligne sélectionnée.")
        return
    conn = sqlite3.connect("ligne.db")
    cursor = conn.cursor()
    for item in to_delete:
        name = app.lines_tree.item(item)["values"][1]
        cursor.execute("DELETE FROM lines WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    load_lines(app)
    messagebox.showinfo("Suppression", f"{len(to_delete)} ligne(s) supprimée(s).")