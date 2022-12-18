# Custom Superset build to add apache pinot driver
# Gary A. Stafford (2022-09-25)
# Updated: 2022-12-18

FROM apache/superset:66138b0ca0b82a94404e058f0cc55517b2240069

# Switching to root to install the required packages
USER root

# Find which driver you need based on the analytics database:
# https://superset.apache.org/docs/databases/installing-database-drivers
RUN pip install mysqlclient psycopg2-binary pinotdb

# Switching back to using the `superset` user
USER superset