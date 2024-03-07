FROM python:3-alpine

ENV GID 1000
ENV UID 1000
ENV USER=docker
ENV GROUPNAME=$USER

RUN addgroup \
    --gid "$GID" \
    "$GROUPNAME" \
&&  adduser \
    --disabled-password \
    --gecos "" \
    --home "$(pwd)" \
    --ingroup "$GROUPNAME" \
    --no-create-home \
    --uid "$UID" \
    $USER

WORKDIR /usr/src/app

RUN chown -R docker:docker /usr/src/app

COPY --chown=docker:docker app.py .
COPY --chown=docker:docker requirements.txt .
COPY --chown=docker:docker templates ./templates

# RUN python3 -m venv .venv
# RUN . .venv/bin/activate
USER docker

RUN pip3 install -r requirements.txt

RUN flask db init
RUN flask db migrate
RUN flask db upgrade

EXPOSE 5000

CMD [ "flask", "run", "--host=0.0.0.0", "--port=5000"]
