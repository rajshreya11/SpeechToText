
from sqlalchemy import text
from database import engine

try:
    # Connect to PostgreSQL
    with engine.connect() as connection:

        # Execute a test query
        result = connection.execute(
            text("SELECT version()")
        )

        print("PostgreSQL Connected Successfully!")

        # Display PostgreSQL version
        print(result.scalar())

except Exception as error:

    print("Connection Failed!")
    print(error)
