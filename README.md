# パッケージのインストール

```sh
pip install -r requirements.txt
```

# .env ファイルの作成

プロジェクトのルートディレクトリに .env ファイルを作成し、以下のように API キーを記述します。

```sh
   OPENAI_API_KEY=your_openai_api_key
   QDRANT_API_KEY=your_qdrant_api_key
```

# API 動作確認手順

このドキュメントでは、`api.py` の機能を動作確認するための手順を説明します。

## 必要なパッケージのインストール

まず、必要なパッケージをインストールします。以下のコマンドをターミナルで実行してください。

```sh
pip install flask langchain PyPDF2 qdrant-client
```

## サーバーの起動

次に、`api.py` を実行して Flask サーバーを起動します。

```sh
python api.py
```

サーバーが起動すると、以下のようなメッセージが表示されます。

```
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

## エンドポイントのテスト

### 1. PDF ファイルのアップロード

`/api/upload_pdf` エンドポイントに PDF ファイルをアップロードします。以下のコマンドを使用します。

#### a. `curl` コマンドを使用する (Unix 系シェル)

```sh
curl -X POST -F "file=@path/to/your/file.pdf" http://127.0.0.1:5000/api/upload_pdf
```

#### b. PowerShell を使用する (Windows)

PowerShell でファイルをアップロードするためのスクリプトを使用します。

```powershell
$filePath = "path\to\your\file.pdf"
$fileName = [System.IO.Path]::GetFileName($filePath)
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
    "Content-Type: application/pdf",
    "",
    [System.IO.File]::ReadAllText($filePath),
    "--$boundary--",
    ""
) -join $LF

Invoke-WebRequest -Uri http://127.0.0.1:5000/api/upload_pdf -Method Post -ContentType "multipart/form-data; boundary=$boundary" -Body $bodyLines
```

### 2. 質問の送信

`/api/ask` エンドポイントに質問を送信します。以下のコマンドを使用します。

#### a. `curl` コマンドを使用する (Unix 系シェル)

```sh
curl -X POST -H "Content-Type: application/json" -d '{"query": "Your question here"}' http://127.0.0.1:5000/api/ask
```

#### b. PowerShell を使用する (Windows)

PowerShell で質問を送信するためのスクリプトを使用します。

```powershell
$json = '{"query": "Your question here"}'
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/ask -Method Post -Body $json -ContentType "application/json"
```

### 3. Postman を使用する

Postman を使用してエンドポイントをテストすることもできます。

#### a. PDF ファイルのアップロード

1. Postman を開きます。
2. 新しいリクエストを作成します。
3. `POST` メソッドを選択し、URL に `http://127.0.0.1:5000/api/upload_pdf` を入力します。
4. `Body` タブを選択し、`form-data` を選択します。
5. `Key` に `file` を入力し、`Value` にアップロードする PDF ファイルを選択します。
6. `Send` ボタンをクリックします。

#### b. 質問の送信

1. 新しいリクエストを作成します。
2. `POST` メソッドを選択し、URL に `http://127.0.0.1:5000/api/ask` を入力します。
3. `Body` タブを選択し、`raw` を選択して `JSON` フォーマットを選択します。
4. 以下のように JSON データを入力します。

   ```json
   {
     "query": "Your question here"
   }
   ```

5. `Send` ボタンをクリックします。

これで、API エンドポイントが正しく動作するかどうかを確認できます。
