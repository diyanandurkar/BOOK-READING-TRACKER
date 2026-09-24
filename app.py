
from flask import Flask, render_template, request, redirect, url_for
from database import create_table, get_db_connection

app = Flask(__name__)


# Create database table
create_table()


# ---------------- HOME ----------------

@app.route("/")
def home():

    connection = get_db_connection()

    # Get all books
    books = connection.execute(
        "SELECT * FROM books"
    ).fetchall()

    # Total books
    total_books = connection.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    # Completed books
    completed_books = connection.execute(
        "SELECT COUNT(*) FROM books WHERE status = 'Completed'"
    ).fetchone()[0]

    # Currently reading
    currently_reading = connection.execute(
        "SELECT COUNT(*) FROM books WHERE status = 'Currently Reading'"
    ).fetchone()[0]

    # Total pages read
    pages_read = connection.execute(
        "SELECT SUM(pages_read) FROM books"
    ).fetchone()[0]

    connection.close()

    # If there are no books
    if pages_read is None:
        pages_read = 0

    return render_template(
        "index.html",
        books=books,
        total_books=total_books,
        completed_books=completed_books,
        currently_reading=currently_reading,
        pages_read=pages_read
    )


# ---------------- ADD BOOK ----------------

@app.route("/add-book", methods=["GET", "POST"])
def add_book():

    if request.method == "POST":

        title = request.form["title"]
        author = request.form["author"]
        genre = request.form["genre"]
        total_pages = request.form["total_pages"]
        pages_read = request.form["pages_read"]
        status = request.form["status"]
        rating = request.form["rating"]
        start_date = request.form["start_date"]
        notes = request.form["notes"]

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO books (
                title,
                author,
                genre,
                total_pages,
                pages_read,
                status,
                rating,
                start_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                author,
                genre,
                total_pages,
                pages_read,
                status,
                rating if rating else None,
                start_date,
                notes
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("home"))

    return render_template("add_book.html")


# ---------------- BOOKS ----------------

@app.route("/books")
def books():

    search = request.args.get("search", "")
    status = request.args.get("status", "")

    connection = get_db_connection()

    query = "SELECT * FROM books WHERE 1=1"
    parameters = []

    # Search
    if search:

        query += """
            AND (
                title LIKE ?
                OR author LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.append(search_value)
        parameters.append(search_value)

    # Status filter
    if status:

        query += " AND status = ?"
        parameters.append(status)

    query += " ORDER BY id DESC"

    books = connection.execute(
        query,
        parameters
    ).fetchall()

    connection.close()

    return render_template(
        "books.html",
        books=books,
        search=search,
        status=status
    )


# ---------------- BOOK DETAILS ----------------

@app.route("/book/<int:book_id>")
def book_details(book_id):

    connection = get_db_connection()

    book = connection.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    connection.close()

    if book is None:
        return "Book not found", 404

    return render_template(
        "book_details.html",
        book=book
    )


# ---------------- EDIT BOOK ----------------

@app.route("/edit-book/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):

    connection = get_db_connection()

    # Find book
    book = connection.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    if book is None:

        connection.close()

        return "Book not found", 404

    # Update book
    if request.method == "POST":

        title = request.form["title"]
        author = request.form["author"]
        genre = request.form["genre"]
        total_pages = request.form["total_pages"]
        pages_read = request.form["pages_read"]
        status = request.form["status"]
        rating = request.form["rating"]
        start_date = request.form["start_date"]
        finish_date = request.form["finish_date"]
        notes = request.form["notes"]

        connection.execute(
            """
            UPDATE books
            SET
                title = ?,
                author = ?,
                genre = ?,
                total_pages = ?,
                pages_read = ?,
                status = ?,
                rating = ?,
                start_date = ?,
                finish_date = ?,
                notes = ?
            WHERE id = ?
            """,
            (
                title,
                author,
                genre,
                total_pages,
                pages_read,
                status,
                rating if rating else None,
                start_date,
                finish_date,
                notes,
                book_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(
            url_for(
                "book_details",
                book_id=book_id
            )
        )

    connection.close()

    return render_template(
        "edit_book.html",
        book=book
    )
    
@app.route("/delete-book/<int:book_id>")
def delete_book(book_id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM books WHERE id = ?",
        (book_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("books"))

@app.route("/statistics")
def statistics():

    connection = get_db_connection()


    # Summary statistics

    total_books = connection.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]


    completed_books = connection.execute(
        "SELECT COUNT(*) FROM books WHERE status = 'Completed'"
    ).fetchone()[0]


    currently_reading = connection.execute(
        "SELECT COUNT(*) FROM books WHERE status = 'Currently Reading'"
    ).fetchone()[0]


    pages_read = connection.execute(
        "SELECT SUM(pages_read) FROM books"
    ).fetchone()[0]


    if pages_read is None:
        pages_read = 0


    # Books by genre

    genre_data = connection.execute("""
        SELECT genre, COUNT(*) AS count
        FROM books
        GROUP BY genre
    """).fetchall()


    genre_labels = []
    genre_values = []


    for row in genre_data:

        genre_labels.append(
            row["genre"] or "Unknown"
        )

        genre_values.append(
            row["count"]
        )


    # Books by status

    status_data = connection.execute("""
        SELECT status, COUNT(*) AS count
        FROM books
        GROUP BY status
    """).fetchall()


    status_labels = []
    status_values = []


    for row in status_data:

        status_labels.append(
            row["status"]
        )

        status_values.append(
            row["count"]
        )


    # Books by rating

    rating_data = connection.execute("""
        SELECT rating, COUNT(*) AS count
        FROM books
        WHERE rating IS NOT NULL
        GROUP BY rating
        ORDER BY rating
    """).fetchall()


    rating_labels = []
    rating_values = []


    for row in rating_data:

        rating_labels.append(
            str(row["rating"])
        )

        rating_values.append(
            row["count"]
        )


    connection.close()


    return render_template(
        "statistics.html",

        total_books=total_books,

        completed_books=completed_books,

        currently_reading=currently_reading,

        pages_read=pages_read,

        genre_labels=genre_labels,

        genre_values=genre_values,

        status_labels=status_labels,

        status_values=status_values,

        rating_labels=rating_labels,

        rating_values=rating_values
    )


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)
