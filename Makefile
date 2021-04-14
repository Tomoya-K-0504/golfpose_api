NAME=app_nginx_uwsgi
LOCAL_NAME=local_uwsgi

LOCATION=asia-northeast1
REGION=$(LOCATION)
PROJECT_ID := $(shell grep \"project_id\"\: app/gcp_all.json | sed -e 's/  "project_id\"\: "//g' | sed -e 's/\"\,//g')
REPOSITORY=easy-uwsgi2
MODEL_NAME=easy_uwsgi2
SOURCE_IMAGE=$(NAME)
TARGET_IMAGE=app_nginx_uwsgi
IMAGE_TAG=$(LOCATION)-docker.pkg.dev/$(PROJECT_ID)/$(REPOSITORY)/$(NAME)
SOURCE_BUCKET=app_source_bucket
ACCESS_TOKEN := $(shell gcloud auth print-access-token)
VERSION_NAME=v5


echo:
	echo $(IMAGE_TAG)


gc_vm:
	# gcloud compute instances delete $(REPOSITORY) --zone $(REGION)-c
	# gcloud compute instances create-with-container $(REPOSITORY) \
	# 	--container-image $(IMAGE_TAG) --accelerator type=nvidia-tesla-t4 \
	# 	--tags http-server --zone $(REGION)-c --boot-disk-size 20GB \
	# 	--preemptible 
	gcloud compute instances create-with-container $(REPOSITORY) \
		--container-image $(IMAGE_TAG) \
		--tags http-server --zone $(REGION)-c --boot-disk-size 20GB \
		--preemptible 
	# gcloud compute firewall-rules create allow-http --preemptible \
 	# 	--allow tcp:80 --target-tags http-server

to_gcs:
	zip -r app.zip ./
	gsutil cp app.zip gs://$(SOURCE_BUCKET)/

build:
	docker build -t $(NAME) .
	# docker build -f Dockerfile -t $(NAME) .

run:
	docker stop $(LOCAL_NAME)
	docker rm $(LOCAL_NAME)
	docker run -d -p 80:80 --name=$(LOCAL_NAME) $(NAME)
	# docker run -d --name=$(LOCAL_NAME) --net=host $(NAME)

attach:
	docker attach $(LOCAL_NAME) --sig-proxy=false

gc_repo:
	gcloud beta artifacts repositories create $(REPOSITORY) \
		--repository-format=docker \
		--location=$(REGION)

gc_push:
	gcloud auth configure-docker $(REGION)-docker.pkg.dev
	docker tag $(SOURCE_IMAGE) $(IMAGE_TAG)
	docker push $(IMAGE_TAG)

gc_model:
	# gcloud beta ai-platform models create $(MODEL_NAME) \
	# 	--region=$(REGION) \
	# 	--enable-logging \
	# 	--enable-console-logging
	gcloud beta ai-platform versions create $(VERSION_NAME) \
		--region=$(REGION) \
		--model=$(MODEL_NAME) \
		--machine-type=n1-standard-4 \
		--image=$(IMAGE_TAG) \
		--ports=80 \
		--health-route=/healthz \
		--predict-route=/predict \
		--python-version=3.7

gc_health:
	curl -X POST \
		-H "Authorization: Bearer $(ACCESS_TOKEN)" \
		-d "file_path=gs://tuto1/short_video.mp4" \
		https://$(REGION)-ml.googleapis.com/v1/projects/$(PROJECT_ID)/models/$(MODEL_NAME)/versions/$(VERSION_NAME):predict

gc_cbuild:
	gcloud builds submit --config cloudbuild.yaml ./app