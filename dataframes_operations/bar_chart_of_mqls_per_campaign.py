import streamlit as st
import plotly.express as px

def main(df, ga_campaigns_costs_, campaign_id):
    st.divider()
    st.title(f"MQL Distribution for Campaign ID: {campaign_id}  (MQL 1-5)")
    
    first_time = ga_campaigns_costs_[ga_campaigns_costs_['campaign_id']==campaign_id]['segments_date'].min()
    specific_campaign = df[
        (df['utm_campaign']==str(campaign_id)) &
        (df['creation_date'] > first_time)].copy()
    
    # Calculate total MQLs
    for_plotting = specific_campaign[['utm_campaign','mql_1', 'mql_2', 'mql_3','mql_4','mql_5']].groupby('utm_campaign').sum()
    st.table(for_plotting)
    fig = px.bar(
        for_plotting.T,
        y=for_plotting.index,
        x=for_plotting.columns.tolist(),
    )
    
    # Rotate the X-axis labels
    fig.update_layout(xaxis_tickangle=-45)
    
    # Display the bar chart in Streamlit
    st.plotly_chart(fig)
    
