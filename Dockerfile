FROM python:3.11

WORKDIR /usr/src/app
COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD  ["python", "./main.py", "--host", "0.0.0.0","--port", "8000", "--reload","true"]