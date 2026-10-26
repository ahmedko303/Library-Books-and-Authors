import os
from decimal import Decimal, InvalidOperation

import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, abort

app = Flask(__name__)
app.secret_key = "library-secret"                 # needed for flash messages
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # images up to 5 MB

# ---- Database settings: change the password to yours ----
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "303120"),
    "database": "library",
}

UPLOAD_DIR = os.path.join(app.root_path, "static", "uploads")
ALLOWED = ["png", "jpg", "jpeg", "gif", "webp"]


# ---------- helpers ----------
def run(sql, params=(), write=False):
    """Run one SQL statement. SELECT returns rows, INSERT/UPDATE/DELETE returns the new id."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    if write:
        conn.commit()
        result = cur.lastrowid
    else:
        result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def image_path(kind, item_id):
    """Find the picture of a book ('book') or an author ('author'), if it exists."""
    for ext in ALLOWED:
        name = f"{kind}_{item_id}.{ext}"
        if os.path.exists(os.path.join(UPLOAD_DIR, name)):
            return name
    return None


@app.context_processor
def helpers():
    def image_url(kind, item_id):
        name = image_path(kind, item_id)
        if not name:
            return None
        version = int(os.path.getmtime(os.path.join(UPLOAD_DIR, name)))
        return url_for("static", filename=f"uploads/{name}", v=version)
    return {"image_url": image_url}


def remove_image(kind, item_id):
    name = image_path(kind, item_id)
    if name:
        os.remove(os.path.join(UPLOAD_DIR, name))


def save_image(file, kind, item_id):
    """Save an uploaded picture as book_<id>.ext or author_<id>.ext."""
    if not file or not file.filename:
        return
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED:
        flash("Picture skipped: use png, jpg, gif or webp.", "error")
        return
    remove_image(kind, item_id)
    file.save(os.path.join(UPLOAD_DIR, f"{kind}_{item_id}.{ext}"))


def read_price(text):
    try:
        price = Decimal(text)
    except InvalidOperation:
        return None
    return price if price >= 0 else None


# ---------- F2.1 show both tables ----------
@app.route("/")
def index():
    books = run("SELECT * FROM book")
    authors = run("SELECT * FROM author")
    names = {a["author_id"]: a["name"] for a in authors}
    return render_template("index.html", books=books, authors=authors, names=names)


# ---------- authors: add (F2.2), edit (F2.3), remove (F2.5) ----------
@app.route("/authors/add", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form["name"].strip()
        country = request.form["country"].strip()
        if not name:
            flash("Please write the author's name.", "error")
            return render_template("author_form.html", author=None)
        new_id = run("INSERT INTO author (name, country) VALUES (%s, %s)",
                     (name, country), write=True)
        save_image(request.files.get("photo"), "author", new_id)
        flash(f"Added author {name}.", "ok")
        return redirect(url_for("index"))
    return render_template("author_form.html", author=None)


@app.route("/authors/<int:author_id>/edit", methods=["GET", "POST"])
def edit_author(author_id):
    rows = run("SELECT * FROM author WHERE author_id = %s", (author_id,))
    if not rows:
        abort(404)
    if request.method == "POST":
        name = request.form["name"].strip()
        country = request.form["country"].strip()
        if not name:
            flash("Please write the author's name.", "error")
            return render_template("author_form.html", author=rows[0])
        run("UPDATE author SET name = %s, country = %s WHERE author_id = %s",
            (name, country, author_id), write=True)
        save_image(request.files.get("photo"), "author", author_id)
        flash(f"Saved changes to {name}.", "ok")
        return redirect(url_for("index"))
    return render_template("author_form.html", author=rows[0])


@app.route("/authors/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    # the books of this author are deleted by the database (ON DELETE CASCADE)
    books = run("SELECT book_id FROM book WHERE author_id = %s", (author_id,))
    run("DELETE FROM author WHERE author_id = %s", (author_id,), write=True)
    for b in books:
        remove_image("book", b["book_id"])
    remove_image("author", author_id)
    flash(f"Removed the author and {len(books)} book(s).", "ok")
    return redirect(url_for("index"))


# ---------- books: add (F2.2), edit (F2.3), remove (F2.4) ----------
@app.route("/books/add", methods=["GET", "POST"])
def add_book():
    authors = run("SELECT * FROM author")
    if not authors:
        flash("Add an author first, then you can add books.", "error")
        return redirect(url_for("add_author"))
    if request.method == "POST":
        title = request.form["title"].strip()
        price = read_price(request.form["price"])
        author_id = request.form["author_id"]
        if not title or price is None:
            flash("Write a title and a price of 0 or more.", "error")
            return render_template("book_form.html", book=None, authors=authors)
        new_id = run("INSERT INTO book (title, price, author_id) VALUES (%s, %s, %s)",
                     (title, price, author_id), write=True)
        save_image(request.files.get("cover"), "book", new_id)
        flash(f"Added the book {title}.", "ok")
        return redirect(url_for("index"))
    return render_template("book_form.html", book=None, authors=authors)


@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    rows = run("SELECT * FROM book WHERE book_id = %s", (book_id,))
    if not rows:
        abort(404)
    authors = run("SELECT * FROM author")
    if request.method == "POST":
        title = request.form["title"].strip()
        price = read_price(request.form["price"])
        author_id = request.form["author_id"]
        if not title or price is None:
            flash("Write a title and a price of 0 or more.", "error")
            return render_template("book_form.html", book=rows[0], authors=authors)
        run("UPDATE book SET title = %s, price = %s, author_id = %s WHERE book_id = %s",
            (title, price, author_id, book_id), write=True)
        save_image(request.files.get("cover"), "book", book_id)
        flash(f"Saved changes to {title}.", "ok")
        return redirect(url_for("index"))
    return render_template("book_form.html", book=rows[0], authors=authors)


@app.route("/books/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    run("DELETE FROM book WHERE book_id = %s", (book_id,), write=True)
    remove_image("book", book_id)
    flash("Removed the book.", "ok")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
