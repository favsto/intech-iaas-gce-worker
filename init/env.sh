#!/usr/bin/env bash

# custom variables
echo DESTINATION_BUCKET="[bucket_name]" >> config
echo SQL_USERNAME="[your_sql_username]" >> config
echo SQL_PASSWORD="[your_sql_password]" >> config
echo SQL_CONNECTION_NAME=$(curl -s "http://metadata/computeMetadata/v1/instance/attributes/sql-connection-name" \
    -H "Metadata-Flavor: Google") >> config


# update env variables
echo export DESTINATION_BUCKET >> config
echo export SQL_USERNAME >> config
echo export SQL_PASSWORD >> config
echo export SQL_CONNECTION_NAME >> config