import hashlib
import os
from general_objects.dictionaries_fe_be import get_be_criteria_for_campaign
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
load_dotenv("auth.env")

USER_CREDENTIALS = {
    os.getenv("USER1_USERNAME"): hashlib.sha256(os.getenv("USER1_PASSWORD").encode()).hexdigest(),
    os.getenv("USER2_USERNAME"): hashlib.sha256(os.getenv("USER2_PASSWORD").encode()).hexdigest(),
    os.getenv("USER3_USERNAME"): hashlib.sha256(os.getenv("USER3_PASSWORD").encode()).hexdigest()
    # Add more users as needed
}


def check_password(username, password):
    """Check if the entered username and password match any stored credentials."""
    if username in USER_CREDENTIALS:
        return hashlib.sha256(password.encode()).hexdigest() == USER_CREDENTIALS[username]
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

    return mqls_, ga_campaigns_costs, campaigns_conversions, campaign_names_dict


def mainly_main():
    engine = init_connection()
    mql, ga_campaigns_costs, campaigns_conversions_, _campaign_names_dict_ = get_data(engine)
    _, campaigns_tab, single_tab, tables_tab = st.tabs(["Hello", "Campaigns level", "Single Campaign","Raw Tables"])

    with campaigns_tab:
        st.subheader("Campaign level analysis")

        criteria = get_be_criteria_for_campaign(st.radio("Select Criteria", ["TypeForm Sent", "MQL", "SQL", "BG Enrolled"]))
        scatter_plot = generate_scatter_chart(mql, ga_campaigns_costs, criteria=criteria)
        relative_campaign_cohort(mql)
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


# Streamlit app structure
def main():
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