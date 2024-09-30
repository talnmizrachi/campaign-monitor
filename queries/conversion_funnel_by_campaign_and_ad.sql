with raw_stages as (
select
    utm_campaign as campaign_id
    ,utm_content as ad_id
       , case when date_submitted_typeform_entered is not null then 1 else 0 end is_typeform
       , case when date_mql_entered is not null then 1 else 0 end is_mql
       , case when date_sql_entered is not null then 1 else 0 end is_sql
       , case when date_bg_enrolled_entered is not null then 1 else 0 end is_bg_enrolled
from marketing_mql_students
where date_submitted_typeform_entered>'2024-01-01')

select campaign_id, ad_id
,sum(is_typeform) typeforms_count
,sum(is_mql) mql_count
,sum(is_sql) sql_counts
,sum(is_bg_enrolled) bg_enrolled
     , case when sum(is_typeform) = 0 then 0 else sum(is_mql::float)  / sum(is_typeform) end mql_from_typeform_rate
     , case when sum(is_mql) = 0 then 0 else sum(is_sql::float) / sum(is_mql)  end sql_from_mql_rate
    , case when sum(is_sql) = 0 then 0 else sum(is_bg_enrolled::float) /sum(is_sql)  end bg_enrolled_from_mql_rate
    , sum(is_bg_enrolled::float) / sum(is_typeform) funnel_conversion_rate
from raw_stages
group by 1,2;