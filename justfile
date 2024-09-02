# just is a handy way to save and run project-specific commands.
# This justfile contains a set of common commands you might
# find helpful while working on Coach

# just installation docs: https://just.systems/man/en/chapter_4.html

# If you use VScode, the following justfile syntax highlight extension might be useful:
# https://marketplace.visualstudio.com/items?itemName=kokakiwi.vscode-just

################################################
################# ENVIRONMENT
################################################

# Builds the docker images with optional additional arguments.
# Usage: just build [ARGS="..."]
# Example: just build --no-cache
build ARGS='':
    docker compose build {{ARGS}}

# Starts the docker containers with optional additional arguments.
up ARGS='':
    docker compose up {{ARGS}}

# Stops the docker containers and removes containers & networks created by `up`.
down:
    docker compose down

# Forces a stop of the running docker containers.
kill:
    docker compose kill

# Force restart and rebuild
reset:
    docker compose down && docker compose kill && docker compose build && docker compose up

# Attaches the current shell to the logs of the specified container.
# If no ARGS are provided, all container logs are displayed
logs ARGS='':
    docker compose logs -f {{ARGS}}

# Installs and sets up pre-commit hooks in the local repository.
setup-pre-commit:
    pip install pre-commit && pre-commit install && cd frontend/ && yarn install && cd ..

# Manually runs the pre-commit hooks on the staged files in the git repository.
run-pre-commit:
    bash .git/hooks/pre-commit

# Removes ALL CONTAINERS & VOLUMES in your local docker environment
# Remember to run `just make-db` after the migrations finish
[confirm("Hit [y] to run a hard-reset. This will remove your database from Coach. Be sure to rebuild and run `just make-db` afterwards.")]
hard-reset:
    docker compose down && docker compose kill | docker system prune -fa --volumes && docker volume rm slack-moderation_pg-data && docker compose build --no-cache && docker compose up

[confirm("Hit [y] to remove all volumes. This clears a lot of space but will erase your local data. You'll need to run a `just build` and `just make-db` afterwards.")]
clean-all-volumes:
    docker compose down && docker volume rm $(docker volume ls -q)

################################################
################# DATABASE
################################################

# Takes down the project and removes the Docker volume containing
# the Coach database data.
drop-db:
    docker compose down && docker volume rm slack-moderation_pg-data

# Creates Django migrations:
makemigrations APP='':
    docker compose exec django python manage.py makemigrations {{APP}}

# Runs pending Django migrations:
migrate APP='' NUMBER='':
    docker compose exec django python ./manage.py migrate {{APP}} {{NUMBER}}

################################################
################# BACKEND
################################################

# Runs Django tests. If no ARGS are specified, all tests are executed
test ARGS='':
    docker compose exec django python manage.py test {{ARGS}}

# Creates a shell
bash:
    docker compose exec django bash

# Creates a django shell
shell:
    docker compose exec django python manage.py shell

# Runs a Django manage.py command
manage ARGS='':
    docker compose exec django python manage.py {{ARGS}}

# Attach to paused process in Django container by default
attach CONTAINER='slack-moderation-slack-moderation-1':
    docker attach {{CONTAINER}}
