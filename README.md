# study-for-fastapi-gemini-todo

# Gemini AI 連携 ToDo 管理アプリ

雑なメモから AI が自動でタスクを抽出し、優先度と期限を判定して整理するアプリケーションです。

## 1. 開発の背景（動機）
- タスク整理が苦手な自分自身の課題を解決するため。
- 雑なメモを投げるだけでAIが構造化してくれるアプリを作成してみたい。

## 2. システム構成
- **Backend**: FastAPI (Python)
- **AI**: Gemini 2.5 Flash API
- **Database**: SQLite3
- **Frontend**: HTML / Jinja2 (FastAPI 標準テンプレート)

## 3. 主な機能と工夫した点
- **自然言語解析**: 「今日中に」「急ぎで」といった曖昧な表現を AI が解釈し、正確な日付と優先度に変換します。
- **構造化出力**: `response_schema` を利用し、AI の回答を JSON 形式に固定。プログラムでの安定したデータ処理を実現しました。
- **非同期処理**: API 呼び出しに `async/await` を採用し、サーバーのレスポンス性能を向上させています。

## 4. 使い方（セットアップ）
1. `requirements.txt` からライブラリをインストール
2. `.env` ファイルを作成し `GOOGLE_API_KEY` を設定
3. `uvicorn main:app --reload` で起動

## 🔑 Gemini API キーの取得方法
本アプリの動作には Gemini API キーが必要です。以下の手順で取得してください。

1. **Google AI Studio にアクセス**: 
   [Google AI Studio](https://aistudio.google.com/) へログインします。
2. **プロジェクトの作成**: 
   画面左側の「Get API key」から、新しい Google Cloud プロジェクトを作成します。
3. **API キーの発行**: 
   「Create API key in new project」をクリックしてキーを生成し、コピーします。

> [!CAUTION]
> **注意点**
> - **アカウントの制限**: 社用アカウントではプロジェクト作成が制限されている場合があります。その場合は私用アカウントでの作成を推奨します。
> - **管理方法**: 取得したキーは直接コードに書かず、 `.env` ファイルに `GOOGLE_API_KEY=あなたのキー` と記述することを推奨します。
