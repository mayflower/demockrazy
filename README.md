# demockrazy

A simple, token based voting system, focusing on anonymity for the participants


# Setup

clone the repository

## on nixOS
in root directory

run `nix-shell`


run `./manage.py makemigrations`

run `./manage.py migrate`

run `./manage.py runserver`


app can be found on localhost, port 8000

## on other distributions

install django dependency

run `pip3 install --user django==2.2.27`


run `./manage.py makemigrations`

run `./manage.py migrate`

run `./manage.py runserver`


app can be found on localhost, port 8000
