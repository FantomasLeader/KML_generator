import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random

class DataManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestionnaire de Points")
        self.root.geometry("800x600")
        
        self.db_path = "points.db"
        self.init_database()
        self.create_random_points()
        
        self.setup_ui()
        self.load_data()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                format TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS export_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                format TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    
    def create_random_points(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM points")
        if cursor.fetchone()[0] == 0:
            formats = ["KML", "GPX", "GeoJSON"]
            for i in range(2):
                nom = f"Point_{i+1}"
                format_type = random.choice(formats)
                lat = round(random.uniform(44.0, 45.0), 6)
                lon = round(random.uniform(-2.0, -1.0), 6)
                cursor.execute("INSERT INTO points (nom, format, latitude, longitude) VALUES (?, ?, ?, ?)",
                             (nom, format_type, lat, lon))
            conn.commit()
        conn.close()
    
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tableau des points avec cases à cocher
        self.tree = ttk.Treeview(main_frame, columns=("selected", "nom", "format", "latitude", "longitude"), show="headings", selectmode="extended")
        self.tree.heading("selected", text="")
        self.tree.heading("nom", text="Nom")
        self.tree.heading("format", text="Format")
        self.tree.heading("latitude", text="Latitude")
        self.tree.heading("longitude", text="Longitude")
        
        self.tree.column("selected", width=40, anchor="center")
        self.tree.column("nom", width=150)
        self.tree.column("format", width=100)
        self.tree.column("latitude", width=120)
        self.tree.column("longitude", width=120)
        
        # Dictionnaire pour suivre l'état des cases à cocher
        self.checked_items = {}
        
        # Bind du clic sur les cases à cocher
        self.tree.bind("<Button-1>", self.on_tree_click)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame pour les boutons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(button_frame, text="Supprimer", command=self.delete_points).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Ajouter", command=self.add_point_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Exporter sélection", command=self.export_selection).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Voir exports", command=self.view_exports).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Tout sélectionner", command=self.select_all).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Tout désélectionner", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
    
    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.checked_items = {}
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, format, latitude, longitude FROM points")
        for row in cursor.fetchall():
            item_id = self.tree.insert("", tk.END, values=("⬜", row[1], row[2], row[3], row[4]))
            self.checked_items[item_id] = {"checked": False, "data": row}
        conn.close()
    
    def delete_points(self):
        checked_items = [item for item, data in self.checked_items.items() if data["checked"]]
        if not checked_items:
            messagebox.showwarning("Attention", "Sélectionnez des points à supprimer")
            return
        
        if messagebox.askyesno("Confirmation", f"Supprimer {len(checked_items)} point(s) ?"):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            for item in checked_items:
                point_id = self.checked_items[item]["data"][0]
                cursor.execute("DELETE FROM points WHERE id = ?", (point_id,))
            conn.commit()
            conn.close()
            self.load_data()
    
    def add_point_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter un point")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Nom:").pack(pady=5)
        nom_entry = tk.Entry(dialog)
        nom_entry.pack(pady=5)
        
        tk.Label(dialog, text="Format:").pack(pady=5)
        format_var = tk.StringVar(value="KML")
        format_combo = ttk.Combobox(dialog, textvariable=format_var, values=["KML", "GPX", "GeoJSON"])
        format_combo.pack(pady=5)
        
        tk.Label(dialog, text="Latitude:").pack(pady=5)
        lat_entry = tk.Entry(dialog)
        lat_entry.pack(pady=5)
        
        tk.Label(dialog, text="Longitude:").pack(pady=5)
        lon_entry = tk.Entry(dialog)
        lon_entry.pack(pady=5)
        
        def save_point():
            try:
                nom = nom_entry.get().strip()
                format_type = format_var.get()
                lat = float(lat_entry.get())
                lon = float(lon_entry.get())
                
                if not nom:
                    messagebox.showerror("Erreur", "Le nom est requis")
                    return
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO points (nom, format, latitude, longitude) VALUES (?, ?, ?, ?)",
                             (nom, format_type, lat, lon))
                conn.commit()
                conn.close()
                
                self.load_data()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Coordonnées invalides")
        
        tk.Button(dialog, text="Sauvegarder", command=save_point).pack(pady=10)
    
    def export_selection(self):
        checked_items = [item for item, data in self.checked_items.items() if data["checked"]]
        if not checked_items:
            messagebox.showwarning("Attention", "Sélectionnez des points à exporter")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM export_points")
        
        for item in checked_items:
            data = self.checked_items[item]["data"]
            cursor.execute("INSERT INTO export_points (nom, format, latitude, longitude) VALUES (?, ?, ?, ?)",
                         (data[1], data[2], data[3], data[4]))
        
        conn.commit()
        conn.close()
        messagebox.showinfo("Succès", f"{len(checked_items)} point(s) exporté(s)")
    
    def view_exports(self):
        export_window = tk.Toplevel(self.root)
        export_window.title("Points exportés")
        export_window.geometry("600x400")
        
        export_tree = ttk.Treeview(export_window, columns=("nom", "format", "latitude", "longitude"), show="headings")
        export_tree.heading("nom", text="Nom")
        export_tree.heading("format", text="Format")
        export_tree.heading("latitude", text="Latitude")
        export_tree.heading("longitude", text="Longitude")
        export_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT nom, format, latitude, longitude FROM export_points")
        for row in cursor.fetchall():
            export_tree.insert("", tk.END, values=row)
        conn.close()
    
    def on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.tree.identify_row(event.y)
            column = self.tree.identify_column(event.x)
            
            if column == "#1" and item in self.checked_items:  # Colonne des cases à cocher
                self.toggle_checkbox(item)
    
    def toggle_checkbox(self, item):
        current_state = self.checked_items[item]["checked"]
        new_state = not current_state
        self.checked_items[item]["checked"] = new_state
        
        # Mettre à jour l'affichage
        values = list(self.tree.item(item)["values"])
        values[0] = "✅" if new_state else "⬜"
        self.tree.item(item, values=values)
    
    def select_all(self):
        for item in self.checked_items:
            self.checked_items[item]["checked"] = True
            values = list(self.tree.item(item)["values"])
            values[0] = "✅"
            self.tree.item(item, values=values)
    
    def deselect_all(self):
        for item in self.checked_items:
            self.checked_items[item]["checked"] = False
            values = list(self.tree.item(item)["values"])
            values[0] = "⬜"
            self.tree.item(item, values=values)

def main():
    root = tk.Tk()
    app = DataManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()