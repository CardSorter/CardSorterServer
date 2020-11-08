FROM python:3.6.12

ENV GROUP_ID=1000 \
    USER_ID=1000

WORKDIR /var/www

COPY ./flaskr .
COPY wsgi.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r ./requirements.txt

# WSGI
RUN pip install gunicorn

# Add the new user
RUN addgroup --gid $GROUP_ID www
RUN adduser --uid $USER_ID --ingroup www www --shell /bin/sh

USER www

EXPOSE 5000

# Regargind the workers: https://docs.gunicorn.org/en/stable/design.html#how-many-workers
# (2 x $num_cores) + 1
CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "wsgi"]

# CMD ["python", "dev.py"]