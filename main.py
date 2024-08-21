import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

from dataframes_operations.single_campaign.bar_chart_of_mqls_per_campaign import main as bar_char_for_campaign
from dataframes_operations.single_campaign.line_plot_cummulative_mqls_and_costs import main as take_data_for_specific_campaign
from dataframes_operations.single_campaign.compare_conversions_for_campaign import main as line_plot_comparing

from dataframes_operations.all_campaigns.scatter_chart_mql_costs import main as generate_scatter_chart
from dataframes_operations.all_campaigns.relative_campaign_cohort import main as relative_campaign_cohort
from queries.read_query import read_query

load_dotenv()

# Initialize the connection
@st.cache_resource
def init_connection():
    DATABASE_URL = os.getenv('DATALAYER_URL')
    engine = create_engine(DATABASE_URL)
    return engine


# Function to run the query and get the data
@st.cache_data
def get_data(_engine):

    campaigns_conversions = pd.read_sql(read_query("queries/conversions_for_single_campaigns.sql"), _engine)
    mqls_ = pd.read_sql(read_query("queries/mql_students.sql"), _engine)
    ga_campaigns_costs = pd.read_sql(read_query("queries/google_ads_campaigns_costs.sql"), _engine)
    ga_campaigns_costs = ga_campaigns_costs[ga_campaigns_costs['daily_campaign_cost']>0].copy()
    
    return mqls_, ga_campaigns_costs, campaigns_conversions


# Streamlit app structure
def main():
    st.title("Campaign and MQL Score Analysis")
    
    engine = init_connection()
    mql, ga_campaigns_costs, campaigns_conversions_ = get_data(engine)
    _, campaigns_tab, single_tab = st.tabs(["Hello", "Campaigns level", "Single Campaign"])
    
    with campaigns_tab:
        scatter_plot = generate_scatter_chart(mql, ga_campaigns_costs)
        relative_campaign_cohort(mql)
    with single_tab:
        line_plot_comparing(campaigns_conversions_)
        campaign_for_graph = st.selectbox("Select Campaign ID", ga_campaigns_costs['campaign_id'].unique().tolist())
        take_data_for_specific_campaign(mql, ga_campaigns_costs, campaign_id=campaign_for_graph, mql_value=1500)
        bar_char_for_campaign(mql, ga_campaigns_costs, campaign_id=campaign_for_graph)
    
    
    
    
    # # User selection for campaigns and MQL scores
    # campaign_options = ga_campaigns_costs['campaign_id'].head()
    # selected_campaigns = st.multiselect("Select Campaigns", campaign_options, default=campaign_options)
    #
    # mql_options = ['mql_1', 'mql_2', 'mql_3', 'mql_4', 'mql_5']
    # selected_mqls = st.multiselect("Select MQL Scores", mql_options, default=mql_options)
    #
    # if selected_campaigns and selected_mqls:
    #     df_filtered = df[df['utm_campaign'].isin(selected_campaigns)].copy()
    #     df_filtered['selected_mql_sum'] = df_filtered[selected_mqls].sum(axis=1)
    #
    #     # Adjusting the columns width
    #     col1, col2 = st.columns([2, 1])  # This makes col1 twice as wide as col2
    #
    #     with col1:
    #         st.write(f"### Heatmap for Selected Campaigns")
    #
    #         # Pivot data for heatmap
    #         heatmap_data = df_filtered.pivot_table(
    #             index='week',
    #             columns='campaign_row',
    #             values='selected_mql_sum',
    #             aggfunc='sum'
    #         )
    #
    #         # Creating heatmap
    #         fig, ax = plt.subplots(figsize=(12, 8))
    #         sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax, annot=True, fmt="g")
    #         plt.title(f'Heatmap of Selected MQLs Sum for Selected Campaigns')
    #         st.pyplot(fig)
    #
    #     with col2:
    #         st.write("### Summary of Selected MQL Scores by Campaign")
    #
    #         summary_table = df_filtered.groupby('utm_campaign')[selected_mqls].sum()
    #         st.dataframe(summary_table)


if __name__ == "__main__":
    main()