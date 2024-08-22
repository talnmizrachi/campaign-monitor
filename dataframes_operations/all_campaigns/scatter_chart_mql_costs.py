import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events


def get_total_cost_per_campaign(costs):
    costs['campaign_id'] = costs['campaign_id'].astype(str)
    total_costs = costs[['campaign_id', 'daily_campaign_cost']].groupby('campaign_id', as_index=False).sum()
    
    return total_costs


def get_mqls_per_campaign(mqls, criteria):
    def generate_df_for_single_criteria(mqls, criteria):
        top_campaigns = mqls.groupby('utm_campaign', as_index=False)[[criteria]].sum()
        top_campaigns = top_campaigns.rename({criteria: f'total_{criteria}s'}, axis=1)
        top_campaigns.sort_values(f'total_{criteria}s', ascending=False)
        return top_campaigns

    top_campaigns = generate_df_for_single_criteria(mqls, criteria)
    # if criteria =='mql':
    #     top_campaigns = mqls.groupby('utm_campaign', as_index=False)[['mql_1', 'mql_2', 'mql_3', 'mql_4', 'mql_5']].sum()
    #     top_campaigns['total_mqls'] = top_campaigns[['mql_1', 'mql_2', 'mql_3', 'mql_4', 'mql_5']].sum(axis=1)
    #     top_campaigns.sort_values('total_mqls', ascending=False)
    # else:
    #     top_campaigns = generate_df_for_single_criteria(mqls, criteria)

    return top_campaigns


def merge_mqls_and_costs(top_mqls, total_costs, criteria):
    merged = top_mqls.merge(total_costs, left_on='utm_campaign', right_on='campaign_id')

    return merged[['utm_campaign', f'total_{criteria}s', 'daily_campaign_cost']].copy()


def generate_data_for_plot(mqls_df, costs_df, criteria):
    total_mqls_ = get_mqls_per_campaign(mqls_df, criteria)
    total_costs_ = get_total_cost_per_campaign(costs_df)
    final_df = merge_mqls_and_costs(total_mqls_, total_costs_, criteria)
    return final_df


def generate_plot(data_for_plot, criteria):
    data_for_plot[f'cost_per_{criteria}'] = data_for_plot['daily_campaign_cost'] / data_for_plot[f'total_{criteria}s']

    fig = px.scatter(
        data_for_plot,
        x=f'total_{criteria}s',
        y='daily_campaign_cost',
        text='utm_campaign'  # This adds the labels to the points
    )

    fig.update_traces(
        textposition='top center',
        hovertemplate=(
                '<b>Campaign:</b> %{text}<br>' +
                '<b>Total criteria:</b> %{x}<br>' +
                '<b>Daily Campaign Cost:</b> %{y}<br>' +
                '<b>Cost per criteria:</b> %{customdata[0]:.2f}<extra></extra>'
        ),
        customdata=data_for_plot[[f'cost_per_{criteria}']]  # Pass the ratio to the hover template
    )


    fig.add_shape(
        type='line',
        x0=data_for_plot[f'total_{criteria}s'].max()/2, x1=data_for_plot[f'total_{criteria}s'].max()/2,  # x position of the line
        y0=min(data_for_plot['daily_campaign_cost']), y1=max(data_for_plot['daily_campaign_cost']),  # vertical line spans entire y-axis
        line=dict(color='RoyalBlue', width=2)
    )

    fig.add_shape(
        type='line',
        x0=min(data_for_plot[f'total_{criteria}s']), x1=max(data_for_plot[f'total_{criteria}s']),  # x position of the line
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


def main(mqls_df, costs_df, criteria='mql'):
    data_for_scatter_plot = generate_data_for_plot(mqls_df, costs_df, criteria)
    return generate_plot(data_for_scatter_plot, criteria)
