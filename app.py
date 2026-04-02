from flask import Flask, render_template, request
import os

# MODULES
from modules.validation import validate_name, validate_email, validate_phone, validate_password
from modules.processing import CSVProcessor, JSONProcessor
from modules.serialization import save_user
from modules.threading_tasks import run_in_thread
from modules.multiprocessing_tasks import run_in_process, generate_plots_in_process

# UTILS
from utils.iterators import DataIterator
from utils.generators import row_generator

app = Flask(__name__)


# HOME PAGE
@app.route('/')
def home():
    return render_template("index.html")


# FORM SUBMIT
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']
    file = request.files.get('file')
    dataset_choice = (request.form.get("dataset_choice") or "").strip()

    error = None

    # -------- VALIDATION --------
    if not validate_name(name):
        error = "Invalid Name"
    elif not validate_email(email):
        error = "Invalid Email"
    elif not validate_phone(phone):
        error = "Invalid Phone"
    elif not validate_password(password):
        error = "Weak Password"

    if error:
        return render_template("index.html", error=error)

    # -------- SAVE USER --------
    user = {
        "name": name,
        "email": email,
        "phone": phone,
        "password": password
    }
    save_user(user)

    stats = None

    # -------- DATASET PROCESSING --------
    # Priority: uploaded file -> dropdown dataset choice.
    if file and file.filename != "":
        filepath = os.path.join("data", file.filename)
        file.save(filepath)
    elif dataset_choice:
        # Prevent path traversal: accept only a simple filename.
        safe_choice = os.path.basename(dataset_choice)
        if safe_choice != dataset_choice:
            return render_template("index.html", error="Invalid dataset choice")

        filepath = os.path.join("data", safe_choice)
        if not os.path.exists(filepath):
            return render_template("index.html", error="Dataset not found")

    else:
        return render_template("dashboard.html", data=None)

    # SELECT PROCESSOR
    if filepath.endswith(".csv"):
        processor = CSVProcessor()
    elif filepath.endswith(".json"):
        processor = JSONProcessor()
    else:
        return render_template("index.html", error="Only CSV or JSON allowed")

    # READ DATA
    df = processor.read_file(filepath)

    # -------- MULTIPROCESSING (plots) --------
    plot_process = run_in_process(generate_plots_in_process, processor.__class__, df)

    # -------- GENERATOR USAGE (threaded) --------
    
    row_info = {"rows_processed": 0}

    def row_task():
        for _ in row_generator(df):
            row_info["rows_processed"] += 1

    row_thread = run_in_thread(row_task)

    # -------- CALCULATE STATS --------
    stats = processor.calculate_stats(df)

    row_thread.join()
    plot_process.join()

    # -------- SAVE DATASET STATS --------
    processor.save_stats(stats)

    # -------- ITERATOR USAGE --------
    iterator = DataIterator(list(stats.mean.items()))
    for item in iterator:
        print("Iterator Output:", item)

    # -------- THREADING (extra task) --------
    run_in_thread(print, "Background thread running...")

    return render_template("dashboard.html", data=stats)


# RUN APP
if __name__ == "__main__":
    app.run(debug=True)