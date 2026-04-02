# Smart Data Processing & Validation Dashboard

This project is a full-stack Flask web app that validates user input, processes uploaded CSV/JSON datasets with pandas/numpy, generates multiple Matplotlib charts, and stores results as JSON.

## Features

- User input form:
  - Name, Email, Phone, Password validated with Regular Expressions (backend + optional frontend JS).
  - Optional dataset upload (CSV or JSON).
  - Also supports selecting a server-side sample dataset from a dropdown (useful for demos/screenshots).
- Dataset processing:
  - Computes per-column `mean`, `median`, and `std` using pandas/numpy.
  - Uses a generator (`row_generator`) for row-wise processing and a custom iterator (`DataIterator`).
- Data visualization (Matplotlib):
  - Correlation heatmap, boxplot, histogram distribution.
  - Bar chart (`bar_chart.png`) and line graph (`line_graph.png`).
  - Extra scatter plots when columns like `salary`/`experience`/`age` exist.
- Concurrency:
  - Multiprocessing for plot generation.
  - Multithreading for row-wise processing and threaded stats computation across column subsets.
- JSON storage:
  - Saves user registrations to `data/users.json`.
  - Saves processed dataset stats to `data/datasets.json`.

## Project Structure (key modules)

- `app.py` - Flask routes (`/` and `/submit`)
- `modules/`
  - `validation.py` - regex validation functions
  - `processing.py` - processors, abstract class, mixins, stats + plots
  - `threading_tasks.py` - threading helper
  - `multiprocessing_tasks.py` - multiprocessing helper for plots
  - `serialization.py` - JSON persistence for users
- `utils/`
  - `decorators.py` - timing + logging decorators
  - `iterators.py` - `DataIterator`
  - `generators.py` - `row_generator`
  - `mixins.py` - `SaveMixin`, `LoggingMixin`, and operator-overloaded `StatsSummary`

## Required Concepts (where implemented)

- Iterators & Generators
  - Generator: `utils/generators.py` (`row_generator`)
  - Custom iterator: `utils/iterators.py` (`DataIterator`)
- Decorators & Closures
  - `utils/decorators.py`: `timing_decorator`, `log_decorator`
- Advanced OOP
  - Abstract class: `modules/processing.py` (`DataProcessor`, `@abstractmethod`)
  - Mixins: `StatsMixin`, `SaveMixin`, `LoggingMixin`
  - Multiple inheritance & MRO: `CSVProcessor` / `JSONProcessor` extend multiple bases
  - Operator overloading: `utils/mixins.py` (`StatsSummary.__add__`) is used to merge threaded partial stats
- Python core + regex
  - Regex validation in `modules/validation.py`
- Multithreading & multiprocessing
  - Threaded stats computation: `StatsMixin.calculate_stats()` uses `ThreadPoolExecutor`
  - Multiprocessing: plot generation runs in a separate process via `modules/multiprocessing_tasks.py`
- Data serialization
  - Users: `modules/serialization.py` stores `data/users.json`
  - Dataset stats: `SaveMixin.save_stats()` stores into `data/datasets.json`

## How to Run

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Start the Flask app:
   - `python app.py`
4. Open the displayed local URL in your browser.

## Notes on Screenshots

After starting the server and uploading a CSV/JSON dataset, take screenshots of:
- The registration form (valid and invalid inputs).
- The dashboard page after upload (stats + charts).

Charts are saved under `static/` and referenced by the dashboard UI.

