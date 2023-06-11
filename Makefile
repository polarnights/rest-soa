PYTHON := PYTHONPATH=./src/ python3.9

server:
	${PYTHON} src/server

worker:
	${PYTHON} src/worker

install:
	apt-get install -y python3.9 python3.9-dev python-dev pip

requirements:
	python3.9 -m pip install .

run_rabbit_mq_worker_and_server:
	rabbitmq-server –detached &
	rabbitmq-plugins enable rabbitmq_management &
	bash -c "while ! curl -s localhost:15672 > /dev/null; do echo waiting for rabbitmq; sleep 3; done;"
	rabbitmqctl add_user username username
	rabbitmqctl set_user_tags username administrator
	rabbitmqctl set_permissions -p / username ".*" ".*" ".*"
	make worker &
	make server
