import json
import sqlite3
import pandas as pd
import os

def save_news_to_csv(data, filename="scraped_news.csv"):
    try:
        if os.path.exists(filename):
            df_existing = pd.read_csv(filename)
        else:
            df_existing = pd.DataFrame(columns=["title", "content"])

        existing_titles = set(df_existing["title"].tolist())

        new_entries = []
        updated_entries = 0

        for item in data:
            title, content = item["title"], item["content"]

            if title not in existing_titles:
                new_entries.append({"title": title, "content": content})
            else:
                existing_content = df_existing.loc[df_existing["title"] == title, "content"].values[0]
                if existing_content != content:
                    df_existing.loc[df_existing["title"] == title, "content"] = content
                    updated_entries += 1

        if new_entries:
            df_new = pd.DataFrame(new_entries)
            df_existing = pd.concat([df_existing, df_new], ignore_index=True)

        df_existing.to_csv(filename, index=False)
        print(f"✅ Data saved: {len(new_entries)} new | {updated_entries} updated.")
    
    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")


def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def write_json(file_path, data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    except Exception:
        return False

def create_table(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def insert_data(db_path, data):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO news (title, content) VALUES (?, ?)", data)
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def fetch_data(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT title, content FROM news")
        data = cursor.fetchall()
        conn.close()
        return data
    except Exception:
        return []
