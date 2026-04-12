First you should be able to clone the repository by running 
git clone https://github.com/Salacho96/X_Backend.git

tu run the containers
docker-compose up --build

to create migrations for user model run
docker-compose exec backend python manage.py makemigrations users

to create migrations for tweets model run
docker-compose exec backend python manage.py makemigrations tweets

to create migrations for search model run
docker-compose exec backend python manage.py makemigrations search  

to appply migrations run
docker-compose exec backend python manage.py migrate

to check tests coverage run
run docker-compose exec backend pytest tests/ -v --cov=apps --cov-report=term-missing

to check tests run 
docker-compose exec backend pytest tests/ -v

to check api swagger documentation check
http://localhost:8000/api/docs/

