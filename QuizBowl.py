import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog

# ============================== DATABASE SETUP ===============================

DB_NAME = "quiz_bowl.db"

# NOTE: These are the course categories you are currently enrolled in.
# You will input the questions manually into the GUI for each of these classes:
# - DS 3400
# - BMGT 3720
# - DS 3850
# - DS 3860
# - FIN 3210
COURSES = {
    "MKT 3400": "mkt3400",
    "BMGT 3720": "bmgt3720",
    "DS 3850": "ds3850",
    "DS 3860": "ds3860",
    "FIN 3210": "fin3210"
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for table in COURSES.values():
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer TEXT NOT NULL
            );
        """)
    conn.commit()
    conn.close()

# =========================== QUESTION CLASS ============================

class Question:
    def __init__(self, question, options, correct):
        self.question = question
        self.options = options
        self.correct = correct

    def is_correct(self, answer):
        return answer == self.correct

# =========================== ADMIN INTERFACE ============================

class AdminInterface:
    def __init__(self, root):
        self.root = root
        self.admin_menu()

    def admin_menu(self):
        self.clear_screen()
        tk.Label(self.root, text="Admin Menu").pack(pady=10)
        tk.Button(self.root, text="Add Question", command=self.add_question).pack(pady=10)
        tk.Button(self.root, text="View Questions", command=self.view_questions).pack(pady=10)
        tk.Button(self.root, text="Exit Admin", command=self.exit_admin).pack(pady=10)

    def add_question(self):
        self.clear_screen()
        tk.Label(self.root, text="Select Course").pack()
        course_var = tk.StringVar()
        course_menu = tk.OptionMenu(self.root, course_var, *COURSES.keys())
        course_menu.pack()

        question_entry = tk.Entry(self.root, width=50)
        option_a = tk.Entry(self.root)
        option_b = tk.Entry(self.root)
        option_c = tk.Entry(self.root)
        option_d = tk.Entry(self.root)
        correct_answer = tk.Entry(self.root)

        tk.Label(self.root, text="Question:").pack()
        question_entry.pack()
        tk.Label(self.root, text="Option A:").pack()
        option_a.pack()
        tk.Label(self.root, text="Option B:").pack()
        option_b.pack()
        tk.Label(self.root, text="Option C:").pack()
        option_c.pack()
        tk.Label(self.root, text="Option D:").pack()
        option_d.pack()
        tk.Label(self.root, text="Correct Answer (A/B/C/D):").pack()
        correct_answer.pack()

        def save_question():
            table = COURSES[course_var.get()]
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {table} (question, option_a, option_b, option_c, option_d, correct_answer)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                question_entry.get(),
                option_a.get(),
                option_b.get(),
                option_c.get(),
                option_d.get(),
                correct_answer.get().upper()
            ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Saved", "Question added successfully!")
            self.admin_menu()

        tk.Button(self.root, text="Save Question", command=save_question).pack(pady=10)

    def view_questions(self):
        self.clear_screen()

    # Ask the admin to select which course's questions to view
        tk.Label(self.root, text="Select Course to View Questions").pack()
        course_var = tk.StringVar()
        course_menu = tk.OptionMenu(self.root, course_var, *COURSES.keys())
        course_menu.pack()

        def display_questions():
        # Get the selected course and fetch its questions from the database
            selected_course = course_var.get()
            table = COURSES[selected_course]
    
        # Connect to the database
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

        # Fetch questions from the selected course table
            cursor.execute(f"SELECT question, option_a, option_b, option_c, option_d, correct_answer FROM {table}")
            rows = cursor.fetchall()
            conn.close()

        # Create a canvas and a vertical scrollbar to make the questions scrollable
            canvas = tk.Canvas(self.root)
            scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)

        # Configure the canvas and scrollbar
            canvas.configure(yscrollcommand=scrollbar.set)

        # Create a window inside the canvas to hold all the questions
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Pack the canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

        # Add all the questions to the scrollable frame
            if rows:
                for i, row in enumerate(rows):
                    question, option_a, option_b, option_c, option_d, correct_answer = row
                    tk.Label(scrollable_frame, text=f"Q{i+1}: {question}").pack(pady=5)
                    tk.Label(scrollable_frame, text=f"A: {option_a}").pack(pady=5)
                    tk.Label(scrollable_frame, text=f"B: {option_b}").pack(pady=5)
                    tk.Label(scrollable_frame, text=f"C: {option_c}").pack(pady=5)
                    tk.Label(scrollable_frame, text=f"D: {option_d}").pack(pady=5)
                    tk.Label(scrollable_frame, text=f"Correct Answer: {correct_answer}").pack(pady=5)
                    tk.Label(scrollable_frame, text="-"*40).pack(pady=5)  # separator for clarity
            else:
                tk.Label(scrollable_frame, text="No questions available for this course.").pack(pady=10)

        # Button to go back to the admin menu
            tk.Button(scrollable_frame, text="Back to Admin Menu", command=self.admin_menu).pack(pady=10)

        # Update the scrollable frame's scroll region
            scrollable_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))

    # Display questions when button is clicked
        tk.Button(self.root, text="Display Questions", command=display_questions).pack(pady=10)


    def exit_admin(self):
        self.root.quit()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


# ========================= USER INTERFACE =============================

class QuizInterface:
    def __init__(self, root):
        self.root = root
        self.welcome_screen()

    def welcome_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Welcome to Quiz Bowl! Choose an option below:").pack(pady=10)
        tk.Button(self.root, text="Admin", command=self.admin_or_user).pack(pady=5)
        tk.Button(self.root, text="User", command=self.start_quiz).pack(pady=5)

    def admin_or_user(self):
        # Asking whether the user is admin or user, based on selection
        self.clear_screen()
        tk.Label(self.root, text="Please enter your selection:").pack(pady=10)
        self.login_screen()

    def login_screen(self):
        password = simpledialog.askstring("Admin Login", "Enter password:", show='*')
        if password == "admin123":
            # Directly open the admin interface after successful login
            AdminInterface(self.root)
        else:
            messagebox.showerror("Access Denied", "Incorrect Password")

    def start_quiz(self):
        self.clear_screen()
        self.select_course()

    def select_course(self):
        tk.Label(self.root, text="Select Course").pack()
        course_var = tk.StringVar()
        course_menu = tk.OptionMenu(self.root, course_var, *COURSES.keys())
        course_menu.pack()

        def start_quiz_for_course():
            self.start_quiz_for(course_var.get())

        tk.Button(self.root, text="Start Quiz", command=start_quiz_for_course).pack()

    def start_quiz_for(self, course):
        self.clear_screen()
        table = COURSES[course]
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(f"SELECT question, option_a, option_b, option_c, option_d, correct_answer FROM {table}")
        rows = cursor.fetchall()
        conn.close()

        self.questions = [Question(row[0], row[1:5], row[5]) for row in rows]
        self.score = 0
        self.q_index = 0
        self.display_question()

    def display_question(self):
        if self.q_index >= len(self.questions):
            self.show_score()
            return

        self.clear_screen()
        q = self.questions[self.q_index]
        tk.Label(self.root, text=q.question, wraplength=500).pack(pady=10)
        var = tk.StringVar()

        for i, opt in enumerate(['A', 'B', 'C', 'D']):
            tk.Radiobutton(self.root, text=q.options[i], variable=var, value=opt).pack(anchor="w")

        def submit():
            if var.get():
                if q.is_correct(var.get()):
                    self.score += 1
                    messagebox.showinfo("Correct", "That's correct!")
                else:
                    messagebox.showinfo("Incorrect", f"Wrong. Correct answer: {q.correct}")
                self.q_index += 1
                self.display_question()
            else:
                messagebox.showwarning("No Selection", "Please select an answer.")

        tk.Button(self.root, text="Submit", command=submit).pack(pady=10)

    def show_score(self):
        self.clear_screen()
        tk.Label(self.root, text=f"Quiz Completed! Your score: {self.score} / {len(self.questions)}").pack(pady=20)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()




# ============================= MAIN APP ===============================

if __name__ == "__main__":
    init_db()  # Ensure database and tables exist

    root = tk.Tk()
    root.title("Quiz Bowl Application")
    root.geometry("600x400")

    # Start the welcome screen (admin/user selection):
    QuizInterface(root)

    root.mainloop()
