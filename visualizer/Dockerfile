FROM python:3.11

WORKDIR /app/main.py
COPY . .

RUN pip install fastapi redis hypercorn

CMD ["python", "main.py"]
