VERSIONS=0.1
NAME=pose2appliance
API_KEY=sample
VIDEO_PATH=/dev/video0


build:
	docker build -t ${NAME}:${VERSIONS} .

run: 
	docker run -d -e "API_KEY=${API_KEY}" \
	--device="${VIDEO_PATH}:/dev/video0" \
	--name ${NAME} \
	${NAME}:${VERSIONS} 

stop:
	docker stop ${NAME}
	docker rm ${NAME}

log:
	docker logs -f ${NAME}