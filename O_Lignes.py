import re
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def setup_notebook_tabs(app):
    """Configurer l'onglet Ligne"""
    ligne_frame = ttk.Frame(app.notebook)
    app.notebook.add(ligne_frame, text="  Lignes  ")
    
    # Frame principal avec deux colonnes
    main_frame = tk.Frame(ligne_frame, relief=tk.GROOVE, borderwidth=2)
    main_frame.pack(fill=tk.BOTH, expand=True, pady=(5,0))
    
    # Frame gauche pour les points disponibles
    left_frame = tk.Frame(main_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tk.Label(left_frame, text="Points :", font=("Arial", 10)).pack(anchor=tk.W,padx=(5,5))
    app.points_listbox = tk.Listbox(left_frame, height=8)
    app.points_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 5), padx=(5,5))

    # Frame central pour les boutons
    center_frame = tk.Frame(main_frame, width=50)
    center_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
    center_frame.pack_propagate(False)
    tk.Button(center_frame, text=">>", command=lambda: add_point_to_line(app), width=6).pack(pady=(50, 5))
    tk.Button(center_frame, text="<<", command=lambda: remove_point_from_line(app), width=6).pack(pady=5)

    # Frame droite pour la ligne en cours
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
    tk.Label(right_frame, text="Ligne:", font=("Arial", 10)).pack(anchor=tk.W)
    app.line_points_listbox = tk.Listbox(right_frame, height=8)
    app.line_points_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 5), padx=(5,5))
    
    # Frame Nom ligne + Bouton créer (hauteur fixe, pas d'expansion)
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

    # TreeView pour afficher les lignes existantes
    tree_frame = tk.Frame(ligne_frame, relief=tk.GROOVE, borderwidth=2)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5,5))

    tk.Label(tree_frame, text="Lignes existantes:", font=("Arial", 10)).pack(anchor=tk.W,pady=(4,4))

    app.lines_tree = ttk.Treeview(tree_frame, columns=("Nom", "Color", "Width"), show="headings", height=6)
    app.lines_tree.heading("Nom", text="Nom")
    app.lines_tree.heading("Color", text="Couleur")
    app.lines_tree.heading("Width", text="Largeur")

    # Colonnes stretch pour ajustement automatique
    app.lines_tree.column("Nom", anchor="center", stretch=True,width=100)
    app.lines_tree.column("Color", anchor="center", stretch=True, width=100)
    app.lines_tree.column("Width", anchor="center", stretch=True, width=100)
    
    scrollbar_lines = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=app.lines_tree.yview)
    app.lines_tree.configure(yscrollcommand=scrollbar_lines.set)
    
    app.lines_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=(5,5))
    scrollbar_lines.pack(side=tk.RIGHT, fill=tk.Y)
    
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
        cursor.execute("SELECT name FROM elements ORDER BY name")
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
    
    # Récupérer les points de la ligne
    points_list = [app.line_points_listbox.get(i) for i in range(app.line_points_listbox.size())]
    if len(points_list) < 2:
        messagebox.showerror("Erreur", "Une ligne doit contenir au moins 2 points")
        return
    
    try:
        conn = sqlite3.connect("ligne.db")
        cursor = conn.cursor()
        
        # Vérifier si le nom existe déjà
        cursor.execute("SELECT name FROM elements WHERE name = ?", (line_name,))
        if cursor.fetchone():
            messagebox.showerror("Erreur", "Une ligne avec ce nom existe déjà")
            conn.close()
            return
        
        # Insérer la nouvelle ligne
        points_str = ",".join(points_list)
        cursor.execute("INSERT INTO elements (name, color, width, points_list) VALUES (?, ?, ?, ?)",
                      (line_name, "rouge", 2, points_str))
        conn.commit()
        conn.close()
        
        # Réinitialiser l'interface
        app.line_name_entry.delete(0, tk.END)
        app.line_points_listbox.delete(0, tk.END)
        
        # Recharger la liste des lignes
        load_lines(app)
        
        messagebox.showinfo("Succès", f"Ligne '{line_name}' créée avec succès")
        
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création de la ligne: {e}")

def load_lines(app):
    """Charger toutes les lignes depuis ligne.db"""
    for item in app.lines_tree.get_children():
        app.lines_tree.delete(item)
    try:
        conn = sqlite3.connect("ligne.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, color, width FROM elements ORDER BY name")
        lines = cursor.fetchall()
        conn.close()
        for line in lines:
            app.lines_tree.insert("", tk.END, values=(line[0], line[1], line[2]))
    except sqlite3.Error:
        pass

def refresh_on_tab_change(app):
    """Rafraîchir les données quand on change d'onglet"""
    selected_tab = app.notebook.select()
    tab_text = app.notebook.tab(selected_tab, "text")
    
    if tab_text == "  Lignes  ":
        load_points(app)
        load_lines(app)