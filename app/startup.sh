#!/bin/bash

# アプリケーションディレクトリに移動
cd /var/app

# uwsgi起動
# TODO: rootで動かさない方が良いですよ。というWarningが出るので、ちゃんと uid 等を指定した方が良い
uwsgi --socket 127.0.0.1:8080 --chdir /var/app/ --wsgi-file app.py --callable app --master --processes 4 --threads 2 & 

# nginx起動
nginx -g "daemon off;"
