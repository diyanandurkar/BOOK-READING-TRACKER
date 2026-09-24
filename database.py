import sqlite3

DATABASE = "database.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            total_pages INTEGER,
            pages_read INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Want to Read',
            rating REAL,
            start_date TEXT,
            finish_date TEXT,
            notes TEXT
        )
    """)

    connection.commit()
    connection.close()


def add_sample_books():
    connection = get_db_connection()

    books = [
        (
            "Atomic Habits",
            "James Clear",
            "Self Help",
            320,
            240,
            "Currently Reading",
            4.5,
            "2026-09-01",
            None,
            "Small habits can create big changes."
        ),
        (
            "The Psychology of Money",
            "Morgan Housel",
            "Finance",
            260,
            120,
            "Currently Reading",
            4.2,
            "2026-09-10",
            None,
            "Interesting lessons about money."
        ),
        (
            "The Alchemist",
            "Paulo Coelho",
            "Fiction",
            208,
            208,
            "Completed",
            4.8,
            "2026-08-01",
            "2026-08-15",
            "A very inspiring book."
        )
    ]

    connection.executemany("""
        INSERT INTO books (
            title,
            author,
            genre,
            total_pages,
            pages_read,
            status,
            rating,
            start_date,
            finish_date,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, books)


    connection.commit()
    connection.close()


# Run these functions
create_table()
def add_cover_column():

    connection = get_db_connection()

    try:

        connection.execute(
            "ALTER TABLE books ADD COLUMN cover_url TEXT"
        )

        connection.commit()

    except sqlite3.OperationalError:

        # Column already exists
        pass

    connection.close()
add_sample_books()