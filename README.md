# Meeting Room booking app
Create and book a meeting room.

## Using Docker for dev environment
Build the project:

`docker-compose build`

Run the project:

`docker-compose up`

### Running migrations, tests and linter with Docker
Enter the web app's Docker container:

`docker exec -it meetings bash`

Run database migrations:

`python manage.py migrate`

Run tests:

`coverage run manage.py test`

Run linter:

`flake8`

There is an option to use the Black formatter for code styling.

## Authentication and Authorization

To get the auth token send a POST request with user credentials to 
the following endpoint:

`api-token-auth/`

Example data for such POST request:
```
{
    "username": "admin",
    "password": "xxxxxxxx"
}
```

All further endpoints require Token Authentication, therefore make sure to 
include the following header in each request:

`Authorization:Token xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`


## Other Endpoints

* ### Users

    `/api/users/`

    Accepts `GET` and `POST` requests.

    Retrieves a list of existing users or allows to create new 
user instances. 

    Example data for creating a new user:
    ```
    {
        "username": "JD",
        "first_name": "John",
        "last_name": "Doe",
        "email": "jd@example.com"
    }
    ```
    `api/users/{id}/`

    Accepts `GET, PUT, PATCH, DELETE` requests.

    Retrieve, update or delete specific user instances.

* ### Meeting Rooms

    `/api/rooms/`

    Accepts `GET` and `POST` requests.

    Retrieves a list of existing meeting rooms or allows to create new 
reservation instances to existing reservations.

    To create a room only a title is required, e.g.:
    ```
    {
        "title" : "Game Room"
    }
    ```
    `api/rooms/{id}/`

    Accepts `GET, PUT, PATCH, DELETE` requests.

    Retrieve, update or delete specific room instances.

    Accepts a `user_id` parameter to filter reservations where a user is either
    a creator or an invitee.

* ### Reservations

    `/api/reservations/`

    Accepts `GET` and `POST` requests.

    Retrieves a list of existing reservations or allows to create new 
reservation instances to existing reservations. Multiple invitations can 
be created by providing the user id.

    Data example for creating a new reservation with two invitations:
    ```
        {
            "title": "Team Agile Best Practices",
            "from_date": "2021-03-17T16:00:00Z",
            "to_date": "2021-03-17T17:00:00Z",
            "room": 1,
            "creator": 1,
            "guests": [
                {
                    "invitee": 2
                },
                {
                    "invitee": 3
                }
            ]
        }
    ```
    `api/reservations/{id}/`

    Accepts `GET, PUT, PATCH, DELETE` requests.

    Retrieve, update or delete specific reservation instances.

    Accepts a `user_id` parameter to filter reservations where a user is either
    a creator or an invitee.

## Additional Notes

* Docker-compose uses .env.dev file for some settings, such as:
DJANGO_SECRET_KEY, DEBUG and SENTRY_URL.

* Running development environment is also possible with Pipenv, however the database
and env variables should be configured accordingly in this case.

* Filtering by `user_id` parameter is set for both the `reservations` and `rooms`
endpoints, the exact requirement was not fully clear to me. 
The two querysets differ only slightly, the one for room filtering using `distinct()`.

* I probably went a little overboard with the update method for the `reservations` 
endpoint, especially with invitation updates, which was not required in the task,
but it seemed interesting to try :)

* There is some basic logging set up, which tracks what data is validated and passed
into queries. Also Sentry is connected to track errors. 

* All tests are run in Circle CI before Github.