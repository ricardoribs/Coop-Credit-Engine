setup:
	pip install -r requirements.txt

test:
	pytest tests/

format:
	black src/ dags/

run:
	docker-compose up --build

clean:
	docker-compose down -v