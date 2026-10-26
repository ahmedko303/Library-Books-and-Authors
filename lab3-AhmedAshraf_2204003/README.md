# Lab 3: Foreign Keys and Simple SQL

Problem 2 (Library: Books and Authors) built with **Python + Flask + MySQL**.

## What is in this folder

| File | What it does |
|---|---|
| `problem2_DDL.sql` | Creates the `library` database with the `author` and `book` tables (primary keys, foreign key with `ON DELETE CASCADE`) |
| `problem2_DML.sql` | Seed data: 4 authors and 8 books |
| `website/` | The Flask website (pages for show, add, edit and remove) |

## How to run it, step by step

1. **Install** Python 3 and MySQL Server, and make sure MySQL is running.
2. **Open a terminal in this folder** (`lab3-<student-id>`).
3. **Build the database and insert the seed data:**
   ```
   mysql -u root -p < problem2_DDL.sql
   mysql -u root -p < problem2_DML.sql
   ```
4. **Install the Python packages:**
   ```
   cd website
   pip install -r requirements.txt
   ```
5. **Tell the website your MySQL password.** Either open `website/app.py` and write it in `DB_CONFIG`
   (`"password": "your-password"`), or set it in the terminal first:
   - Windows (cmd): `set DB_PASSWORD=your-password`
   - Windows (PowerShell): `$env:DB_PASSWORD="your-password"`
   - Mac / Linux: `export DB_PASSWORD=your-password`
6. **Start the website:**
   ```
   python app.py
   ```
7. **Open** http://127.0.0.1:5000 in your browser.

## What you can do on the website

| Task | Where |
|---|---|
| F2.1 Show the books table (with `author_id`) and the authors table | Home page |
| F2.2 Add a book / add an author | "Add book" and "Add author" buttons |
| F2.3 Edit a book / edit an author | "Edit" button in each row |
| F2.4 Remove a book | "Remove" button in a book row |
| F2.5 Remove an author (their books are removed too) | "Remove" button in an author row |
| Bonus: book covers and author photos | Choose a picture in the add / edit forms |

## Notes

- Pictures are saved in `website/static/uploads/` as `book_<id>.jpg` and `author_<id>.jpg`, so the
  database tables keep exactly the schema from the lab sheet.
- Running `problem2_DDL.sql` again resets the database. Empty `website/static/uploads/` if you want
  the old pictures to go away too.
- Lab 2 pages: copy your Lab 2 files into `website/templates/` and `website/static/`, add their routes
  to `app.py`, and add a link in `templates/base.html`.
