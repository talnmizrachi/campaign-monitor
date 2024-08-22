
with base as (
SELECT
            utm_campaign,
            date(greatest(date_mql_entered, hubspot_created_at)) AS creation_date,
            CASE WHEN mql_score = 1 THEN 1 ELSE 0 END AS mql_1,
            CASE WHEN mql_score = 2 THEN 1 ELSE 0 END AS mql_2,
            CASE WHEN mql_score = 3 THEN 1 ELSE 0 END AS mql_3,
            CASE WHEN mql_score = 4 THEN 1 ELSE 0 END AS mql_4,
            CASE WHEN mql_score = 5 THEN 1 ELSE 0 END  AS mql_5,
            case when date_sql_entered is not null then 1 else 0 end as sql,
            case when date_bg_enrolled_entered is not null then 1 else 0 end as bg_enrolled,
            case when date_submitted_typeform_entered is not null then 1 else 0 end as typeform_sent
        FROM
            marketing_mql_students
        WHERE true
             and utm_campaign is not null
             and date_mql_entered is not null
        ORDER BY
            utm_campaign, creation_date desc)

select utm_campaign
     , creation_date
, sum(mql_1) mql_1
, sum(mql_2) mql_2
, sum(mql_3) mql_3
, sum(mql_4) mql_4
, sum(mql_5) mql_5
, sum(mql_1) + sum(mql_2) + sum(mql_3) + sum(mql_4) + sum(mql_5) mql
, sum(sql) sql
, sum(bg_enrolled) bg_enrolled
, sum(typeform_sent) typeform_sent

from base
where true
and creation_date>='2023-07-18'

group by 1,2