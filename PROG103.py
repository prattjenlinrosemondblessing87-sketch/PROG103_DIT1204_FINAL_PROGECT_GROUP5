import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


# ======================== DATABASE ========================
class Database:
    def __init__(self, db_name="school.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                gender TEXT,
                dob TEXT,
                course TEXT,
                enrollment_date TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                instructor TEXT,
                duration TEXT,
                fee REAL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date TEXT,
                status TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
        ''')
        self.conn.commit()

    def insert_student(self, name, email, phone, gender, dob, course, enrollment_date):
        try:
            self.cursor.execute('''
                INSERT INTO students (name, email, phone, gender, dob, course, enrollment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, email, phone, gender, dob, course, enrollment_date))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def fetch_students(self):
        self.cursor.execute("SELECT * FROM students")
        return self.cursor.fetchall()

    def fetch_student_by_id(self, student_id):
        self.cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
        return self.cursor.fetchone()

    def update_student(self, student_id, name, email, phone, gender, dob, course):
        self.cursor.execute('''
            UPDATE students SET name=?, email=?, phone=?, gender=?, dob=?, course=?
            WHERE id=?
        ''', (name, email, phone, gender, dob, course, student_id))
        self.conn.commit()

    def delete_student(self, student_id):
        self.cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
        self.conn.commit()

    def insert_course(self, name, instructor, duration, fee):
        self.cursor.execute('''
            INSERT INTO courses (name, instructor, duration, fee) VALUES (?, ?, ?, ?)
        ''', (name, instructor, duration, fee))
        self.conn.commit()

    def fetch_courses(self):
        self.cursor.execute("SELECT * FROM courses")
        return self.cursor.fetchall()

    def fetch_courses_names(self):
        self.cursor.execute("SELECT name FROM courses")
        return [row[0] for row in self.cursor.fetchall()]

    def insert_attendance(self, student_id, date, status):
        self.cursor.execute('''
            INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)
        ''', (student_id, date, status))
        self.conn.commit()

    def fetch_attendance(self, student_id):
        self.cursor.execute("SELECT * FROM attendance WHERE student_id=? ORDER BY date DESC",
                            (student_id,))
        return self.cursor.fetchall()

    def get_stats(self):
        self.cursor.execute("SELECT COUNT(*) FROM students")
        total_students = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM courses")
        total_courses = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM attendance WHERE status='Present'")
        present_count = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM attendance")
        total_attendance = self.cursor.fetchone()[0]
        return total_students, total_courses, present_count, total_attendance


