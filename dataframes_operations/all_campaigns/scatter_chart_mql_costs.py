import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events


def get_total_cost_per_campaign(costs):
    costs['campaign_id'] = costs['campaign_id'].astype(str)
    total_costs = costs[['campaign_id', 'daily_campaign_cost']].groupby('campaign_id', as_index=False).sum()
    
    return total_costs


def get_mqls_per_campaign(mqls):

    top_campaigns = mqls.groupby('utm_campaign', as_index=False)[['mql_1', 'mql_2', 'mql_3', 'mql_4', 'mql_5']].sum()
    top_campaigns['total_mqls'] = top_campaigns[['mql_1', 'mql_2', 'mql_3', 'mql_4', 'mql_5']].sum(axis=1)
    top_campaigns.sort_values('total_mqls', ascending=False)
    
    return top_campaigns


def merge_mqls_and_costs(top_mqls, total_costs):
    merged = top_mqls.merge(total_costs, left_on='utm_campaign', right_on='campaign_id')

    return merged[['utm_campaign', 'total_mqls', 'daily_campaign_cost']].copy()


def generate_data_for_plot(mqls_df, costs_df):
    total_mqls_ = get_mqls_per_campaign(mqls_df)
    total_costs_ = get_total_cost_per_campaign(costs_df)
    final_df = merge_mqls_and_costs(total_mqls_, total_costs_)
    return final_df


def generate_plot(data_for_plot):
    data_for_plot['cost_per_mql'] = data_for_plot['daily_campaign_cost'] / data_for_plot['total_mqls']

    fig = px.scatter(
        data_for_plot,
        x='total_mqls',
        y='daily_campaign_cost',
        text='utm_campaign'  # This adds the labels to the points
    )

    fig.update_traces(
        textposition='top center',
        hovertemplate=(
                '<b>Campaign:</b> %{text}<br>' +
                '<b>Total MQLs:</b> %{x}<br>' +
                '<b>Daily Campaign Cost:</b> %{y}<br>' +
                '<b>Cost per MQL:</b> %{customdata[0]:.2f}<extra></extra>'
        ),
        customdata=data_for_plot[['cost_per_mql']]  # Pass the ratio to the hover template
    )


    fig.add_shape(
        type='line',
        x0=data_for_plot['total_mqls'].max()/2, x1=data_for_plot['total_mqls'].max()/2,  # x position of the line
        y0=min(data_for_plot['daily_campaign_cost']), y1=max(data_for_plot['daily_campaign_cost']),  # vertical line spans entire y-axis
        line=dict(color='RoyalBlue', width=2)
    )

    fig.add_shape(
        type='line',
        x0=min(data_for_plot['total_mqls']), x1=max(data_for_plot['total_mqls']),  # x position of the line
        y0=data_for_plot['daily_campaign_cost'].max()/2, y1=data_for_plot['daily_campaign_cost'].max()/2,  # vertical line spans entire y-axis
        line=dict(color='RoyalBlue', width=2)
    )
    # selected_points = plotly_events(fig, click_event=False, hover_event=False, select_event=True)
    #
    # st.write(f"Click events:{selected_points}" )
    # Display the plot in Streamlit
    st.plotly_chart(fig)
    st.divider()

    return fig


def main(mqls_df, costs_df):
    data_for_scatter_plot = generate_data_for_plot(mqls_df, costs_df)
    return generate_plot(data_for_scatter_plot)
