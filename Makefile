BASE_IMAGE=nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04
LOCAL_NAME=$(gpu)

REPOSITORY=easy-uwsgi2
MODEL_NAME=easy_uwsgi2
SOURCE_IMAGE=$(NAME)
TARGET_IMAGE=app_nginx_uwsgi


build:
	docker build -t $(NAME) ./app
	# docker build -f Dockerfile -t $(NAME) ./app

run:
	docker stop $(LOCAL_NAME)
	docker rm $(LOCAL_NAME)
	docker run -d -p 80:80 --gpus 1 --name=$(LOCAL_NAME) $(NAME)
	# docker run -d --name=$(LOCAL_NAME) --net=host $(NAME)

exec:
	docker exec -it gpu /bin/bash

attach:
	docker attach $(LOCAL_NAME) --sig-proxy=false

from_gpu_image:
	docker run -it --name $(NAME) -v $(pwd):/app -p 80:80 --gpus 1 $(BASE_IMAGE) /bin/bash