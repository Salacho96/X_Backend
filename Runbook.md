# Prerequisites
- Docker >= 25
- Docker Compose >= 2
- Git

# Clone the repository
git clone https://github.com/Salacho96/X_Backend.git
cd X_Backend

# Setup environment variables
# .env is not included in the repo for security reasons
# Copy the example file and use it as is - default values work out of the box
cp .env.example .env

# Run the containers (this installs all dependencies automatically)
docker-compose up --build

# In another terminal, apply migrations
docker-compose exec backend python manage.py makemigrations users
docker-compose exec backend python manage.py makemigrations tweets
docker-compose exec backend python manage.py makemigrations search
docker-compose exec backend python manage.py migrate

# Run tests
docker-compose exec backend pytest tests/ -v

# Run tests with coverage
docker-compose exec backend pytest tests/ -v --cov=apps --cov-report=term-missing

# API documentation
http://localhost:8000/api/docs/

# Example credentials (after running migrations)
email: prueb2@prueba.com
password: twitterpassword