import hashlib
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
load_dotenv("auth.env")

USER_CREDENTIALS = {
    os.getenv("USER1_USERNAME"): hashlib.sha256(os.getenv("USER1_PASSWORD").encode()).hexdigest(),
    os.getenv("USER2_USERNAME"): hashlib.sha256(os.getenv("USER2_PASSWORD").encode()).hexdigest()
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


# Function to run the query and get the data
@st.cache_data
def get_data(_engine):

    campaigns_conversions = pd.read_sql(read_query("queries/conversions_for_single_campaigns.sql"), _engine)
    mqls_ = pd.read_sql(read_query("queries/mql_students.sql"), _engine)
    ga_campaigns_costs = pd.read_sql(read_query("queries/google_ads_campaigns_costs.sql"), _engine)
    ga_campaigns_costs = ga_campaigns_costs[ga_campaigns_costs['daily_campaign_cost']>0].copy()

    return mqls_, ga_campaigns_costs, campaigns_conversions

def mainly_main():
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