import streamlit as st
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def create_base_for_pivot(mql, selection='week'):
    interim_mql = mql.copy()
    st.write(interim_mql)
    if selection == "week":
        interim_mql["cohort_skip"] = pd.to_datetime(interim_mql['creation_date']).dt.strftime("%Y-%V")
    elif selection == 'month':
        interim_mql["cohort_skip"] = pd.to_datetime(interim_mql['creation_date']).dt.strftime("%Y-%m")
    elif selection == 'quarter':
        interim_mql["cohort_skip"] = pd.to_datetime(interim_mql['creation_date']).dt.strftime("%Y-%B")
    else:
        interim_mql["cohort_skip"] = pd.to_datetime(interim_mql['creation_date']).dt.date
    
    st.write(interim_mql[['cohort_skip','creation_date']])
    interim_mql = interim_mql.drop('creation_date', axis=1).copy()
    interim_mql = interim_mql.groupby(['utm_campaign','cohort_skip'], as_index=False).sum()
    return interim_mql


def main(mql_df, n_campaigns=50):
    all_mqls = ["mql_1", "mql_2", "mql_3", "mql_4", "mql_5"]

    mql_selection = st.multiselect("Select MQL Scores", all_mqls, default=all_mqls)
    cadance_selection = st.radio("What is the cadance?", ["Day","Week", "Month", 'Quarter'])

    temping = create_base_for_pivot(mql_df, selection=cadance_selection.lower())
    temping['cohort_time'] = temping[['utm_campaign']].groupby('utm_campaign', as_index=False).cumcount()

    st.write("### Heatmap of Total MQL Scores by Campaign")

    for_pivot = pd.concat((temping[['utm_campaign', 'cohort_time']], temping[mql_selection].sum(axis=1)), axis=1)

    pivoted = for_pivot.pivot_table(index='utm_campaign', columns='cohort_time', values=0, aggfunc='sum')
    pivoted['total'] = pivoted.sum(axis=1)

    # st.write(pivoted.head(n_campaigns))
    pivoted = pivoted.sort_values('total', ascending=False).head(n_campaigns)
    pivoted = pivoted.drop('total', axis=1)
    fig, ax = plt.subplots(figsize=(16, 10))
    ax = sns.heatmap(pivoted, annot=True, cmap='Greens', cbar=False)
    st.pyplot(fig)
    return fig

