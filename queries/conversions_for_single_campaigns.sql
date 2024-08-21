SELECT 'google' as platform, campaign_id, segments_date, sum(metrics_conversions) conversions
FROM google_ads_campaign_performance_by_day
where segments_date>'2023-07-01'
GROUP BY platform, campaign_id, segments_date
HAVING COUNT(segments_date) > 1
union all
select 'tiktok' as platform, dimensions_campaign_id campaign_id, date(dimensions_stat_time_day) segments_date, sum(metrics_result::int) conversions
from tiktok_auction_ads_campaign_basic_daily
where date(dimensions_stat_time_day)>'2023-07-01'
group by 1,2,3
-- having sum(metrics_spend::double precision) >0
having  sum(metrics_result::int) > 0
order by 1,2