# ======================== MAIN APPLICATION ========================
class EducationManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Education Management System")
        self.root.geometry("1200x750")
        self.root.minsize(1100, 700)
        self.root.configure(bg="#f0f2f5")

        self.db = Database()
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Custom colors
        self.COLORS = {
            "primary": "#2c3e50",
            "secondary": "#3498db",
            "accent": "#e74c3c",
            "success": "#27ae60",
            "warning": "#f39c12",
            "bg": "#f0f2f5",
            "card": "#ffffff",
            "text": "#2c3e50",
            "text_light": "#7f8c8d",
            "border": "#dcdde1",
            "header": "#2c3e50",
            "gradient1": "#2c3e50",
            "gradient2": "#3498db",
            "hover": "#ecf0f1"
        }

    def create_widgets(self):
        # ===== TOP HEADER BAR =====
        header_frame = tk.Frame(self.root, bg=self.COLORS["primary"], height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="🎓 Education Management System",
                 font=("Segoe UI", 20, "bold"),
                 fg="white", bg=self.COLORS["primary"]).pack(side="left", padx=20, pady=10)

        tk.Label(header_frame, text=f"📅 {datetime.now().strftime('%d %B %Y')}",
                 font=("Segoe UI", 11),
                 fg="#ecf0f1", bg=self.COLORS["primary"]).pack(side="right", padx=20, pady=10)

        # ===== SIDEBAR =====
        sidebar = tk.Frame(self.root, bg=self.COLORS["primary"], width=220)
        sidebar.pack(fill="y", side="left")
        sidebar.pack_propagate(False)

        # Sidebar menu items
        menu_items = [
            ("📊  Dashboard", self.show_dashboard),
            ("👨‍🎓  Students", self.show_students),
            ("📚  Courses", self.show_courses),
            ("✅  Attendance", self.show_attendance),
        ]

        tk.Label(sidebar, text="", bg=self.COLORS["primary"], height=2).pack()

        self.menu_buttons = []
        for text, cmd in menu_items:
            btn = tk.Button(sidebar, text=text, font=("Segoe UI", 12, "bold"),
                            fg="white", bg=self.COLORS["primary"],
                            relief="flat", cursor="hand2",
                            anchor="w", padx=20, pady=12,
                            activebackground=self.COLORS["secondary"],
                            activeforeground="white",
                            command=cmd)
            btn.pack(fill="x")
            self.menu_buttons.append(btn)

        # Highlight first button
        self.menu_buttons[0].config(bg=self.COLORS["secondary"])

        # ===== MAIN CONTENT AREA =====
        self.content_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        self.content_frame.pack(fill="both", expand=True)

        # Show dashboard by default
        self.show_dashboard()

    # ==================== DASHBOARD ====================
    def show_dashboard(self):
        self.clear_content()
        self.highlight_button(0)

        total_students, total_courses, present, total_att = self.db.get_stats()

        # Stats Cards Row
        cards_frame = tk.Frame(self.content_frame, bg=self.COLORS["bg"])
        cards_frame.pack(fill="x", padx=20, pady=20)

        stats = [
            ("👨‍🎓 Total Students", total_students, self.COLORS["secondary"]),
            ("📚 Total Courses", total_courses, self.COLORS["success"]),
            ("✅ Present Today", present, self.COLORS["warning"]),
            ("📋 Attendance Rate",
             f"{round((present/total_att)*100, 1) if total_att > 0 else 0}%",
             self.COLORS["accent"])
        ]

        for i, (title, value, color) in enumerate(stats):
            card = tk.Frame(cards_frame, bg=color, width=250, height=120)
            card.pack(side="left", padx=10, fill="both", expand=True)
            card.pack_propagate(False)

            tk.Label(card, text=title, font=("Segoe UI", 11),
                     fg="white", bg=color).pack(pady=(15, 5))
            tk.Label(card, text=str(value), font=("Segoe UI", 28, "bold"),
                     fg="white", bg=color).pack()

        # Recent Students Table
        table_frame = tk.Frame(self.content_frame, bg=self.COLORS["card"],
                               relief="flat", bd=0)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(table_frame, text="📋 Recent Students",
                 font=("Segoe UI", 14, "bold"),
                 fg=self.COLORS["text"], bg=self.COLORS["card"]).pack(pady=(15, 10), anchor="w")

        # Table
        tree_frame = tk.Frame(table_frame, bg=self.COLORS["card"])
        tree_frame.pack(fill="both", expand=True)

        columns = ("ID", "Name", "Email", "Course", "Enrolled")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)

        self.style.configure("Treeview",
                             background=self.COLORS["card"],
                             foreground=self.COLORS["text"],
                             rowheight=35,
                             font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading",
                             background=self.COLORS["primary"],
                             foreground="white",
                             font=("Segoe UI", 10, "bold"))
        self.style.configure("Treeview", bd=0)
        self.style.configure("Treeview.Focus", background="transparent")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Populate
        students = self.db.fetch_students()
        for s in students[-10:]:
            self.tree.insert("", "end", values=(s[0], s[1], s[2], s[6], s[7]))

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    # ==================== STUDENTS PAGE ====================
    def show_students(self):
        self.clear_content()
        self.highlight_button(1)

        # Left: Form | Right: Table
        left_frame = tk.Frame(self.content_frame, bg=self.COLORS["card"], width=380)
        left_frame.pack(fill="y", side="left", padx=20, pady=20, ipadx=10)
        left_frame.pack_propagate(False)

        right_frame = tk.Frame(self.content_frame, bg=self.COLORS["card"])
        right_frame.pack(fill="both", expand=True, padx=(0, 20), pady=20)

        # ---- FORM ----
        form_title = tk.Label(left_frame, text="👨‍🎓 Student Registration",
                               font=("Segoe UI", 16, "bold"),
                               fg=self.COLORS["text"], bg=self.COLORS["card"])
        form_title.pack(pady=(20, 5))

        tk.Label(left_frame, text="─" * 40, bg=self.COLORS["card"],
                 fg=self.COLORS["border"]).pack()

        fields = ["Full Name", "Email", "Phone", "Gender", "Date of Birth", "Course"]
        self.student_entries = {}
        self.gender_var = tk.StringVar(value="Male")
        self.course_var = tk.StringVar()

        courses = self.db.fetch_courses_names()
        if courses:
            self.course_var.set(courses[0])

        y = 10
        for field in fields:
            tk.Label(left_frame, text=field + ":", font=("Segoe UI", 10, "bold"),
                     fg=self.COLORS["text"], bg=self.COLORS["card"],
                     anchor="w").pack(fill="x", padx=(15, 10), pady=(y, 0))
            y = 2

            if field == "Gender":
                ttk.Combobox(left_frame, textvariable=self.gender_var,
                             values=["Male", "Female", "Other"], state="readonly",
                             width=22, font=("Segoe UI", 10)).pack(fill="x", padx=(15, 10), pady=(0, 5))
            elif field == "Course":
                ttk.Combobox(left_frame, textvariable=self.course_var,
                             values=courses, state="readonly",
                             width=22, font=("Segoe UI", 10)).pack(fill="x", padx=(15, 10), pady=(0, 5))
            else:
                entry = ttk.Entry(left_frame, font=("Segoe UI", 10), width=24)
                entry.pack(fill="x", padx=(15, 10), pady=(0, 5))
                self.student_entries[field] = entry

        # Buttons
        btn_frame = tk.Frame(left_frame, bg=self.COLORS["card"])
        btn_frame.pack(fill="x", padx=15, pady=15)

        tk.Button(btn_frame, text="➕  Add Student", font=("Segoe UI", 11, "bold"),
                  bg=self.COLORS["success"], fg="white", relief="flat",
                  cursor="hand2", activebackground="#219a52",
                  command=self.add_student).pack(fill="x", pady=3)

        tk.Button(btn_frame, text="🔄  Refresh", font=("Segoe UI", 11, "bold"),
                  bg=self.COLORS["secondary"], fg="white", relief="flat",
                  cursor="hand2", activebackground="#2980b9",
                  command=self.refresh_students).pack(fill="x", pady=3)

        tk.Button(btn_frame, text="✏️  Update Selected", font=("Segoe UI", 11, "bold"),
                  bg=self.COLORS["warning"], fg="white", relief="flat",
                  cursor="hand2", activebackground="#e67e22",
                  command=self.update_student).pack(fill="x", pady=3)

        tk.Button(btn_frame, text="🗑️  Delete Selected", font=("Segoe UI", 11, "bold"),
                  bg=self.COLORS["accent"], fg="white", relief="flat",
                  cursor="hand2", activebackground="#c0392b",
                  command=self.delete_student).pack(fill="x", pady=3)

        # ---- TABLE ----
        tk.Label(right_frame, text="📋 Student Records",
                 font=("Segoe UI", 14, "bold"),
                 fg=self.COLORS["text"], bg=self.COLORS["card"]).pack(pady=(10, 5), anchor="w")

        # Search bar
        search_frame = tk.Frame(right_frame, bg=self.COLORS["card"])
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="🔍", font=("Segoe UI", 12),
                 bg=self.COLORS["card"]).pack(side="left", padx=5)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.search_students)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var,
                                 font=("Segoe UI", 10), width=25)
        search_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Treeview
        columns = ("ID", "Name", "Email", "Phone", "Gender", "Course", "Enrolled")
        self.student_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=16)

        for col in columns:
            self.student_tree.heading(col, text=col)
            widths = {"ID": 50, "Name": 130, "Email": 160, "Phone": 110,
                      "Gender": 70, "Course": 120, "Enrolled": 110}
            self.student_tree.column(col, width=widths.get(col, 100), anchor="center")

        self.student_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.student_tree.bind("<<TreeviewSelect>>", self.on_student_select)

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical",
                                  command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.refresh_students()

    def add_student(self):
        name = self.student_entries["Full Name"].get().strip()
        email = self.student_entries["Email"].get().strip()
        phone = self.student_entries["Phone"].get().strip()
        gender = self.gender_var.get()
        dob = self.student_entries["Date of Birth"].get().strip()
        course = self.course_var.get()

        if not all([name, email, course]):
            messagebox.showwarning("Missing Data", "Name, Email, and Course are required!")
            return

        enrollment = datetime.now().strftime("%Y-%m-%d")
        success = self.db.insert_student(name, email, phone, gender, dob, course, enrollment)

        if success:
            messagebox.showinfo("Success", "✅ Student added successfully!")
            self.clear_form()
            self.refresh_students()
        else:
            messagebox.showerror("Error", "❌ Email already exists!")

    def refresh_students(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        students = self.db.fetch_students()
        for s in students:
            self.student_tree.insert("", "end", values=(
                s[0], s[1], s[2], s[3], s[4], s[6], s[7]))

    def search_students(self, *args):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        keyword = self.search_var.get().lower()
        students = self.db.fetch_students()

        for s in students:
            if keyword in str(s[1]).lower() or keyword in str(s[2]).lower() or keyword in str(s[6]).lower():
                self.student_tree.insert("", "end", values=(
                    s[0], s[1], s[2], s[3], s[4], s[6], s[7]))

    def on_student_select(self, event):
        selected = self.student_tree.selection()
        if selected:
            item = self.student_tree.item(selected[0])
            values = item["values"]
            self.student_entries["Full Name"].delete(0, "end")
            self.student_entries["Full Name"].insert(0, values[1])
            self.student_entries["Email"].delete(0, "end")
            self.student_entries["Email"].insert(0, values[2])
            self.student_entries["Phone"].delete(0, "end")
            self.student_entries["Phone"].insert(0, values[3])
            self.gender_var.set(values[4])
            self.course_var.set(values[5])

    def update_student(self):
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a student to update!")
            return

        values = self.student_tree.item(selected[0])["values"]
        student_id = values[0]
        name = self.student_entries["Full Name"].get().strip()
        email = self.student_entries["Email"].get().strip()
        phone = self.student_entries["Phone"].get().strip()
        gender = self.gender_var.get()
        dob = self.student_entries["Date of Birth"].get().strip()
        course = self.course_var.get()

        self.db.update_student(student_id, name, email, phone, gender, dob, course)
        messagebox.showinfo("Success", "✅ Student updated!")
        self.refresh_students()

    def delete_student(self):
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a student to delete!")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?"):
            values = self.student_tree.item(selected[0])["values"]
            self.db.delete_student(values[0])
            messagebox.showinfo("Deleted", "🗑️ Student deleted!")
            self.refresh_students()
            self.clear_form()

    def clear_form(self):
        for entry in self.student_entries.values():
            entry.delete(0, "end")
        self.gender_var.set("Male")

    # ==================== COURSES PAGE ====================
    def show_courses(self):
        self.clear_content()
        self.highlight_button(2)

        left_frame = tk.Frame(self.content_frame, bg=self.COLORS["card"], width=350)
        left_frame.pack(fill="y", side="left", padx=20, pady=20, ipadx=10)
        left_frame.pack_propagate(False)

        right_frame = tk.Frame(self.content_frame, bg=self.COLORS["card"])
        right_frame.pack(fill="both", expand=True, padx=(0, 20), pady=20)

        # Form
        tk.Label(left_frame, text="📚 Course Management",
                 font=("Segoe UI", 16, "bold"),
                 fg=self.COLORS["text"], bg=self.COLORS["card"]).pack(pady=(20, 5))
        tk.Label(left_frame, text="─" * 40, bg=self.COLORS["card"],
                 fg=self.COLORS["border"]).pack()

        fields = ["Course Name", "Instructor", "Duration", "Fee ($)"]
        self.course_entries = {}

        for field in fields:
            tk.Label(left_frame, text=field + ":", font=("Segoe UI", 10, "bold"),
                     fg=self.COLORS["text"], bg=self.COLORS["card"],
                     anchor="w").pack(fill="x", padx=(15, 10), pady=(8, 0))
            entry = ttk.Entry(left_frame, font=("Segoe UI", 10), width=22)
            entry.pack(fill="x", padx=(15, 10), pady=(0, 5))
            self.course_entries[field] = entry

        tk.Button(left_frame, text="➕  Add Course", font=("Segoe UI", 11, "bold"),
                  bg=self.COLORS["success"], fg="white", relief="flat",
                  cursor="hand2", activebackground="#219a52",
                  command=self.add_course).pack(fill="x", padx=15, pady=15)

        # Table
        tk.Label(right_frame, text="📋 Course List",
                 font=("Segoe UI", 14, "bold"),
                 fg=self.COLORS["text"], bg=self.COLORS["card"]).pack(pady=(10, 5), anchor="w")

        columns = ("ID", "Course Name", "Instructor", "Duration", "Fee")
        self.course_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=16)

        for col in columns:
            self.course_tree.heading(col, text=col)
            self.course_tree.column(col, width=150, anchor="center")

        self.course_tree.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical",
                                  command=self.course_tree.yview)
        self.course_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.refresh_courses()

    def add_course(self):
        name = self.course_entries["Course Name"].get().strip()
        instructor = self.course_entries["Instructor"].get().strip()
        duration = self.course_entries["Duration"].get().strip()
        fee = self.course_entries["Fee ($)"].get().strip()

        if not name or not instructor:
            messagebox.showwarning("Missing Data", "Course Name and Instructor are required!")
            return

        try:
            fee_val = float(fee) if fee else 0
        except ValueError:
            messagebox.showerror("Error", "Fee must be a number!")
            return

        self.db.insert_course(name, instructor, duration, fee_val)
        messagebox.showinfo("Success", "✅ Course added!")
        for e in self.course_entries.values():
            e.delete(0, "end")
        self.refresh_courses()

    def refresh_courses(self):
        for item in self.course_tree.get_children():
            self.course_tree.delete(item)
        for c in self.db.fetch_courses():
            self.course_tree.insert("", "end", values=(c[0], c[1], c[2], c[3], c[4]))

    # ==================== ATTENDANCE PAGE ====================
    def show_attendance(self):
        self.clear_content()
        self.highlight_button(3)

        left_frame = tk.Frame(self.content_frame, bg=self.COLORS["card"], width=350)
        left_frame.pack(fill="y", side="left", padx=20, pady=20, ipadx=10)
        left_frame.pack_propagate(False)

        right_frame = tk.Frame(self.content_frame, bg=self.COLORS["card"])
        right_frame.pack(fill="both", expand=True, padx=(0, 20), pady=20)

        # Form
        tk.Label(left_frame, text="✅ Attendance Marking",
                 font=("Segoe UI", 16, "bold"),
                 fg=self.COLORS["text"], bg=self.COLORS["card"]).pack(pady=(20, 5))
        tk.Label(left_frame, text="─" * 40, bg=self.COLORS["card"],
                 fg=self.COLORS["border"]).pack()

        tk.Label(left_frame, text="Student:", font=("Segoe UI", 10, "bold"),
                 fg=self.COLORS["text"], bg=self.COLORS["card"],
                 anchor="w").pack(fill="x", padx=(15, 10), pady=(10, 0))

        students = self.db.fetch_students()
        student_list = [(f"{s[1]} (ID: {s[0]})", s[0]) for s in students]
        if not student_list:
            student_list = [("No students found", 0)]

        self.attendance_student_var = tk.StringVar(value=student_list[0][0] if student_list else "")
        self.attendance_student_map = dict(student_list)

        ttk.Combobox(left_frame, textvariable=self.attendance_student_var,
                     values=[s[0] for s in student_list], state="readonly",
                     width=28, font=("Segoe UI", 10)).pack(fill="x", padx=(15, 10), pady=(0, 5))

        tk.Label(left_frame, text="Date:", font=("Segoe UI", 10, "bold"),
                 fg=self.COLORS["text"], bg=self.COLORS["card"],
                 anchor="w").pack(fill="x", padx=(15, 10), pady=(10, 0))

        self.attendance_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(left_frame, textvariable=self.attendance_date_var,
                  font=("Segoe UI", 10), width=26).pack(fill="x", padx=(15, 10), pady=(0, 5))

        tk.Label(left_frame, text="Status:", font=("Segoe UI", 10, "bold"),
                 fg=self.COLORS["text"], bg=self.COLORS["card"],
                 anchor="w").pack(fill="x", padx=(15, 10), pady=(10, 0))

        self.attendance_status_var = tk.StringVar(value="Present")
        ttk.Combobox(left_frame, textvariable=self.attendance_status_var,
                     values=["Present", "Absent", "Late"], state="readonly",
                     width=26, font=("Segoe UI", 10)).pack(fill="x", padx=(15, 10), pady=(0, 5))

        tk.Button(left_frame, text="✅  Mark Attendance", font=("Segoe UI", 11, "bold"),
                  bg=self.COLORS["secondary"], fg="white", relief="flat",
                  cursor="hand2", activebackground="#2980b9",
                  command=self.mark_attendance).pack(fill="x", padx=15, pady=15)

        tk.Button(left_frame, text="📊  View History", font=("Segoe UI", 11, "bold"),
                  bg=self.COLORS["warning"], fg="white", relief="flat",
                  cursor="hand2", activebackground="#e67e22",
                  command=self.view_attendance_history).pack(fill="x", padx=15, pady=5)

        # Table
        tk.Label(right_frame, text="📋 Latest Attendance Records",
                 font=("Segoe UI", 14, "bold"),
                 fg=self.COLORS["text"], bg=self.COLORS["card"]).pack(pady=(10, 5), anchor="w")

        columns = ("ID", "Student", "Date", "Status")
        self.attendance_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=16)

        for col in columns:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=150, anchor="center")

        self.attendance_tree.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical",
                                  command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.refresh_attendance()

    def mark_attendance(self):
        sel = self.attendance_student_var.get()
        if sel == "No students found":
            messagebox.showwarning("No Data", "Add students first!")
            return

        student_id = self.attendance_student_map.get(sel, 0)
        date = self.attendance_date_var.get()
        status = self.attendance_status_var.get()

        self.db.insert_attendance(student_id, date, status)
        messagebox.showinfo("Success", f"✅ {status} marked for {sel}")
        self.refresh_attendance()

    def refresh_attendance(self):
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        self.cursor = self.db.conn.cursor()
        self.cursor.execute('''
            SELECT a.id, s.name, a.date, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            ORDER BY a.date DESC, a.id DESC
            LIMIT 50
        ''')
        for row in self.cursor.fetchall():
            self.attendance_tree.insert("", "end", values=row)

    def view_attendance_history(self):
        sel = self.attendance_student_var.get()
        if sel == "No students found":
            messagebox.showwarning("No Data", "Add students first!")
            return

        student_id = self.attendance_student_map.get(sel, 0)
        records = self.db.fetch_attendance(student_id)

        if not records:
            messagebox.showinfo("No Records", "No attendance records found.")
            return

        win = tk.Toplevel(self.root)
        win.title("Attendance History")
        win.geometry("500x400")
        win.configure(bg=self.COLORS["bg"])

        tk.Label(win, text=f"📊 History for Student ID: {student_id}",
                 font=("Segoe UI", 13, "bold"),
                 fg=self.COLORS["text"], bg=self.COLORS["bg"]).pack(pady=10)

        cols = ("Date", "Status")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=15)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=180, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for r in records:
            tree.insert("", "end", values=(r[2], r[3]))

        ttk.Scrollbar(win, orient="vertical", command=tree.yview).pack(side="right", fill="y")
        tree.configure(yscrollcommand=ttk.Scrollbar(win, orient="vertical", command=tree.yview).set)

    # ==================== HELPERS ====================
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def highlight_button(self, index):
        for btn in self.menu_buttons:
            btn.config(bg=self.COLORS["primary"])
        self.menu_buttons[index].config(bg=self.COLORS["secondary"])


# ======================== RUN APP ========================
if __name__ == "__main__":
    root = tk.Tk()
    app = EducationManagementSystem(root)
root.mainloop()