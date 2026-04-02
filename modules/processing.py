import matplotlib
matplotlib.use('Agg')   # Prevent GUI/thread errors

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

# IMPORT UTILS
from utils.decorators import timing_decorator, log_decorator
from utils.mixins import LoggingMixin, SaveMixin, StatsSummary


# ---------------- ABSTRACT CLASS ----------------
class DataProcessor(ABC, LoggingMixin):

    @abstractmethod
    def process(self, file_path):
        pass


# ---------------- MIXIN (STATS + VISUALIZATION) ----------------
class StatsMixin:

    def calculate_stats(self, df):
        numeric_df = df.select_dtypes(include=['number'])
        if 'id' in numeric_df.columns:
            numeric_df = numeric_df.drop(columns=['id'])

        if numeric_df.empty:
            return StatsSummary(mean={}, median={}, std={})

        columns = list(numeric_df.columns)
        mid = len(columns) // 2 or 1
        col_chunks = [columns[:mid], columns[mid:]] if len(columns) > 1 else [columns]

        def compute_for_cols(cols):
            part = numeric_df[cols]
            return StatsSummary(
                mean=part.mean(numeric_only=True).to_dict(),
                median=part.median(numeric_only=True).to_dict(),
                std=part.std(numeric_only=True).to_dict(),
            )

        # Threaded computation across column subsets (independent per column stats).
        with ThreadPoolExecutor(max_workers=len(col_chunks)) as ex:
            futures = [ex.submit(compute_for_cols, chunk) for chunk in col_chunks if chunk]
            parts = [f.result() for f in futures]

        # Operator overloading merges the partial summaries.
        total = parts[0]
        for part in parts[1:]:
            total = total + part

        return total

    def generate_plots(self, df):

        os.makedirs("static", exist_ok=True)

        numeric_df = df.select_dtypes(include=['number'])

        if 'id' in numeric_df.columns:
            numeric_df = numeric_df.drop(columns=['id'])

        if numeric_df.empty:
            return

        # Choose columns for generic charts.
        first_col = numeric_df.columns[0]
        second_col = numeric_df.columns[1] if len(numeric_df.columns) > 1 else first_col

        # -------- 1. CORRELATION HEATMAP --------
        corr = numeric_df.corr()

        plt.figure(figsize=(6, 4))
        plt.imshow(corr, cmap='coolwarm', interpolation='nearest')
        plt.colorbar()

        plt.xticks(range(len(corr.columns)), corr.columns, rotation=45)
        plt.yticks(range(len(corr.columns)), corr.columns)

        for i in range(len(corr.columns)):
            for j in range(len(corr.columns)):
                plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha='center', va='center', color='black')

        plt.title("Feature Correlation")
        plt.tight_layout()
        plt.savefig("static/heatmap.png")
        plt.clf()

        # -------- 2. BOXPLOT --------
        plt.figure(figsize=(8, 5))
        plt.boxplot([numeric_df[col] for col in numeric_df.columns],
                    labels=numeric_df.columns)

        plt.title("Feature Spread & Outliers")
        plt.xticks(rotation=20)
        plt.tight_layout()
        plt.savefig("static/boxplot.png")
        plt.clf()

        # -------- 3. HISTOGRAM --------
        numeric_df.hist(figsize=(10, 6), bins=10)
        plt.suptitle("Feature Distributions")
        plt.tight_layout()
        plt.savefig("static/hist.png")
        plt.clf()

        # -------- 3.5 BAR CHART --------
        series = numeric_df[second_col].dropna()
        series = series.head(10)
        plt.figure(figsize=(7, 4))
        if not series.empty:
            plt.bar(range(1, len(series) + 1), series.values)
            plt.xticks(range(1, len(series) + 1), [str(i) for i in range(1, len(series) + 1)], rotation=0)
            plt.title(f"Top Values (bar) - {second_col}")
            plt.xlabel("Index")
            plt.ylabel(second_col)
        else:
            plt.text(0.5, 0.5, "Not enough data for bar chart", ha="center", va="center")
            plt.axis("off")
        plt.tight_layout()
        plt.savefig("static/bar_chart.png")
        plt.clf()

        # -------- 3.6 LINE GRAPH --------
        line_df = numeric_df[[first_col, second_col]].dropna()
        plt.figure(figsize=(7, 4))
        if not line_df.empty:
            # Sort by x to make the line visually meaningful.
            line_df = line_df.sort_values(by=first_col)
            plt.plot(line_df[first_col].values, line_df[second_col].values, linewidth=2)
            plt.title(f"{second_col} over {first_col} (line)")
            plt.xlabel(first_col)
            plt.ylabel(second_col)
        else:
            plt.text(0.5, 0.5, "Not enough data for line graph", ha="center", va="center")
            plt.axis("off")
        plt.tight_layout()
        plt.savefig("static/line_graph.png")
        plt.clf()

        # -------- 4. SCATTER (RELATIONSHIP) --------
        if 'salary' in numeric_df.columns:

            if 'experience' in numeric_df.columns:
                plt.figure(figsize=(6, 4))
                plt.scatter(numeric_df['experience'], numeric_df['salary'])

                # regression line
                z = np.polyfit(numeric_df['experience'], numeric_df['salary'], 1)
                p = np.poly1d(z)
                plt.plot(numeric_df['experience'], p(numeric_df['experience']), "r")

                plt.title("Salary vs Experience")
                plt.xlabel("Experience")
                plt.ylabel("Salary")
                plt.tight_layout()
                plt.savefig("static/salary_vs_experience.png")
                plt.clf()

            if 'age' in numeric_df.columns:
                plt.figure(figsize=(6, 4))
                plt.scatter(numeric_df['age'], numeric_df['salary'])

                z = np.polyfit(numeric_df['age'], numeric_df['salary'], 1)
                p = np.poly1d(z)
                plt.plot(numeric_df['age'], p(numeric_df['age']), "r")

                plt.title("Salary vs Age")
                plt.xlabel("Age")
                plt.ylabel("Salary")
                plt.tight_layout()
                plt.savefig("static/salary_vs_age.png")
                plt.clf()
# ---------------- CSV PROCESSOR ----------------
class CSVProcessor(DataProcessor, StatsMixin, SaveMixin):

    @log_decorator
    @timing_decorator
    def read_file(self, file_path):
        return pd.read_csv(file_path)

    def process(self, file_path):
        df = self.read_file(file_path)
        return self.calculate_stats(df)


# ---------------- JSON PROCESSOR ----------------
class JSONProcessor(DataProcessor, StatsMixin, SaveMixin):

    @log_decorator
    @timing_decorator
    def read_file(self, file_path):
        return pd.read_json(file_path)

    def process(self, file_path):
        df = self.read_file(file_path)
        return self.calculate_stats(df)