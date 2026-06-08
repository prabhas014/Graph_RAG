import sqlite3

def check():
    try:
        conn = sqlite3.connect('c:\\Users\\prabh\\.gemini\\antigravity\\scratch\\graph-rag-system\\backend\\sql_app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, filename, status FROM documents")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        conn.close()
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    check()
