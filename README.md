# Hope4Ever API

Backend API for the Hope4Ever platform.

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root with the following variables:
   ```
   APP_NAME="Hope4Ever API"
   ENV=dev
   DEBUG=true
   API_V1_PREFIX=/api/v1
   
   DB_HOST=your_database_host
   DB_PORT=your_database_port
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_NAME=your_database_name
   
   JWT_SECRET=your_jwt_secret
   JWT_ALG=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```
5. Run the migrations:
   ```bash
   alembic upgrade head
   ```
6. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Environment Variables

All configuration is loaded from environment variables. Create a `.env` file in the project root with the required variables.

## Database Migrations

This project uses Alembic for database migrations:

- Create a new migration: `alembic revision --autogenerate -m "migration message"`
- Apply migrations: `alembic upgrade head`
- Rollback migration: `alembic downgrade -1`

## Development

1. Make your changes
2. Run the tests
3. Create a pull request