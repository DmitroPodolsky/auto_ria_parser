from datetime import datetime

import psycopg2
from loguru import logger
from psycopg2.extras import execute_values

from app.config import settings


class Manager:
    """Class for managing database connection and data"""

    def __init__(self):
        """Initialize database connection and create table if not exists"""

        self.connection = psycopg2.connect(
            database=settings.POSTGRESS_DATABASE,
            user=settings.POSTGRESS_USER,
            password=settings.POSTGRESS_PASSWORD,
            host=settings.POSTGRESS_HOST,
            port=settings.POSTGRESS_PORT,
        )

        logger.info("Database connection established")

        self.create_table()

    def create_table(self):
        """Create table if not exists"""

        cursor = self.connection.cursor()
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS car_data (
                url VARCHAR(255),
                title VARCHAR(255),
                price_usd INTEGER,
                odometer INTEGER,
                username VARCHAR(255),
                image_url VARCHAR(255),
                images_count INTEGER,
                car_number VARCHAR(255),
                car_vin VARCHAR(255),
                datetime_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        cursor.execute(create_table_sql)
        self.connection.commit()
        cursor.close()

        logger.info("Table created")

    def insert_data(self, values: list[tuple]):
        """Insert data into table
        :param values: list of tuples with data
        """

        cursor = self.connection.cursor()
        execute_values(
            cursor,
            "INSERT INTO car_data (url, title, price_usd, odometer, username, image_url, images_count, car_number, car_vin) VALUES %s",
            values,
        )
        self.connection.commit()
        cursor.close()

        logger.info("Data inserted")

    def dump_data(self):
        """Dump data from table to sql file"""

        cursor = self.connection.cursor()

        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dump_filename = settings.DATA / f"dump_{current_date}.sql"

        with open(dump_filename, "w", encoding="utf-8") as file:
            cursor.execute("SELECT * FROM car_data")
            column_names = []

            columns_descr = cursor.description

            for column_name in columns_descr:
                column_names.append(column_name[0])

            insert_prefix = "INSERT INTO car_data (%s) VALUES " % (
                ", ".join(column_names)
            )
            rows = cursor.fetchall()

            row_data = ",\n".join(
                "("
                + ", ".join(
                    "'%s'" % str(value) if isinstance(value, datetime) else repr(value)
                    for value in data
                )
                + ")"
                for data in rows
            )

            file.write("{}\n{};\n".format(insert_prefix, row_data))

            logger.success("Data dumped")

            cursor.execute("DELETE FROM your_table_name")
            self.connection.commit()
            logger.success("Data from table deleted")
