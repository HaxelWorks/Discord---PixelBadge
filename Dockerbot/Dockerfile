FROM python:3.10

RUN apt-get update && apt-get install -y python3-pip && pip3 install --upgrade pip && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt


EXPOSE 8765


CMD ["python", "main.py"]
