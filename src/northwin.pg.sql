create table users ( id serial not null, name varchar(100) not null, age int not null, status boolean not null default false , addedat TIMESTAMP not null default CURRENT_TIMESTAMP, addedby varchar(200) not null default CURRENT_USER, updatedat TIMESTAMP null, updatedby varchar(200) null, primary key(id) );


create table UserAuths(
    id SERIAL not null,
    username VARCHAR(100) not null,
    password_hash VARCHAR(100) not null,
    active BOOLEAN not null DEFAULT false,
    addedon TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    addedby VARCHAR(100) not null DEFAULT CURRENT_USER,
    updatedat TIMESTAMP NULL,
    updatedby VARCHAR NULL,
    PRIMARY KEY(id)
)