import sqlite3
import tkinter as tk
import os

class DatabaseUI:
    
    def __init__(self, root):        
        self.root = root
        self.root.title("Database UI")
        self.root.geometry("400x300")
        
        self.db_name = 'my_database.db'
        self.initialize_database(self.db_name)

        label_info = tk.Label(self.root, text=f"Database {self.db_name} initialisée", font=("Arial", 10))
        label_info.pack(anchor=tk.NW, pady=5, padx=5)

        label_table= tk.Label(self.root, text="Nom des Tables:", font=("Arial", 10))
        label_table.pack(anchor=tk.NW, pady=5, padx=5)

        self.listbox_tables = tk.Listbox(self.root, width=20, height=5)
        self.listbox_tables.pack(anchor=tk.NW, pady=10, padx=5)

        button_rename = tk.Button(self.root, text="TEST", command=lambda: self.test_table())
        button_rename.pack(anchor=tk.NW, pady=5, padx=5)

        self.init_listbox_tables()

    def test_table(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor.execute("PRAGMA foreign_keys = ON")

            cursor = conn.cursor()
            
            # Create Test table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Test (
                TestId INTEGER ,
                TestName NVARCHAR(100),
                PRIMARY KEY (TestId AUTOINCREMENT)
                )
            ''')

            # Liste des types de données possibles dans SQLite:
            # TEXT, NUMERIC, INTEGER, REAL, BLOB
            
            # Liste des contraintes possibles dans SQLite:
            # NOT NULL, PRIMARY KEY, AUTOINCREMENT, UNIQUE, DEFAULT, CHECK, FOREIGN KEY 

            # Liste des mot-cles pour les requêtes:
            # SELECT, FROM, WHERE, GROUP BY, ORDER BY, LIMIT

            # Add a new column to Test table
            table_name="Test"
            column_name="Description"
            column_type="NVARCHAR(255)"
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            
            # Rename Test table
            new_name = "Renamed"
            cursor.execute(f"ALTER TABLE {table_name} RENAME TO {new_name}")

            #Ajouter des données dans la table Renamed
            cursor.execute(f"INSERT INTO {new_name} (TestName, Description) VALUES (?, ?)", ("Sample Test", "This is a sample description"))    

            #Ajouter les donnees par defaut dans la table Department
            cursor.execute(f"INSERT INTO {new_name} DEFAULT VALUES")
            
            # Suppression de la table Marks
            cursor.execute("DROP TABLE IF EXISTS Marks")

            conn.commit()
            conn.close()
            
            self.init_listbox_tables()

        except Exception as e:
            print(f"Erreur lors de des tests: {e}")
            
    

    def init_listbox_tables(self):
        # Charger les noms de tables depuis la base de données
        try:
            self.listbox_tables.delete(0, tk.END)
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite%'")
            tables = cursor.fetchall()
            conn.close()
            for table in tables:
                self.listbox_tables.insert(tk.END, table[0])
        except Exception as e:
            self.listbox_tables.insert(tk.END, f"Erreur: {e}")

    def initialize_database(self, db_name):
        """Initializes the SQLite database with a users table."""
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        # Create Department table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Department (
                DepartmentId INTEGER PRIMARY KEY AUTOINCREMENT,
                DepartmentName NVARCHAR(100) NOT NULL
            )
        ''')
        # Create Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Students (
                StudentId INTEGER PRIMARY KEY NOT NULL,
                StudentName NVARCHAR(50) NOT NULL,
                DepartmentId INTEGER NULL,
                DateOfBirth DATE NULL,
                FOREIGN KEY (DepartmentId) REFERENCES Department (DepartmentId)
            )
        ''')
        # Create Marks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Marks (
                StudentId INTEGER NOT NULL,
                SubjectId INTEGER NOT NULL,
                Mark INTEGER NULL
            )
        ''')
        # Create Subjects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Subjects (
                SubjectId INTEGER NOT NULL PRIMARY KEY,
                SubjectName NVARCHAR(50) NOT NULL
            )
        ''')
        
        # Test de la FOREIGN KEY
        cursor.execute("INSERT INTO Department VALUES (1, 'IT')")
        cursor.execute("INSERT INTO Department VALUES (2, 'Arts')")
        cursor.execute("SELECT * FROM Department")
        rows = cursor.fetchall()
        for row in rows:
            print(row)

        try:
            cursor.execute("INSERT INTO Students (StudentName, DepartmentId) VALUES ('Alice',5)")
        except sqlite3.IntegrityError:
            print("Erreur d'intégrité : La clé étrangère n'existe pas.")
        
        conn.commit()
        conn.close()

def main():
    root = tk.Tk()
    app = DatabaseUI(root)

    def on_closing():
        root.destroy()
        if os.path.exists(app.db_name):
            try:
                os.remove(app.db_name)
                print(f"Base de données '{app.db_name}' supprimée.")
            except Exception as e:
                print(f"Erreur lors de la suppression de la base de données : {e}")

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()