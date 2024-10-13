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

    typeforms as (
select utm_campaign, utm_content, date(date_submitted_typeform_entered) date, count(*) typeforms
from marketing_mql_students
where date_submitted_typeform_entered is not null
and date_submitted_typeform_entered>='2024-01-01'
group by utm_campaign, utm_content, date_submitted_typeform_entered),
     mqls as (
select utm_campaign, utm_content, date(date_mql_entered) date, count(*) mqls
from marketing_mql_students
where date_mql_entered is not null
and date_mql_entered>='2024-01-01'
group by utm_campaign, utm_content, date_mql_entered),
    sqls as (
select utm_campaign, utm_content, date(date_sql_entered) date, count(*) sqls
from marketing_mql_students
where date_sql_entered is not null
and date_sql_entered>='2024-01-01'
group by utm_campaign, utm_content, date_sql_entered),
    bgs as (
select utm_campaign, utm_content, date(date_bg_enrolled_entered) date, count(*) bgs
from marketing_mql_students
where date_bg_enrolled_entered is not null
and date_bg_enrolled_entered>='2024-01-01'
group by utm_campaign, utm_content, date_bg_enrolled_entered),
    students_dates as (
        select utm_campaign campaign_id, utm_content ad_id, date date_of_reference, typeforms, mqls, sqls, bgs
            from typeforms
            full outer join mqls
            using (utm_campaign, utm_content, date)
            full outer join sqls
            using (utm_campaign, utm_content, date)
            full outer join bgs
            using (utm_campaign, utm_content, date)
    )

select platform
       , campaign_id
     , ad_id
     , date_of_reference
     , to_char(date_of_reference, 'IYYY-IW') AS year_week
     , to_char(date_of_reference, 'YYYY-MM') AS year_month
     , coalesce(clicks, 0) clicks
     , coalesce(total_spend, 0) total_spend
     , coalesce(typeforms, 0) typeforms
     , coalesce(mqls, 0) mqls
     , coalesce(sqls, 0) sqls
     , coalesce(bgs, 0) bgs
     , case when clicks = 0 then 0 else typeforms::float/ clicks end typeform_from_clicks_rate
     , case when typeforms = 0 then 0 else mqls::float  / typeforms  end mql_from_typeform_rate
     , case when mqls = 0 then 0 else sqls::float / mqls  end sql_from_mql_rate
     , case when sqls = 0 then 0 else bgs::float / sqls   end bg_enrolled_from_mql_rate
     , case when typeforms =0 then 0 else bgs::float / typeforms end funnel_conversion_rate
from total_spends
left join students_dates
using (campaign_id,ad_id ,date_of_reference)
