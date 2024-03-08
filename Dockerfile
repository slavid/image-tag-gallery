# Define the base image
FROM python:3.12-slim-bookworm

VOLUME [ "/app" ]

ENV FLASK_APP="/app/app.py"

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY app.py ./app.py
COPY templates ./templates
COPY styles.css ./static/css/

RUN flask db init
RUN flask db migrate
RUN flask db upgrade

EXPOSE 5000

CMD [ "flask", "run", "--host=0.0.0.0", "--port=5000"]