with total_spends as (
select 'Google' as platform, campaign_id, adgroupad_ad_id ad_id, date(segments_date) date_of_reference ,sum(metrics_clicks) as clicks,  sum(metrics_costmicros)/1000000 total_spend
from google_ads_ad_performance_by_day
GROUP BY campaign_id, adgroupad_ad_id, segments_date
union all
select 'Facebook' as platform, _campaign_id campaign_id, _ad_id,date(_date_start), sum(_clicks::int) as clicks, sum(_spend::float) total_spend
from facebook_fb_ads_insight_report_basic
group by _campaign_id, _ad_id,_date_start
union all
select 'TikTok' as platform, campaign_id, ad_id,  date(dimensions_stat_time_day), sum(metrics_clicks::int) clicks, sum(metrics_spend::float)
from  tiktok_auction_ads_basic_daily
join tiktok_ads
on tiktok_ads.ad_id = tiktok_auction_ads_basic_daily.dimensions_ad_id
group by campaign_id, ad_id,  dimensions_stat_time_day),

    student_data as (
select utm_campaign campaign_id, utm_content ad_id, domain, plan_duration, count(hubspot_id) total_students
from marketing_mql_students
join bg_students
using (hubspot_id)
group by utm_campaign,utm_content , lp_variant, domain, plan_duration),

    all_campaigns_data as (
    select platform, date_of_reference, campaign_id, ad_id, sum(clicks) as clicks, sum(total_spend)::int total_spend
from student_data
join total_spends
using (campaign_id, ad_id)
group by platform, date_of_reference, campaign_id, ad_id
),

    raw_stages as (
select
    utm_campaign as campaign_id
    ,utm_content as ad_id
       , case when date_submitted_typeform_entered is not null then 1 else 0 end is_typeform
       , case when date_mql_entered is not null then 1 else 0 end is_mql
       , case when date_sql_entered is not null then 1 else 0 end is_sql
       , case when date_bg_enrolled_entered is not null then 1 else 0 end is_bg_enrolled
from marketing_mql_students
where date_submitted_typeform_entered>'2024-01-01')


select platform, campaign_id, ad_id, sum(clicks) ad_clicks, sum(total_spend) ad_spend
,sum(is_typeform) typeforms_count
,sum(is_mql) mql_count
,sum(is_sql) sql_counts
,sum(is_bg_enrolled) bg_enrolled
     , case when sum(is_typeform) = 0 then 0 else sum(is_mql::float)  / sum(is_typeform) end mql_from_typeform_rate
     , case when sum(is_mql) = 0 then 0 else sum(is_sql::float) / sum(is_mql)  end sql_from_mql_rate
    , case when sum(is_sql) = 0 then 0 else sum(is_bg_enrolled::float) /sum(is_sql)  end bg_enrolled_from_mql_rate
    , sum(is_bg_enrolled::float) / sum(is_typeform) funnel_conversion_rate
from raw_stages
join all_campaigns_data
using (campaign_id, ad_id)
group by platform, campaign_id, ad_id