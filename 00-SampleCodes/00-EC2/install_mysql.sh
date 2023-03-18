#!/bin/bash -ex
sudo su
rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2022
rpm -Uvh https://repo.mysql.com/mysql80-community-release-el7-3.noarch.rpm
yum install -y mysql-community-server
systemctl enable mysqld
systemctl start mysqld
export DbMasterPassword=Password@123
export DbMasterUsername=dbuser
mysql -u root "-p$(grep -oP '(?<=root@localhost\: )\S+' /var/log/mysqld.log)" -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${DbMasterPassword}'" --connect-expired-password
mysql -u root "-p${DbMasterPassword}" -e "CREATE USER '${DbMasterUsername}' IDENTIFIED BY '${DbMasterPassword}'"
mysql -u root "-p${DbMasterPassword}" -e "GRANT ALL PRIVILEGES ON *.* TO '${DbMasterUsername}'"
mysql -u root "-p${DbMasterPassword}" -e "FLUSH PRIVILEGES"
cd /var/lib/mysql-files/
wget https://datasets.imdbws.com/name.basics.tsv.gz
wget https://datasets.imdbws.com/title.akas.tsv.gz
wwget https://datasets.imdbws.com/title.basics.tsv.gz
wwget https://datasets.imdbws.com/title.crew.tsv.gz
wwget https://datasets.imdbws.com/title.episode.tsv.gz
wwget https://datasets.imdbws.com/title.principals.tsv.gz
wwget https://datasets.imdbws.com/title.ratings.tsv.gz
wgzip -d *.gz
curl -O https://www.amazondynamodblabs.com/static/rdbms-migration/rdbms-migration.zip
unzip -q rdbms-migration.zip
chmod 775 *.*
mysql -u root "-p${DbMasterPassword}" -e "CREATE DATABASE imdb;"
mysql -u root "-p${DbMasterPassword}" -e "CREATE TABLE imdb.title_akas (titleId VARCHAR(200), ordering VARCHAR(200),title VARCHAR(1000), region VARCHAR(1000), language VARCHAR(1000), types VARCHAR(1000),attributes VARCHAR(1000),isOriginalTitle VARCHAR(5),primary key (titleId, ordering));"
mysql -u root "-p${DbMasterPassword}" -e "CREATE TABLE imdb.title_basics (tconst  VARCHAR(200), titleType  VARCHAR(1000),primaryTitle  VARCHAR(1000), originalTitle  VARCHAR(1000), isAdult  VARCHAR(1000), startYear  VARCHAR(1000),endYear  VARCHAR(1000),runtimeMinutes  VARCHAR(1000),genres  VARCHAR(1000),primary key (tconst));"
mysql -u root "-p${DbMasterPassword}" -e "CREATE TABLE imdb.title_crew (tconst  VARCHAR(200), directors  VARCHAR(1000),writers  VARCHAR(1000),primary key (tconst));"
mysql -u root "-p${DbMasterPassword}" -e "CREATE TABLE imdb.title_principals (tconst  VARCHAR(200), ordering  VARCHAR(200),nconst  VARCHAR(200), category  VARCHAR(1000), job  VARCHAR(1000), characters  VARCHAR(1000),primary key (tconst,ordering,nconst));"
mysql -u root "-p${DbMasterPassword}" -e "CREATE TABLE imdb.title_ratings (tconst  VARCHAR(200), averageRating float,numVotes  integer,primary key (tconst));"
mysql -u root "-p${DbMasterPassword}" -e "CREATE TABLE imdb.name_basics (nconst  VARCHAR(200), primaryName  VARCHAR(1000),birthYear  VARCHAR(1000), deathYear  VARCHAR(1000), primaryProfession  VARCHAR(1000), knownForTitles VARCHAR(1000),primary key (nconst));"
mysql -u root "-p${DbMasterPassword}" -e "LOAD DATA INFILE '/var/lib/mysql-files/title_ratings.tsv' IGNORE INTO TABLE imdb.title_ratings FIELDS TERMINATED BY '\t';"
mysql -u root "-p${DbMasterPassword}" -e "LOAD DATA INFILE '/var/lib/mysql-files/title_basics.tsv'  IGNORE INTO TABLE imdb.title_basics FIELDS TERMINATED BY '\t';"
mysql -u root "-p${DbMasterPassword}" -e "LOAD DATA INFILE '/var/lib/mysql-files/title_crew.tsv' IGNORE INTO TABLE imdb.title_crew FIELDS TERMINATED BY '\t';"
mysql -u root "-p${DbMasterPassword}" -e "LOAD DATA INFILE '/var/lib/mysql-files/title_principals.tsv' IGNORE INTO TABLE imdb.title_principals FIELDS TERMINATED BY '\t';"
mysql -u root "-p${DbMasterPassword}" -e "LOAD DATA INFILE '/var/lib/mysql-files/name_basics.tsv' IGNORE INTO TABLE imdb.name_basics FIELDS TERMINATED BY '\t';"
mysql -u root "-p${DbMasterPassword}" -e "LOAD DATA INFILE '/var/lib/mysql-files/title_akas.tsv' IGNORE INTO  TABLE imdb.title_akas FIELDS TERMINATED BY '\t';"