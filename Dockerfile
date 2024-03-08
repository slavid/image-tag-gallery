# Define the base image
FROM python:3.12-slim-bookworm

VOLUME [ "/app" ]

RUN apt-get update && apt-get install -y sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ENV FLASK_APP="/app/app.py"

WORKDIR /app

COPY requirements.txt .

RUN python3 -m venv .venv
RUN . .venv/bin/activate

RUN sudo pip3 install -r requirements.txt

RUN echo "$(whereis flask)"

COPY app.py ./app.py
COPY templates ./templates
COPY styles.css ./static/css/

RUN sudo flask db init
RUN sudo flask db migrate
RUN sudo flask db upgrade

EXPOSE 5000

CMD [ "flask", "run", "--host=0.0.0.0", "--port=5000"]