FROM python:3.8
RUN mkdir /foodgram
COPY requirements.txt /foodgram
RUN pip install --upgrade pip && pip install -r /foodgram/requirements.txt
COPY . /foodgram
WORKDIR /foodgram
CMD bash -c "python3 manage.py collectstatic --no-input && gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000"
