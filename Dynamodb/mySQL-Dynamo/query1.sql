CREATE VIEW imdb.movies AS
    SELECT tp.tconst,
           tp.ordering,
           tp.nconst,
           tp.category,
           tp.job,
           tp.characters,
           tb.titleType,
           tb.primaryTitle,
           tb.originalTitle,
           tb.isAdult,
           tb.startYear,
           tb.endYear,
           tb.runtimeMinutes,
           tb.genres,
           nm.primaryName,
           nm.birthYear,
           nm.deathYear,
           nm.primaryProfession,
           tc.directors,
           tc.writers
    FROM imdb.title_principals tp
    LEFT JOIN imdb.title_basics tb ON tp.tconst = tb.tconst
    LEFT JOIN imdb.name_basics nm ON tp.nconst = nm.nconst
    LEFT JOIN imdb.title_crew tc ON tc.tconst = tp.tconst;