FROM python:3.12-slim-bookworm

ENV GID 1000
ENV UID 1000
ENV USER=docker
ENV GROUPNAME=$USER

RUN apt-get update \
 && apt-get install -y sudo

RUN adduser --disabled-password --gecos '' $USER
RUN adduser $USER sudo

RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

WORKDIR /usr/src/app

RUN chown -R $USER:$USER /usr/src/app

COPY --chown=$USER:$USER app.py .
COPY --chown=$USER:$USER requirements.txt .
COPY --chown=$USER:$USER templates ./templates

#RUN python3 -m venv .venv
#RUN . .venv/bin/activate

RUN sudo pip3 install -r requirements.txt

# USER docker

RUN chown -R $USER:$USER /usr/src/app

RUN sudo flask db init
RUN sudo flask db migrate
RUN sudo flask db upgrade

RUN chown -R $USER:$USER /usr/src/app

USER $USER

EXPOSE 5000

CMD [ "flask", "run", "--host=0.0.0.0", "--port=5000"]
