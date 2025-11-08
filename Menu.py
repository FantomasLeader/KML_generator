import tkinter as tk
from tkinter import Menu

class MenuBar:
    def __init__(self, master, import_raster_callback=None, export_kml_callback=None, import_kml_callback=None, fermer_carte_callback=None):
        self.master = master
        self.menu_bar = Menu(master)
        self._create_menus(import_raster_callback, export_kml_callback, import_kml_callback, fermer_carte_callback)
        master.config(menu=self.menu_bar)

    def _create_menus(self, import_raster_callback, export_kml_callback, import_kml_callback, fermer_carte_callback):
        # Fichiers menu
        fichiers_menu = Menu(self.menu_bar, tearoff=0)
        fichiers_menu.add_command(label="  Importer Raster  ", command=import_raster_callback)
        fichiers_menu.add_separator()
        fichiers_menu.add_command(label="  Fermer Carte  ", command=fermer_carte_callback)
        fichiers_menu.add_separator()
        fichiers_menu.add_command(label="  Exporter kml  ", command=export_kml_callback)
        fichiers_menu.add_command(label="  Importer kml  ", command=import_kml_callback)
        self.menu_bar.add_cascade(label="Fichiers", menu=fichiers_menu)

        # Infos menu
        infos_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Infos", menu=infos_menu)

# Exemple d'utilisation:
if __name__ == "__main__":
    def importer_raster():
        print("Importer Raster sélectionné")

    def exporter_kml():
        print("Exporter kml sélectionné")
    
    def importer_kml():
        print("Importer kml sélectionné")

    root = tk.Tk()
    root.title("Exemple Menu")
    menu = MenuBar(root, importer_raster, exporter_kml, importer_kml)
    root.mainloop()
