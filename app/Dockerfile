FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY requirements.txt /app

# flask、uwsgiをインストール
RUN pip install -r /app/requirements.txt

COPY . /app
