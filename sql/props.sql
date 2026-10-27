-- Props catalog for the planner. Run once in a Snowsight worksheet,
-- then load backend/data/props.csv into it (Data > Add Data > Load data into a table).
-- The backend reads this table when Snowflake is configured and falls back to the CSV otherwise.

CREATE DATABASE IF NOT EXISTS HAUNTED_HOUSE;

CREATE TABLE IF NOT EXISTS HAUNTED_HOUSE.PUBLIC.PROPS (
    name STRING,
    category STRING,
    theme STRING,      -- room keyword the prop fits (see ROOM_THEMES in catalog.py), or 'any'
    price NUMBER(10, 2)
);

-- Sanity check after loading
SELECT theme, COUNT(*) AS props, MIN(price) AS cheapest, MAX(price) AS priciest
FROM HAUNTED_HOUSE.PUBLIC.PROPS
GROUP BY theme
ORDER BY theme;
