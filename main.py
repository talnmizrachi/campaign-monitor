import hashlib
import os
from general_objects.dictionaries_fe_be import get_be_criteria_for_campaign
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
import socket

from pygwalker.api.streamlit import StreamlitRenderer


from dataframes_operations.single_campaign.bar_chart_of_mqls_per_campaign import main as bar_char_for_campaign
from dataframes_operations.single_campaign.line_plot_cummulative_mqls_and_costs import main as take_data_for_specific_campaign
from dataframes_operations.single_campaign.compare_conversions_for_campaign import main as line_plot_comparing

from dataframes_operations.all_campaigns.scatter_chart_mql_costs import main as generate_scatter_chart
from dataframes_operations.all_campaigns.relative_campaign_cohort import main as relative_campaign_cohort
from queries.read_query import read_query

load_dotenv()
load_dotenv("auth.env")

def get_user_credentials():
    USER_CREDENTIALS = {
        os.getenv("USER1_USERNAME"): hashlib.sha256(os.getenv("USER1_PASSWORD").encode()).hexdigest(),
        os.getenv("USER2_USERNAME"): hashlib.sha256(os.getenv("USER2_PASSWORD").encode()).hexdigest(),
        os.getenv("USER3_USERNAME"): hashlib.sha256(os.getenv("USER3_PASSWORD").encode()).hexdigest()
        # Add more users as needed
    }
    
    return USER_CREDENTIALS


def check_password(username, password):
    """Check if the entered username and password match any stored credentials."""
    user_credentials = get_user_credentials()
    if username in user_credentials:
        return hashlib.sha256(password.encode()).hexdigest() == user_credentials[username]
    return False


# Initialize the connection
@st.cache_resource
def init_connection():
    DATABASE_URL = os.getenv('DATALAYER_URL')
    engine = create_engine(DATABASE_URL)
    return engine


def read_and_preprocess_campaign_costs(_engine):
    ga_campaigns_costs_ = pd.read_sql(read_query("queries/google_ads_campaigns_costs.sql"), _engine)
    ga_campaigns_costs_ = ga_campaigns_costs_[ga_campaigns_costs_['daily_campaign_cost'] > 0].copy()

    ga_campaigns_costs = ga_campaigns_costs_[['campaign_id', 'segments_date', 'daily_campaign_cost']].copy()
    campaign_names_dict_ = (ga_campaigns_costs_[['campaign_id', 'campaign_name']].
                           drop_duplicates()
                           .set_index('campaign_id').to_dict()['campaign_name'])

    return ga_campaigns_costs, campaign_names_dict_

# Function to run the query and get the data
@st.cache_data
def get_data(_engine):
    ga_campaigns_costs, campaign_names_dict = read_and_preprocess_campaign_costs(_engine)
    campaigns_conversions = pd.read_sql(read_query("queries/conversions_for_single_campaigns.sql"), _engine)
    mqls_ = pd.read_sql(read_query("queries/mql_students.sql"), _engine)
    
    conversion_funnel_by_campaign_and_ad = pd.read_sql(read_query("queries/conversion_funnel_by_campaign_and_ad.sql"), _engine)
    explorer_data = pd.read_sql(read_query("queries/explorer_data.sql"), _engine)
    return mqls_, ga_campaigns_costs, campaigns_conversions, campaign_names_dict, conversion_funnel_by_campaign_and_ad, explorer_data

@st.cache_resource
def get_explorer_renderer(this_df):
    return StreamlitRenderer(this_df)


def mainly_main():
    engine = init_connection()
    mql, ga_campaigns_costs, campaigns_conversions_, _campaign_names_dict_, conversion_funnel_by_campaign_and_ad, explorer_data_ = get_data(engine)
    _, campaigns_tab, single_tab, funnel_view, explore_tab, tables_tab = st.tabs(["Hello", "Campaigns level", "Single Campaign","Funnel View", "Explorer", "Raw Tables"])

    with campaigns_tab:
        st.subheader("Campaign level analysis")

        criteria = get_be_criteria_for_campaign(st.radio("Select Criteria", ["TypeForm Sent", "MQL", "SQL", "BG Enrolled"]))
        scatter_plot = generate_scatter_chart(mql, ga_campaigns_costs, criteria=criteria)
        relative_campaign_cohort(mql)
    with funnel_view:
        st.subheader("Funnel View")
        first_table = ['platform','campaign_id', 'ad_id', "ad_clicks", "ad_spend", 'typeforms_count', "mql_count", "sql_counts", "bg_enrolled"]
        second_table = ['platform','campaign_id', 'ad_id', 'typeform_from_clicks_rate', 'mql_from_typeform_rate', "sql_from_mql_rate", "bg_enrolled_from_mql_rate", "funnel_conversion_rate"]
        
        st.dataframe(conversion_funnel_by_campaign_and_ad[first_table])
        st.dataframe(conversion_funnel_by_campaign_and_ad[second_table])
    with single_tab:
        line_plot_comparing(campaigns_conversions_, _campaign_names_dict_)
        campaign_for_graph = st.selectbox("Select Campaign ID", ga_campaigns_costs['campaign_id'].unique().tolist())
        take_data_for_specific_campaign(mql, ga_campaigns_costs, campaign_id=campaign_for_graph, mql_value=1500)
        bar_char_for_campaign(mql, ga_campaigns_costs, campaign_id=campaign_for_graph)
    with tables_tab:
        with st.expander("MQL Table"):
            st.dataframe(mql)
        with st.expander("Google Ads Campaigns Costs Table"):
            st.dataframe(ga_campaigns_costs)

        with st.expander("Campaigns Conversions Table"):
            st.dataframe(campaigns_conversions_)

    with explore_tab:
        st.subheader("Explore raw data")
        renderer = get_explorer_renderer(explorer_data_)
        renderer.explorer()


def is_running_locally():
    # Check if the app is running locally (localhost)
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip == "127.0.0.1" or local_ip.startswith("192.168.")


def main():
    if is_running_locally():
        st.session_state["authenticated"] = True
    
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    if not st.session_state["authenticated"]:
        st.write("Please log in to access this app.")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Log in"):
            if check_password(username, password):
                st.session_state["authenticated"] = True
                st.success("Logged in successfully!")
            else:
                st.error("Incorrect username or password")
    else:
        st.title("Campaign and MQL Score Analysis")
        mainly_main()
        
        if st.button("Log out"):
            st.session_state["authenticated"] = False

if __name__ == "__main__":
    main()