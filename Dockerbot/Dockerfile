# A basic python 3.10 image
FROM python:3.10
#open port 8765 on ip 192.168.0.147

RUN apt-get update && apt-get install -y python3-pip && pip3 install --upgrade pip && apt-get clean && rm -rf /var/lib/apt/lists/*

# RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -

# RUN apt-get update && apt-get install -y nodejs && apt-get clean && rm -rf /var/lib/apt/lists


COPY . /app

WORKDIR /app

EXPOSE 8765

RUN pip install -r requirements.txt

CMD ["python", "main.py"]