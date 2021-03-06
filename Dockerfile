FROM python:3.8
WORKDIR /foodgram
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
CMD bash -c "python3 manage.py collectstatic --no-input && gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000"
