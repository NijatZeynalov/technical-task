

1.  **Start DynamoDB Local**:
    Open a terminal and run the Docker container:
    ```bash
    docker run -d -p 8002:8000 amazon/dynamodb-local
    ```

2.  **Set Environment Variables**:
    In a new terminal, set the environment variables so the application can connect to the local database.

    **For Windows PowerShell (Recommended):**
    ```powershell
    $env:DYNAMODB_REGION="us-east-1"
    $env:DYNAMODB_HOST="http://localhost:8002"
    ```

    **For Windows Command Prompt (CMD):**
    ```cmd
    set DYNAMODB_REGION=us-east-1
    set DYNAMODB_HOST=http://localhost:8002
    ```

3.  **Create DynamoDB Tables**:
    With the environment variables set, run the table creation script:
    ```bash
    python create_tables.py
    ```


```bash
ollama --version
ollama serve
```

In a new PowerShell tab, pull the model used by the app

```bash
ollama pull phi3
```

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, and the documentation (Swagger UI) can be accessed at `http://127.0.0.1:8000/docs`.
