FROM python:3.13-slim

WORKDIR /app

RUN apt update && apt install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "src/main.py"] 
