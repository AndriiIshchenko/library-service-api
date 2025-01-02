# Libray Service API


App for managing library/

## Technology Stack

- **Backend:** Python 3.13, Django 4.x, Django REST Framework
- **Database:** PostgreSQL
- **Others:** Stripe, JWT, Celery, Redis, Docker, Click, Pillow, PyYAML, psycopg2, pyflakes, pytz


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Must have:
- a computer with some operating system 
- some free time

### System Requirements

- Python
- pip (Python package installer)
- Docker


### Installing

A step by step series of examples that tell you how to get a development env running

1. Clone the repository:
    ```
    git clone the-link-from-forked-repo
    ```
2. Open the project folder in your IDE
   
3. If you are using PyCharm - it may propose you to automatically create venv for your project and install requirements in it, but if not:
    ```
    python -m venv venv
    venv\Scripts\activate (on Windows)
    source venv/bin/activate (on macOS)
    pip install -r requirements.txt
    ```
3. Use .env.example to configure the environment.

4. Run with Docker.
    ```
    docker compose up --build
    ```
    App will be available at 127.0.0.1:8001

5. You can use test db/
    ```
    docker exec -it <container_name> python manage.py loaddata library_test_db.json 
    ```

6. Creating superuser:
    ```
    docker exec -it <container_name>  createsuperuser
    ```
    Or use:
    ```
    andrew@andrew.com
    andrew
    ```

## Permissions
    - Unauthorized users can get access to books list.
    - Authorized users can borrow books.
    - Admin user can return books.
    
## Scheduling

    Celery is used for sending notifications about overdue borrowings via Telergam each day at 9 pm.
    Check every minute for expired payments.  
  

## API Endpoints

Major endpoints for interacting with the application:

    Books:
      - `/api/books/` - List of books only admin can add books.
      - `/api/books/<id>/` - Manage book for admin.
    Borrowings:
      - `/api/borrowings/` - List of borrowings, search by user_id, book_id, is_active.
      - `/api/borrowings/notify-overdue/` - admin only notify actual overdue boorrowings via telegram
      - `/api/borrowings/<id>/' - detail book
      - `/api/borrowings/<id>/return-book' - admin only return  book create Payment object and Stripe session
      - `/api/borrowings/<id>/actual_payment'  - refresh expired payments
    Payments:
      - `/api/payments/` - List of payments.
      - `/api/payments/<id>/' - Manage payment.
      - `/api/payments/<id>/success'   - Successful payment update payment
     
  
    User:
      - `/api/user/register/` - Register a new user .
      - `/api/user/token/` - Obtain token pair.
      - `/api/user/token/refresh/` - Actualize your access token with refresh token .
      - `/api/user/token/verify/` - Verify token if it is valid.
      - `api/user/me/` - Manage your profile details.
      - `api/user/logout/` - Logout (deactivate refresh token).
      
### Swagger API

- `/api/doc/swagger/`

### Redoc API

- `/api/doc/redoc/`
