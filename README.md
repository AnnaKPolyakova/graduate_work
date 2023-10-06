#  Ticket booking

It will be great to connect movies with going to the cinema. Not everyone likes to stay at home and
watch movies alone.
Sometimes you want to watch them with a company of like-minded people.
To implement this feature, a separate microservice was created using
where you can create events and book tickets for them.

[Research on db selection](research.md)

The following actions are available to users:
- cities: creation (deletion, change) with time zone indication
   (only available to superusers). View a list of cities (for all)
- places: events: creation (change, deletion, viewing) with
   indicating the address and city where they will be hosts. To view
   list you can filter by city
- events: creation (deletion, change) of an event indicating the collection location,
   film, possible number of participants. Events can be filtered by
   host, location, start date
- hosts: view the list of event organizers (hosts), including your own
   events (those whose events the request user attended) with the ability
   filtering by city
- blacklist: the host can add another user to the blacklist and
   then he will not be able to create a booking for his event
- ticket booking: registration for events (change of registration,
   deletion). The user or the host can delete their reservation. Can
   get all bookings (available filtering by user, event, host) or
   only your bookings (available filtering by host)

Sorting the issuance of objects:
Sorting is available by any fields of objects, or when requesting hosts -
sort by id

Restrictions:
- you cannot create an event for a past time and date
(taking into account time zones in different cities)
- you cannot register for an event if all places are already taken or
   it's already passed
- you cannot delete a city or event if there are related objects

Technologies and requirements:
```
Python 3.9+
flask
```
### Docker settings

##### Installation

* [Detailed Installation Guide](https://docs.docker.com/install/linux/docker-ce/ubuntu/)

### Docker-compose settings

##### Installation

* [Detailed Installation Guide](https://docs.docker.com/compose/install/)

### Running the application(

#### Before starting the project, create environment variables
Create a .env in the root and add the necessary variables to it
Example in .env.example - to run the entire application in docker
Example in .env.example-local - to run the application locally and partially in docker

#### Run entirely in docker containers: 

* `docker-compose up -d --build`

To stop the container:  
* `docker-compose down --rmi all --volumes`


#### Running the project partially in docker containers

* `docker-compose -f docker-compose-local.yml up -d --build`

To stop the container:  
* `docker-compose -f docker-compose-local.yml down --rmi all --volumes`


Documentation:

http://127.0.0.1:8000/v1/doc/redoc/
http://127.0.0.1:8000/v1/doc/swagger/


### Tests

#### Running tests partially in docker containers

* `docker-compose -f docker-compose-local.yml up -d --build`
* `pytest`

To stop the container:  
* `docker-compose -f docker-compose-local.yml down --rmi all --volumes`


#### Running tests in docker containers

* `docker-compose -f tests/functional/docker-compose-test.yml up -d --build`

To stop the container:  
* `docker-compose -f tests/functional/docker-compose-test.yml down --rmi all --volumes`

