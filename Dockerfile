FROM python:3-alpine

#ENV GID 1000
#ENV UID 1000

#USER ${UID}:${GID}

WORKDIR /usr/src/app

COPY app.py .
COPY requirements.txt .
COPY templates ./templates

# RUN python3 -m venv .venv
# RUN . .venv/bin/activate

RUN pip3 install -r requirements.txt

RUN flask db init
RUN flask db migrate
RUN flask db upgrade

EXPOSE 5000

VOLUME ["/usr/src/app"]

CMD [ "flask", "run", "--host=0.0.0.0", "--port=5000"]
