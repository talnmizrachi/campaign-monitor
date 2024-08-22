SELECT campaign_id,campaign_name, segments_date, sum(metrics_costmicros)/1e6 daily_campaign_cost
from google_ads_campaign_performance_by_day
where true
and metrics_costmicros>0
and segments_date>='2023-07-18'
group by 1,2,3
order by daily_campaign_cost desc