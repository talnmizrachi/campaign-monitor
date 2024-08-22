import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt


def read_data(data):
    platform = st.selectbox("Which platform are we talking about?", options=data['platform'].unique().tolist())
    current_data = data[data['platform'] == platform].copy()
    
    return current_data


def preprocess_data(data):
    def fill_dates(group):
        # Generate the full date range
        full_range = pd.date_range(start=group['creation_date'].min(), end=group['creation_date'].max())
        
        # Reindex the DataFrame to the full date range
        group = group.set_index('creation_date').reindex(full_range).reset_index()
        
        # Rename the columns after resetting the index
        group.columns = ['creation_date', 'platform', 'utm_campaign', 'conversions']
        
        # Forward fill the 'utm_campaign' column to fill in missing values
        group['utm_campaign'] = group['utm_campaign'].ffill()
        group['platform'] = group['platform'].ffill()
        
        return group
    
    mql = data.dropna()
    mql = mql.rename({"campaign_id": "utm_campaign", "segments_date": "creation_date"}, axis=1).copy()
    
    mql['creation_date'] = pd.to_datetime(mql['creation_date'])
    mql = mql.sort_values(['platform', 'utm_campaign', 'creation_date']).copy()
    
    mql_filled = mql.groupby(['platform', 'utm_campaign'], group_keys=False).apply(fill_dates).reset_index(
        drop=True).fillna(0)
    mql_filled = mql_filled[['platform', 'utm_campaign', 'creation_date', 'conversions']].sort_values(
        ['utm_campaign', 'creation_date']).copy()
    return mql_filled


def pivot_data_to_cohorts(data):
    def remove_trailing_zeros(lst):
        while lst and lst[-1] == 0:
            lst.pop()
        return [int(x) for x in lst]
    
    mql_filled_filter = data.groupby('utm_campaign').filter(lambda x: x['creation_date'].nunique() > 1)
    mql_filled_filter['col'] = mql_filled_filter.groupby('utm_campaign').cumcount()
    pivot = mql_filled_filter.pivot_table(index='utm_campaign', columns='col', values='conversions', aggfunc="sum",
                                          fill_value="0")
    pivot = pivot.map(lambda x: int(x) if isinstance(x, str) else x)
    
    result_dict = pivot.apply(lambda row: remove_trailing_zeros(row.tolist()), axis=1).to_dict()
    all_campaign_ids = list(key for key, values in result_dict.items())
    
    return result_dict, all_campaign_ids


def cosine_similarity_computer(old_campaign, new_campaign):
    # Determine the overlapping length
    min_length = min(len(old_campaign), len(new_campaign))
    
    # Truncate both series to the overlapping length
    old_campaign_trimmed = np.array(old_campaign[:min_length]).reshape(1, -1)
    new_campaign_trimmed = np.array(new_campaign[:min_length]).reshape(1, -1)
    
    # Compute cosine similarity on the trimmed series
    similarity = cosine_similarity(old_campaign_trimmed, new_campaign_trimmed)[0][0]
    return similarity


def compute_similarities(new_campaign, all_campaigns, num_of_campaigns=3):
    
    len_of_new_campaign = len(all_campaigns[new_campaign])
    old_campaigns = {k: v[0:len_of_new_campaign] for k, v in all_campaigns.items() if
                     len(v) > len_of_new_campaign + 2 and k != new_campaign}
    
    similarities = {}
    for campaign_name, old_campaign in old_campaigns.items():
        similarity = cosine_similarity_computer(old_campaign, all_campaigns[new_campaign])
        similarities[campaign_name] = similarity
    
    # Find the top 3 most similar old campaigns
    top_similar_campaigns = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:num_of_campaigns]
    
    return top_similar_campaigns, similarities, old_campaigns


def plot_campaign_conversions(new_campaign_id, all_campaigns, old_campaigns, top_similar_campaigns, similarities):
    len_of_new_campaign = len(all_campaigns[new_campaign_id])

    for campaign_name, similarity_score in top_similar_campaigns:
        fig, ax = plt.subplots(figsize=(16, 6))
        ax.plot(all_campaigns[campaign_name][0:len_of_new_campaign * 2], label=campaign_name, marker='o', alpha=0.7,lw=8)
        ax.plot(all_campaigns[new_campaign_id], label="New Campaign", marker='o', alpha=0.5, lw=3)
        ax.set_ylim(bottom=0)  # Adjust the bottom to start at 0

        ax.legend()
        st.subheader(f'Cosine Similarity Comparison: {campaign_name} vs New Campaign ({100 * similarity_score:.1f}%)')
        ax.set_xlabel('Time')
        ax.set_ylabel('Conversions')
        
        st.pyplot(plt)


def main(data, campaign_name_dict):
    data_ = read_data(data)
    preprocessed_data = preprocess_data(data_)
    campaigns_dictionaries, _all_campaigns = pivot_data_to_cohorts(preprocessed_data)

    campaign_to_check = st.text_input("Choose a campaign to compare:", value="21591593475")
    st.markdown(f"""Campaign Name:  
                {campaign_name_dict.get(campaign_to_check)}""")

    top_similar, similarities, old_campaigns = compute_similarities(campaign_to_check, campaigns_dictionaries,
                                                                    num_of_campaigns=3)
    

    plot_campaign_conversions(
            new_campaign_id=campaign_to_check,
            all_campaigns=campaigns_dictionaries,
            old_campaigns=old_campaigns,
            top_similar_campaigns=top_similar,
            similarities=similarities
        )
    
    st.divider()
