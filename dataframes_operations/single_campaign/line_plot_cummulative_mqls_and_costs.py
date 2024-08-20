import streamlit as st


def main(df, costs, campaign_id, mql_value=150):
    specific_campaign_mql = df[df['utm_campaign'] == str(campaign_id)].copy()
    specific_campaign_costs = costs[costs['campaign_id'] == str(campaign_id)].copy()
    
    specific_campaign_mql['total_daily_mqls'] = specific_campaign_mql[
        [x for x in specific_campaign_mql.columns if x.startswith('mql')]].sum(axis=1)
    
    costs_for_merge = specific_campaign_costs[['segments_date', 'daily_campaign_cost']].copy()
    mqls_for_merge = specific_campaign_mql[['creation_date', 'total_daily_mqls']].copy()
    for_cummalative = costs_for_merge.sort_values('segments_date').merge(mqls_for_merge, left_on='segments_date',
                                                                         right_on='creation_date', how='left')
    for_cummalative = for_cummalative[['segments_date', 'daily_campaign_cost', 'total_daily_mqls']].set_index(
        'segments_date')
    for_cummalative = for_cummalative.fillna(0)
    
    for_cummalative['cum_daily_campaign_cost'] = for_cummalative['daily_campaign_cost'].cumsum()
    for_cummalative['cum_mqls'] = for_cummalative['total_daily_mqls'].cumsum()
    
    
    st.title(f'Cummulative MQLs and Costs for Campaign {campaign_id}')
    st.subheader(f'Cummulative MQLs - {int(for_cummalative["cum_mqls"].max())},'
                 f'\nAvg. expected value of {mql_value}$\n'
                 f'\nCummulative Costs - {int(for_cummalative["cum_daily_campaign_cost"].max()):,}$')
    
    for_cummalative['cum_mqls'] *= mql_value
    st.line_chart(for_cummalative[['cum_mqls', 'cum_daily_campaign_cost']], color=['#6495ED', '#8ACE00'])