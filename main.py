import os
import sqlite3
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

load_dotenv()
app = FastAPI()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# データベースの初期設定
DB_FILE = "todos.db"

def init_db():
    """データベースとテーブルを作成する"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            priority TEXT,
            deadline TEXT
        )
    """)
    conn.commit()
    conn.close()


# アプリ起動時にテーブルを作る
init_db()

class MemoRequest(BaseModel):
    memo: str


@app.get("/list", response_class=HTMLResponse)
async def fet_list_view(request: Request):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    return templates.TemplateResponse("index.html", {"request": request, "todos": rows})
# ToDoを抽出して保存する
@app.post("/extract-todos")
async def extract_todos_api(request: MemoRequest):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"以下のメモからToDoを抽出して整理してください:\n{request.memo}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "タスク名": {"type": "STRING"},
                            "優先度": {"type": "STRING"},
                            "期限": {"type": "STRING"},
                        }
                    }
                }
            )
        )

        # ここでデータベースに保存する
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        for item in response.parsed:
            cursor.execute(
                "INSERT INTO todos (task, priority, deadline) VALUES (?, ?, ?)",
                (item["タスク名"], item["優先度"], item["期限"])
            )
        conn.commit()
        conn.close()

        return {"status": "success", "message": f"{len(response.parsed)}件保存しました", "data": response.parsed}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 保存されたToDoを一覧表示する
@app.get("/todos")
def get_all_todos():
    conn = sqlite3.connect(DB_FILE)
    # 辞書形式でデータを取り出すための設定
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()


    # データをリスト形式に変換して返す
    return [dict(row) for row in rows]


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    #指定されたidのデータを削除するSQLを実行
    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))

    #実際に削除されたか確認
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="指定されたidのタスクが見つかりませんでした。")

    conn.commit()
    conn.close()
    return{"status": "success", "message": f"id:{todo_id}のタスクを削除しました"}

