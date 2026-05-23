import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime, timedelta


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="malaika2426,./",
    database="lms"
)

cur = conn.cursor()


def login():

    cur.execute(
        """
        SELECT role
        FROM users
        WHERE username=%s AND password=%s
        """,
        (user.get(), pwd.get())
    )

    res = cur.fetchone()

    if res:
        login_app.destroy()
        dashboard(res[0])
    else:
        messagebox.showerror("Error", "Invalid Login")

def dashboard(role):

    app = ctk.CTk()
    app.geometry("1400x750")
    app.title(f"University Of Rasul Library - {role}")

    sidebar = ctk.CTkFrame(app, width=220)
    sidebar.pack(side="left", fill="y")

    title = ctk.CTkLabel(
        sidebar,
        text="UNIVERSITY\nOF\nRASUL",
        font=("Arial", 26, "bold")
    )
    title.pack(pady=20)

    main = ctk.CTkFrame(app)
    main.pack(side="right", expand=True, fill="both")

    def clear():
        for widget in main.winfo_children():
            widget.destroy()


    def books_page():

        clear()

        top = ctk.CTkFrame(main) 
        top.pack(fill="x", pady=10)

        content = ctk.CTkFrame(main)
        content.pack(expand=True, fill="both")

        search_entry = ctk.CTkEntry(top, placeholder_text="Search Book")
        search_entry.pack(side="left", padx=10)

        cols = ("ID", "Title", "Author", "Category", "ISBN", "Copies", "Status")

        tree = ttk.Treeview(content, columns=cols, show="headings")

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=150)

        tree.pack(expand=True, fill="both")

        def load_books():

            for i in tree.get_children():
                tree.delete(i)

            cur.execute("""
            SELECT b.*,
            (SELECT COUNT(*) FROM issue WHERE book_id=b.id)
            FROM books b
            """)

            data = cur.fetchall()

            for row in data:
                available = row[5] - row[6]
                status = "Available" if available > 0 else "Not Available"

                tree.insert("", "end", values=(
                    row[0], row[1], row[2],
                    row[3], row[4], row[5], status
                ))

        load_books()

        def search_book():

            q = search_entry.get()

            for i in tree.get_children():
                tree.delete(i)

            cur.execute("""
            SELECT b.*,
            (SELECT COUNT(*) FROM issue WHERE book_id=b.id)
            FROM books b
            WHERE title LIKE %s
            OR author LIKE %s
            """, (f"%{q}%", f"%{q}%"))

            for row in cur.fetchall():
                available = row[5] - row[6]
                status = "Available" if available > 0 else "Not Available"

                tree.insert("", "end", values=(
                    row[0], row[1], row[2],
                    row[3], row[4], row[5], status
                ))

        ctk.CTkButton(top, text="Search", command=search_book).pack(side="left", padx=10)

        if role == "admin":

            def add_book():
                win = ctk.CTkToplevel(app)
                win.geometry("400x400")

                t = ctk.CTkEntry(win, placeholder_text="Title")
                a = ctk.CTkEntry(win, placeholder_text="Author")
                c = ctk.CTkEntry(win, placeholder_text="Category")
                i = ctk.CTkEntry(win, placeholder_text="ISBN")
                cp = ctk.CTkEntry(win, placeholder_text="Copies")

                for w in [t, a, c, i, cp]:
                    w.pack(pady=10)

                def save():
                    cur.execute("""
                    INSERT INTO books (title,author,category,isbn,copies)
                    VALUES(%s,%s,%s,%s,%s)
                    """, (t.get(), a.get(), c.get(), i.get(), cp.get()))

                    conn.commit()
                    messagebox.showinfo("Success", "Book Added")
                    win.destroy()
                    load_books()

                ctk.CTkButton(win, text="Save Book", command=save).pack(pady=20)

            def delete_book():
                sel = tree.selection()
                if not sel:
                    return

                book_id = tree.item(sel)["values"][0]

                cur.execute("DELETE FROM books WHERE id=%s", (book_id,))
                conn.commit()

                messagebox.showinfo("Success", "Book Deleted")
                load_books()

            def issue_book():
                sel = tree.selection()
                if not sel:
                    return

                book_id = tree.item(sel)["values"][0]

                win = ctk.CTkToplevel(app)
                win.geometry("300x250")

                member = ctk.CTkEntry(win, placeholder_text="Member ID")
                member.pack(pady=20)

                def save_issue():

                    due = datetime.now() + timedelta(days=10)

                    cur.execute("""
                    INSERT INTO issue (member_id,book_id,due_date)
                    VALUES(%s,%s,%s)
                    """, (member.get(), book_id, due.strftime("%Y-%m-%d")))

                    conn.commit()
                    messagebox.showinfo("Success", "Book Issued")
                    win.destroy()
                    load_books()

                ctk.CTkButton(win, text="Issue", command=save_issue).pack(pady=20)

            def return_book():
                sel = tree.selection()
                if not sel:
                    return

                book_id = tree.item(sel)["values"][0]

                cur.execute("DELETE FROM issue WHERE book_id=%s", (book_id,))
                conn.commit()

                messagebox.showinfo("Success", "Book Returned")
                load_books()

            ctk.CTkButton(top, text="Add Book", command=add_book).pack(side="left", padx=10)
            ctk.CTkButton(top, text="Issue Book", command=issue_book).pack(side="left", padx=10)
            ctk.CTkButton(top, text="Return Book", command=return_book).pack(side="left", padx=10)
            ctk.CTkButton(top, text="Delete Book", command=delete_book).pack(side="left", padx=10)
            
            
            
            # STUDENT / TEACHER
        if role in ["student", "teacher"]:

            def reserve_book():

                sel = tree.selection()
                if not sel:
                    return

                book_id = tree.item(sel)["values"][0]

                win = ctk.CTkToplevel(app)
                win.geometry("300x250")

                member = ctk.CTkEntry(win, placeholder_text="Member ID")
                member.pack(pady=20)

                def send():

                    cur.execute("""
                    INSERT INTO reserve_requests (member_id,book_id,status)
                    VALUES(%s,%s,'Pending')
                    """, (member.get(), book_id))

                    conn.commit()
                    messagebox.showinfo("Success", "Request Sent")
                    win.destroy()

                ctk.CTkButton(win, text="Reserve", command=send).pack(pady=20)

            ctk.CTkButton(top, text="Reserve Book", command=reserve_book).pack(side="left", padx=10)

            
    # =====================================================
    # MEMBER PAGE (UPDATED ONLY THIS PART)
    # =====================================================

    def member_page():

        clear()

        cols = ("ID", "Name", "Type", "Roll / Teacher ID")

        top = ctk.CTkFrame(main)
        top.pack(fill="x", pady=10)

        search_entry = ctk.CTkEntry(top, placeholder_text="Search Member by ID")
        search_entry.pack(side="left", padx=10)

        tree = ttk.Treeview(main, columns=cols, show="headings")

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=200)

        tree.pack(expand=True, fill="both")

        def load():

            for i in tree.get_children():
                tree.delete(i)

            cur.execute("SELECT * FROM members")

            for row in cur.fetchall():
                tree.insert("", "end", values=row)

        load()

        def search_member():

            q = search_entry.get()

            for i in tree.get_children():
                tree.delete(i)

            cur.execute("""
            SELECT * FROM members
            WHERE id LIKE %s
            """, (f"%{q}%",))

            for row in cur.fetchall():
                tree.insert("", "end", values=row)

        def add_member():

            win = ctk.CTkToplevel(app)
            win.geometry("320x360")

            mid = ctk.CTkEntry(win, placeholder_text="Member ID")
            name = ctk.CTkEntry(win, placeholder_text="Name")
            typ = ctk.CTkComboBox(win, values=["student", "teacher"])
            rid = ctk.CTkEntry(win, placeholder_text="Roll / Teacher ID")

            mid.pack(pady=10)
            name.pack(pady=10)
            typ.pack(pady=10)
            rid.pack(pady=10)

            def save():

                cur.execute("""
                INSERT INTO members
                VALUES (%s, %s, %s, %s)
                """, (mid.get(), name.get(), typ.get(), rid.get()))

                conn.commit()
                messagebox.showinfo("Success", "Member Added")
                win.destroy()
                load()

            ctk.CTkButton(win, text="Save", command=save).pack(pady=20)

        def delete_member():

            sel = tree.selection()
            if not sel:
                return

            mid = tree.item(sel)["values"][0]

            cur.execute("DELETE FROM members WHERE id=%s", (mid,))
            conn.commit()

            messagebox.showinfo("Success", "Member Deleted")
            load()

        ctk.CTkButton(top, text="Search", command=search_member).pack(side="left", padx=10)
        ctk.CTkButton(main, text="Add Member", command=add_member).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(main, text="Delete Member", command=delete_member).pack(side="left", padx=10, pady=10)

    # =====================================================
    # OTHER PAGES (UNCHANGED)
    # =====================================================

    def request_page():
        clear()

        cols = ("ID", "Member ID", "Book ID", "Status")
        tree = ttk.Treeview(main, columns=cols, show="headings")

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=200)

        tree.pack(expand=True, fill="both")

        def load():
            for i in tree.get_children():
                tree.delete(i)

            cur.execute("SELECT * FROM reserve_requests")

            for row in cur.fetchall():
                tree.insert("", "end", values=row)

        load()

        def approve():
            sel = tree.selection()
            if not sel:
                return

            rid = tree.item(sel)["values"][0]

            cur.execute("UPDATE reserve_requests SET status='Approved' WHERE id=%s", (rid,))
            conn.commit()
            load()

        def reject():
            sel = tree.selection()
            if not sel:
                return

            rid = tree.item(sel)["values"][0]

            cur.execute("UPDATE reserve_requests SET status='Rejected' WHERE id=%s", (rid,))
            conn.commit()
            load()

        ctk.CTkButton(main, text="Approve", command=approve).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(main, text="Reject", command=reject).pack(side="left", padx=10, pady=10)

    def fine_page():

        clear()

        cols = ("Issue ID", "Book ID", "Member ID", "Due Date",  "Fine")

        tree = ttk.Treeview(main, columns=cols, show="headings")

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=150)

        tree.pack(expand=True, fill="both")

        cur.execute("SELECT * FROM issue")
        data = cur.fetchall()

        for r in data:

            due = r[3]

            if isinstance(due, str):
                due = datetime.strptime(due, "%Y-%m-%d").date()

            late = max((datetime.now().date() - due).days, 0)
            fine = late * 50

            tree.insert("", "end", values=(
                r[0], r[2], r[1], due, late, fine
            ))

    # SIDEBAR
    ctk.CTkButton(sidebar, text="Books", command=books_page).pack(fill="x", pady=10)

    if role == "admin":
        ctk.CTkButton(sidebar, text="Members", command=member_page).pack(fill="x", pady=10)
        ctk.CTkButton(sidebar, text="Requests", command=request_page).pack(fill="x", pady=10)
        ctk.CTkButton(sidebar, text="Fine Records", command=fine_page).pack(fill="x", pady=10)

    books_page()
    app.mainloop()


# =========================================================
# LOGIN WINDOW
# =========================================================

login_app = ctk.CTk()
login_app.geometry("400x350")
login_app.title("University Of Rasul Login")

ctk.CTkLabel(login_app, text="UNIVERSITY OF RASUL", font=("Arial", 28, "bold")).pack(pady=30)

user = ctk.CTkEntry(login_app, placeholder_text="Username", width=250)
user.pack(pady=10)

pwd = ctk.CTkEntry(login_app, placeholder_text="Password", show="*", width=250)
pwd.pack(pady=10)

ctk.CTkButton(login_app, text="Login", width=200, command=login).pack(pady=20)

login_app.mainloop()