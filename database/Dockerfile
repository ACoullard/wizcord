FROM mongo:7.0

ENV MONGO_INITDB_ROOT_USERNAME=admin
ENV MONGO_INITDB_ROOT_PASSWORD=password
ENV MONGO_INITDB_DATABASE=mydatabase

# Expose the default MongoDB port
EXPOSE 27017

# Create a directory for data persistence
RUN mkdir -p /data/db

# Set volume for data persistence
VOLUME ["/data/db"]

# # Copy custom configuration file (optional)
# COPY mongod.conf /etc/mongod.conf

# Set the command to run MongoDB with the custom config
# CMD ["mongod", "--config", "/etc/mongod.conf"]
CMD ["mongod"]