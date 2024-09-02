.PHONY: install all build start clean

all: install build run 
build:
	docker build ./fastapi_app/ -t poc/fastapi_app:latest
	docker build ./smoke/ -t poc/smoke:latest
run:
	docker compose -f docker-compose.yml up -d
	sleep 3
	docker compose -f docker-compose-sondas-1.yml up -d
	sleep 3 
	docker compose -f docker-compose-sondas-2.yml up -d
	sleep 3
clean:
	docker compose -f docker-compose.yml kill
	docker compose -f docker-compose.yml rm -f
	docker compose -f docker-compose-sondas-1.yml kill
	docker compose -f docker-compose-sondas-1.yml rm -f
	docker compose -f docker-compose-sondas-2.yml kill
	docker compose -f docker-compose-sondas-2.yml rm -f
	# docker images -f dangling=true|awk '{print $3}'|grep -v IMAGE|xargs -I ARGS docker image rm ARGS
	
install:
	if (docker plugin list|grep loki); then echo "ok - loki plugin installed"; else docker plugin install  grafana/loki-docker-driver:latest --alias loki --grant-all-permissions; fi
