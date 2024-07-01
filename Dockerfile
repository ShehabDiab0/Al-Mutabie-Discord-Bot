FROM python:3.11.4-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT [ "python3", "main.py", "/data/tasks.db", "/data/last_run.json" ]