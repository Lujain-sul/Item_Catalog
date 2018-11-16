# Item Catalog
## Table of Contents

* [Instructions](#instructions)
* [Contributing](#contributing)

## Instructions

1. About the project

The project uses flask framework and SQLAlchemy to implement CRUD functionalities on item catalog, it uses Google OAuth2.0 to implement authentication & authorization service. It also implements a JSON endpoint to represents all categories along with associated items.


2. Prerequisites

- python3
- VirtualBox
- Vagrant
- Virtual Machine (VM) https://github.com/udacity/fullstack-nanodegree-vm

3. How to run the application

- cd to vagrant folder inside VM
- run `vagrant up`
- run `vagrant ssh`
- run `cd /vagrant`
- run `pip3 install flask`
- run `pip3 install SQLAlchemy`
- run `pip3 install --upgrade oauth2client`
- run `python3 database_setup.py` to create catalog.db database
- run `python3 load_data.py` to insert some data to catalog.db
- run `python3 application.py` to start the server
- visit the application at http://localhost:5000/catalog


## Contributing

This project is built in the fulfillment of Udacity Full Stack Nano Degree requirement, pull requests will not be merged to this project.
