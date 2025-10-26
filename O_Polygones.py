import re
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def setup_notebook_tabs_polygone(app):
    """Configurer l'onglet Polygone"""
    polygone_frame = ttk.Frame(app.notebook)
    app.notebook.add(polygone_frame, text=" Polygones ")
    
    # Frame principal avec deux colonnes
    main_frame = tk.Frame(polygone_frame, relief=tk.GROOVE, borderwidth=2)
    main_frame.pack(fill=tk.BOTH, expand=True, pady=(5,0))
    
    # Frame gauche pour les points disponibles
    left_frame = tk.Frame(main_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tk.Label(left_frame, text="Points :", font=("Arial", 10)).pack(anchor=tk.W,padx=(5,5))
    app.points_listbox_poly = tk.Listbox(left_frame, height=8)
    app.points_listbox_poly.pack(fill=tk.BOTH, expand=True, pady=(5, 5), padx=(5,5))

    # Frame central pour les boutons
    center_frame = tk.Frame(main_frame, width=50)
    center_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
    center_frame.pack_propagate(False)
    tk.Button(center_frame, text=">>", command=lambda: add_point_to_polygone(app), width=6).pack(pady=(50, 5))
    tk.Button(center_frame, text="<<", command=lambda: remove_point_from_polygone(app), width=6).pack(pady=5)

    # Frame droite pour le polygone en cours
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
    tk.Label(right_frame, text="Polygone:", font=("Arial", 10)).pack(anchor=tk.W)
    app.polygone_points_listbox = tk.Listbox(right_frame, height=8)
    app.polygone_points_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 5), padx=(5,5))
    
    # Frame Nom polygone + Couleur + Largeur + Remplissage + Bouton créer
    name_frame = tk.Frame(polygone_frame, relief=tk.GROOVE, borderwidth=2)
    name_frame.pack(fill=tk.X, expand=False, pady=(5,0))
    tk.Label(name_frame, text="Nom du polygone : ").grid(row=0,column=0, sticky=tk.W, pady=(5,5), padx=(5,5))
    app.polygone_name_entry = tk.Entry(name_frame, width=20)
    app.polygone_name_entry.grid(row=0,column=1, pady=(5,5), padx=(5,5))
    tk.Label(name_frame, text="Couleur : ").grid(row=0,column=2, sticky=tk.W, padx=(5,5))
    app.polygone_color_entry = tk.Entry(name_frame, width=10)
    app.polygone_color_entry.grid(row=0,column=3, padx=(5,5))
    tk.Label(name_frame, text="Largeur : ").grid(row=0,column=4, sticky=tk.W, padx=(5,5))
    app.polygone_width_entry = tk.Entry(name_frame, width=5)
    app.polygone_width_entry.grid(row=0,column=5, padx=(5,5))
    tk.Label(name_frame, text="Remplir : ").grid(row=0,column=6, sticky=tk.W, padx=(5,5))
    app.polygone_fill_var = tk.IntVar()
    tk.Checkbutton(name_frame, variable=app.polygone_fill_var).grid(row=0,column=7, padx=(5,5))
    tk.Button(name_frame, text="Créer polygone", command=lambda: create_polygone(app)).grid(row=1,column=1, sticky='ew', pady=(5,5), padx=(5,5))
    
    # TreeView pour afficher les polygones existants
    tree_frame = tk.Frame(polygone_frame, relief=tk.GROOVE, borderwidth=2)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5,5))

    tk.Label(tree_frame, text="Polygones existants:", font=("Arial", 10)).pack(anchor=tk.W,pady=(4,4))

    app.polygones_tree = ttk.Treeview(tree_frame, columns=("Nom", "Color", "Width", "Fill"), show="headings", height=6)
    app.polygones_tree.heading("Nom", text="Nom")
    app.polygones_tree.heading("Color", text="Couleur")
    app.polygones_tree.heading("Width", text="Largeur")
    app.polygones_tree.heading("Fill", text="Remplir")

    app.polygones_tree.column("Nom", anchor="center", stretch=True,width=100)
    app.polygones_tree.column("Color", anchor="center", stretch=True, width=100)
    app.polygones_tree.column("Width", anchor="center", stretch=True, width=100)
    app.polygones_tree.column("Fill", anchor="center", stretch=True, width=100)
    
    scrollbar_polygones = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=app.polygones_tree.yview)
    app.polygones_tree.configure(yscrollcommand=scrollbar_polygones.set)
    
    app.polygones_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=(5,5))
    scrollbar_polygones.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Charger les données initiales
    load_points_polygone(app)
    load_polygones(app)
    
    # Bind pour rafraîchir quand l'onglet devient actif
    app.notebook.bind("<<NotebookTabChanged>>", lambda e: refresh_on_tab_change_polygone(app))

def load_points_polygone(app):
    """Charger tous les points depuis point.db"""
    app.points_listbox_poly.delete(0, tk.END)
    try:
        conn = sqlite3.connect("point.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM elements ORDER BY name")
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
    
    # Récupérer les points du polygone
    points_list = [app.polygone_points_listbox.get(i) for i in range(app.polygone_points_listbox.size())]
    if len(points_list) < 3:
        messagebox.showerror("Erreur", "Un polygone doit contenir au moins 3 points")
        return
    try:
        conn = sqlite3.connect("polygone.db")
        cursor = conn.cursor()
        # Vérifier si le nom existe déjà
        cursor.execute("SELECT name FROM elements WHERE name = ?", (polygone_name,))
        if cursor.fetchone():
            messagebox.showerror("Erreur", "Un polygone avec ce nom existe déjà")
            conn.close()
            return
        # Insérer le nouveau polygone
        points_str = ",".join(points_list)
        cursor.execute("INSERT INTO elements (name, color, width, fill, points_list) VALUES (?, ?, ?, ?, ?)",
                      (polygone_name, color, int(width), int(fill), points_str))
        conn.commit()
        conn.close()
        # Réinitialiser l'interface
        app.polygone_name_entry.delete(0, tk.END)
        app.polygone_color_entry.delete(0, tk.END)
        app.polygone_width_entry.delete(0, tk.END)
        app.polygone_points_listbox.delete(0, tk.END)
        app.polygone_fill_var.set(0)
        # Recharger la liste des polygones
        load_polygones(app)
        messagebox.showinfo("Succès", f"Polygone '{polygone_name}' créé avec succès")
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création du polygone: {e}")

def load_polygones(app):
    """Charger tous les polygones depuis polygone.db"""
    for item in app.polygones_tree.get_children():
        app.polygones_tree.delete(item)
    try:
        conn = sqlite3.connect("polygone.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, color, width, fill FROM elements ORDER BY name")
        polygones = cursor.fetchall()
        conn.close()
        for polygone in polygones:
            app.polygones_tree.insert("", tk.END, values=(polygone[0], polygone[1], polygone[2], polygone[3]))
    except sqlite3.Error:
        pass

def refresh_on_tab_change_polygone(app):
    """Rafraîchir les données quand on change d'onglet"""
    selected_tab = app.notebook.select()
    tab_text = app.notebook.tab(selected_tab, "text")
    if tab_text == " Polygones ":
        load_points_polygone(app)
        load_polygones(app)
