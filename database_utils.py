import sqlite3
import contextlib

@contextlib.contextmanager
def get_db_connection(db_name):
    """Context manager pour les connexions SQLite qui garantit la fermeture"""
    conn = None
    try:
        conn = sqlite3.connect(db_name, timeout=10.0)  # Timeout de 10 secondes
        yield conn
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def execute_db_query(db_name, query, params=None, fetch_all=False, fetch_one=False):
    """Exécute une requête SQLite de manière sécurisée"""
    try:
        with get_db_connection(db_name) as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch_all:
                return cursor.fetchall()
            elif fetch_one:
                return cursor.fetchone()
            else:
                conn.commit()
                return cursor.rowcount
    except sqlite3.Error as e:
        print(f"Erreur base de données: {e}")
        raise

def close_all_connections():
    """Force la fermeture de toutes les connexions SQLite potentiellement ouvertes"""
    import gc
    gc.collect()  # Force le garbage collection pour fermer les connexions non fermées