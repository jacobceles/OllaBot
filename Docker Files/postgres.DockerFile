FROM postgres:17
WORKDIR /Postgres
COPY  /Init_Files/*  /docker-entrypoint-initdb.d/
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_USER=strawhat
ENV POSTGRES_DB=OPSchool