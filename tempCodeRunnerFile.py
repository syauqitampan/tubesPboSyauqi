
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"ERROR [database.py] Query gagal: {e} | Query: {query[:60]}")
        conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def fetch_query(query: str, params: tuple = None, fetch_all: bool = True):
    """Menjalankan query SELECT dan mengembalikan hasil."""
    conn = get_db_connection()
    if not conn:
        return None