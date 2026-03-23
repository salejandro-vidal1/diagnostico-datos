FROM python:3.11

WORKDIR /app/main.py
COPY . .

RUN pip install requests redis

CMD ["python", "main.py"]
