# Image tag gallery

> Most simple ever self-hosted image gallery that allows to add multiple tags to images when they are uploaded.

![homepage](https://raw.githubusercontent.com/slavid/image-tag-gallery/main/resources/homepage.png)

Features
--------

-   **Image Upload:** Users can upload images from their device and assign tags to them.
-   **Image Tagging:** Each image can have one or more tags assigned to facilitate searching.
-   **Tag-based Search:** Users can search for images by tags and view all images associated with a specific tag and search multiple tags at once which will show only images containing all tags.
-   **Image Gallery:** The application provides a gallery where all uploaded images, along with their corresponding tags, can be viewed.

## Acknowledgements

On March 6th, 2024, I embarked on the journey of creating this project with the **assistance of AI technology** provided by `OpenAI` (also known as `ChatGPT`) and Google's `Gemini` (formerly known as `Bard`). Even this README is being written with the assistance of AI. The project aims to provide a platform for managing images with tags and URLs efficiently. Throughout the development process, various technologies and frameworks were utilized to bring this vision to life. Special thanks to the following:

-   The Flask framework for web development in Python.
-   SQLAlchemy for the database integration.
-   Bootstrap for the front-end design.
-   **OpenAI for providing AI assistance in the development process.**

Manual Installation
------------

1.  Clone this repository to your local machine:

```bash
$ git clone https://github.com/slavid/image-tag-gallery.git
```

2.   Navigate to the project directory:

```bash
$ cd image-tag-gallery
```
3. Use local virtual environment (venv):

```bash
$ python3 -m venv .venv
$ . .venv/bin/activate
```
4. Install dependencies using pip:

```bash
$ pip3 install -r requirements.txt
```

5. Init flask database:

```bash
$ flask db init
$ flask db migrate
$ flask db upgrade
```

6. Start the application:
```bash
$ flask run
```
---

- This will create a database by default at `./instance/` called `tags.db`.
- CSS located at `./static/css/styles.css`
- Images uploaded to `./static/uploads.`

Docker Installation
------------

Either use `docker run` or `docker compose`:

- Docker run:

```bash
$ docker run --rm -it -d -p 5000:5000 \ 
-v /local/backup/of/images/:/app/static/uploads \
--name image-tag-gallery \
draz1c/image-tag-gallery:latest
```

- Docker compose
```yaml
---
version: "3"
services:
  image-tag-gallery:
    image: draz1c/image-tag-gallery:latest
    container_name: image-tag-gallery
    volumes:
      - '/local/backup/of/images/:/app/static/uploads'
    ports:
      - 5000:5000
    restart: always
```

Usage
-----

1.  Open your web browser and go to http://localhost:5000 (or http://127.0.0.1:5000).
2.  Upload an image from your device and assign tags as needed.
3.  Explore the image gallery and search for images by tags.

## Backup data

I can't seem to be able to mount `/app` as a bind mount as I would normally do with other docker containers because that just overrides the content of `/app` and thus makes it not working (I wonder if this has something to do with [**s6-overlay**](https://github.com/just-containers/s6-overlay) and I need to use it...).

So I'm using a script to get the location of the `Docker volume` in the host computer and with a daily cron jon run copy all the contents of the Docker volume:

The script to find the location (needs work)
```bash
#!/usr/bin/env bash

COMMAND=$(docker inspect -f '{{ .Mounts }}' image-tag-gallery | awk -F ' ' '{print $9}')

echo $COMMAND
```

Cronjob run under root (runs at 3 AM each day):

```bash
0 3 * * * cp -uR --no-preserve=mode,ownership $(/script/location.sh)/* \
/backup/folder/location/ && chown -R non-root-user:non-root-user \
/backup/folder/location/ >/dev/null 2>&1
```

## TODO

- [ ] Allow bind mount of the app's path: `/app`.
- [ ] Fix translations (while coding I've mixed Spanish and English everywhere).
- [ ] More pleasing interface (I'm definitely not a web designer).
- [ ] Fix script to find Docker volume to be more consistent.
- [ ] Chose a catchy project name
- [x] ~~Add some basic CI.~~

Contribution
------------

If you'd like to contribute to this project, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/new-feature`).
3.  Make your changes and commit them (`git commit -am 'Add new feature'`).
4.  Push your branch (`git push origin feature/new-feature`).
5.  Open a Pull Request.


## Version history

| **Date**   | **Version** | **Changes**     |
|:----------:|:-----------:|:---------------:|
| 03/08/2024 | 0.1         | Initial release |
| 03/16/2024 | 0.2         | Added restrictive search button and popup confirmation window upon trying to delete images|