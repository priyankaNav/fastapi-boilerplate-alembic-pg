.PHONY: alembic-init prepare-env update-alembic-config auto-generate-schema run-migrations migrate

# Path to Alembic configuration and environment files
ALEMBIC_INI := alembic.ini
ALEMBIC_ENV_PY := alembic/env.py

# Database URL
DATABASE_URL := postgresql://postgres:typeface2024@db:5432/dropbox-equivalent-db

alembic-init:
	docker-compose run web alembic init alembic
# Modify env.py to include the Base import and update target_metadata using awk for compatibility
prepare-env:
	@{ echo "from db.base import Base"; cat $(ALEMBIC_ENV_PY); } > temp_env.py && mv temp_env.py $(ALEMBIC_ENV_PY)
	@awk '/target_metadata = None/ { print "target_metadata = Base.metadata"; next }1' $(ALEMBIC_ENV_PY) > temp_env.py && mv temp_env.py $(ALEMBIC_ENV_PY)

# Update the sqlalchemy.url in alembic.ini to the DATABASE_URL
update-alembic-config:
	@sed -i '' 's|sqlalchemy.url =.*|sqlalchemy.url = $(DATABASE_URL)|' $(ALEMBIC_INI) || sed -i 's|sqlalchemy.url =.*|sqlalchemy.url = $(DATABASE_URL)|' $(ALEMBIC_INI)

# Run Alembic migrations within the Docker container
auto-generate-schema:
	docker-compose run web alembic revision --autogenerate -m "Initial migration"
run-migrations:
	docker-compose run web alembic upgrade head

# Main target to run all tasks
migrate: alembic-init prepare-env update-alembic-config auto-generate-schema run-migrations
