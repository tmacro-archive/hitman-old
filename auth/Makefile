-include env_make
NS = tmacro
VERSION ?= latest

REPO = hitman
NAME = hitman
INSTANCE = dev
.PHONY: build push shell run start stop rm release

build:
	docker build -t $(NS)/$(REPO):$(VERSION) .

push:
	docker push $(REGISTRY)/$(NS)/$(REPO):$(VERSION)

shell:
	docker run --rm --name $(NAME)-$(INSTANCE) -i -t $(PORTS) $(VOLUMES) $(ENV) --entrypoint /bin/sh $(NS)/$(REPO):$(VERSION)

develop:
	docker run --rm --name $(NAME)-$(INSTANCE) -it --entrypoint /bin/sh $(PORTS) $(VOLUMES) $(ENV) $(NS)/$(REPO):$(VERSION)

run:
	docker run -it --rm --name $(NAME)-$(INSTANCE) $(PORTS) $(VOLUMES) $(ENV) $(NS)/$(REPO):$(VERSION)

start:
	docker run -d --name $(NAME)-$(INSTANCE) $(PORTS) $(VOLUMES) $(ENV) $(NS)/$(REPO):$(VERSION)

stop:
	docker stop $(NAME)-$(INSTANCE)

kill:
	docker kill $(NAME)-$(INSTANCE)

rm:
	docker rm $(NAME)-$(INSTANCE)

squash:
	docker save $(NS)/$(REPO):$(VERSION) | sudo docker-squash --verbose -t $(NS)/$(REPO):$(VERSION) | docker load

tag:
	docker tag $(NS)/$(REPO):$(VERSION) $(REGISTRY)/$(NS)/$(REPO):$(VERSION)

release: build
	make squash -e VERSION=$(VERSION)
	make tag -e VERSION=$(VERSION)
	make push -e VERSION=$(VERSION)

default: build
