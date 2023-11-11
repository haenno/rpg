FROM python:3.10-bullseye
ENV PYTHONUNBUFFERED 1
# check later 
# ENV PYTHONDONTWRITEBYTECODE 1
RUN /usr/local/bin/python -m pip install --upgrade pip
WORKDIR /srv/rpg
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ARG DJANGO_SUPERUSER_EMAIL
ARG DJANGO_SUPERUSER_PASSWORD
ARG DJANGO_SUPERUSER_USERNAME
RUN chmod +x start_drfjwt.sh
CMD ["sh", "start_rpg_prod.sh"]