# -- Вроде работает
# select p.driver_1, p.car_number , p.start_time, p.stop_time, array_agg(ce.event_date), count(coalesce (ce.event_date, null))  from ii.pls p
# inner join ii.can_events ce on p.car_number = ce.car_number and ce.event_date  between p.start_time and cast (coalesce(stop_time, '2024-01-22') as timestamp)
# where ce.event_date between cast('2024-01-15' as timestamp) and cast('2024-01-22' as timestamp)
# and not ( p.author_document <> p.author_document_change and p.stop_time isnull)
# group by p.driver_1 , p.car_number , p.start_time , p.stop_time
# ;
#
# -- теперь машины считаются вместе
# select p.driver_1, array_agg(distinct p.car_number), array_agg(ce.event_date), count(coalesce (ce.event_date, null))  from ii.pls p
# inner join ii.can_events ce on p.car_number = ce.car_number and ce.event_date  between p.start_time and cast (coalesce(stop_time, '2024-01-22') as timestamp)
# where ce.event_date between cast('2024-01-15' as timestamp) and cast('2024-01-22' as timestamp)
# and not ( p.author_document <> p.author_document_change and p.stop_time isnull)
# group by p.driver_1
# ;
#
# --yt gjkexbkjcm
# select p.driver_1,
# array_agg(distinct p.car_number),
# array_agg(ce.event_date),
# count(coalesce (ce.event_date, null)),
# sum(cast (coalesce(p.stop_time, '2024-01-22') as timestamp)- p.start_time),
# p.start_time,
# p.stop_time
# from ii.pls p
# inner join ii.can_events ce on p.car_number = ce.car_number and ce.event_date  between p.start_time and cast (coalesce(stop_time, '2024-01-22') as timestamp)
# where ce.event_date between cast('2024-01-15' as timestamp) and cast('2024-01-22' as timestamp)
# and not ( p.author_document <> p.author_document_change and p.stop_time isnull)
# group by p.driver_1
# , p.start_time,
# p.stop_time
# ;

import psycopg2

# Establish the connection to the database
conn = psycopg2.connect(database="YOUR_DB", user="YOUR_USER", password="YOUR_PASSWORD", host="YOUR_HOST",
                        port="YOUR_PORT")

cur = conn.cursor()

# Query 1
cur.execute("""
    SELECT p.driver_1, p.car_number , p.start_time, p.stop_time, array_agg(ce.event_date), count(coalesce (ce.event_date, null))  
    FROM ii.pls p 
    INNER JOIN ii.can_events ce ON p.car_number = ce.car_number AND ce.event_date  BETWEEN p.start_time AND cast (coalesce(stop_time, '2024-01-22') AS timestamp)
    WHERE ce.event_date BETWEEN cast('2024-01-15' AS timestamp) AND cast('2024-01-22' AS timestamp)
    AND NOT ( p.author_document <> p.author_document_change AND p.stop_time IS NULL)
    GROUP BY p.driver_1 , p.car_number , p.start_time , p.stop_time;
    """)
results1 = cur.fetchall()

# Query 2
cur.execute("""
    SELECT p.driver_1, array_agg(distinct p.car_number), array_agg(ce.event_date), count(coalesce (ce.event_date, null))  
    FROM ii.pls p 
    INNER JOIN ii.can_events ce ON p.car_number = ce.car_number AND ce.event_date  BETWEEN p.start_time AND cast (coalesce(stop_time, '2024-01-22') AS timestamp)
    WHERE ce.event_date BETWEEN cast('2024-01-15' AS timestamp) AND cast('2024-01-22' AS timestamp)
    AND NOT ( p.author_document <> p.author_document_change AND p.stop_time IS NULL)
    GROUP BY p.driver_1;    
    """)
results2 = cur.fetchall()

# Query 3
cur.execute("""
    SELECT p.driver_1, array_agg(distinct p.car_number), array_agg(ce.event_date), count(coalesce (ce.event_date, null)), 
    SUM(cast (coalesce(p.stop_time, '2024-01-22') AS timestamp)- p.start_time), p.start_time, p.stop_time 
    FROM ii.pls p 
    INNER JOIN ii.can_events ce ON p.car_number = ce.car_number AND ce.event_date  BETWEEN p.start_time AND cast (coalesce(stop_time, '2024-01-22') AS timestamp)
    WHERE ce.event_date BETWEEN cast('2024-01-15' AS timestamp) AND cast('2024-01-22' AS timestamp)
    AND NOT ( p.author_document <> p.author_document_change AND p.stop_time IS NULL)
    GROUP BY p.driver_1, p.start_time, p.stop_time;
    """)
results3 = cur.fetchall()

cur.close()
conn.close()
