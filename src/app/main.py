import streamlit as st
import pandas as pd
import plotly.express as px
from src.data.scraper import get_real_historical_ma_data, get_real_live_ma_data, get_company_profile

st.set_page_config(page_title="Tech M&A Landscape", layout="wide")

# Initialize session state data so it doesn't regenerate on every interaction
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = get_real_historical_ma_data()
if 'live_data' not in st.session_state:
    st.session_state.live_data = get_real_live_ma_data()

st.title("Tech M&A and Exit Landscape Analyzer")
st.markdown("Analyze historical tech acquisitions (>= $50M) and live market trends to identify optimal startup lanes.")

tab1, tab2, tab3 = st.tabs(["Historical View", "Live Market & Analytics", "Monopoly Tracker"])

with tab1:
    st.header("Historical View (Past 3 Years)")
    df_hist = st.session_state.historical_data

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Total Value by Category")
        if not df_hist.empty:
            fig1 = px.bar(df_hist.groupby('Category')['Value ($M)'].sum().reset_index(),
                          x='Category', y='Value ($M)', title="Total Deal Value by Category ($M)")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("No historical data available for chart.")

    with col2:
        st.subheader("Deal Volume Over Time")
        if not df_hist.empty:
            df_hist['YearMonth'] = pd.to_datetime(df_hist['Date']).dt.to_period('M').astype(str)
            volume_over_time = df_hist.groupby('YearMonth').size().reset_index(name='Deal Count')
            fig2 = px.line(volume_over_time, x='YearMonth', y='Deal Count', title="Number of Deals Over Time")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No historical data available for chart.")

    st.subheader("Recent Major Deals (>= $50M)")
    st.dataframe(df_hist.sort_values(by='Date', ascending=False).head(20), use_container_width=True)

with tab2:
    st.header("Live Market & State-of-the-Art Analytics")

    df_live = st.session_state.live_data

    col_live1, col_live2 = st.columns([2, 1])

    with col_live1:
        st.subheader("Top Valuated Companies (In Talks)")
        if not df_live.empty and 'Estimated Valuation ($M)' in df_live.columns and df_live['Estimated Valuation ($M)'].notna().any():
            top_live = df_live.sort_values(by='Estimated Valuation ($M)', ascending=False).head(15)
            fig_live = px.bar(top_live, x='Company', y='Estimated Valuation ($M)', color='Category',
                              title="Highest Valuated Companies Currently in Acquisition Talks")
            st.plotly_chart(fig_live, use_container_width=True)
        else:
            st.warning("No live valuation data available to visualize.")

        st.dataframe(df_live, use_container_width=True)

    with col_live2:
        st.subheader("RAG Company Insight")
        st.write("Select a company to analyze using our mock RAG Engine:")
        selected_company = st.selectbox("Select Company:", df_live['Company'].tolist())

        if st.button("Analyze Company"):
            with st.spinner("Retrieving contextual data..."):
                # Get headline context if available
                headline = ""
                company_row = df_live[df_live['Company'] == selected_company]
                if not company_row.empty:
                    headline = company_row.iloc[0]['Source Headline']

                profile = get_company_profile(selected_company, headline)
                st.success("Analysis Complete!")
                st.write(f"**Description:** {profile['Description']}")
                st.write(f"**Products/Services:**")
                for prod in profile['Products']:
                    st.write(f"- {prod}")
                st.write(f"**RAG Inferred Category:** {profile['Inferred Category']}")

    st.divider()
    st.subheader("Actionable Insight: Best Lanes for Startups")
    # Simple logic: category with most activity in live data
    if not df_live.empty:
        hot_categories = df_live['Category'].value_counts()
        if not hot_categories.empty and hot_categories.index[0] != 'Pending Analysis':
            top_lane = hot_categories.index[0]
            st.info(f"Based on live in-talks data, the most active tech lane right now is **{top_lane}**. "
                    f"Startups aiming for rapid, high-dollar exits should consider building in the {top_lane} space.")
        else:
             st.info("Not enough specific categorized data to generate lane insights right now.")
    else:
        st.info("No live data available for actionable insights.")

with tab3:
    st.header("Monopoly Tracker")
    st.write("Visualizing which Big Tech companies are aggressively acquiring startups in specific tech lanes.")

    if not df_hist.empty:
        # Calculate acquisitions by Acquirer and Category
        monopoly_data = df_hist.groupby(['Acquirer', 'Category']).size().reset_index(name='Acquisition Count')

        if not monopoly_data.empty:
            fig_mono = px.treemap(
                monopoly_data,
                path=['Category', 'Acquirer'],
                values='Acquisition Count',
                title="Big Tech Monopoly Map: Acquisitions by Lane",
                color='Acquirer'
            )
            st.plotly_chart(fig_mono, use_container_width=True)
        else:
            st.warning("Insufficient categorical data for Monopoly Tracker.")
    else:
        st.warning("No historical data available for Monopoly Tracker.")

    # Identify Monopolies (Acquirer with highest share in a category)
    st.subheader("Potential Monopolies Forming")

    for category in df_hist['Category'].unique():
        cat_data = monopoly_data[monopoly_data['Category'] == category]
        if not cat_data.empty:
            top_acquirer = cat_data.sort_values(by='Acquisition Count', ascending=False).iloc[0]
            total_cat_acquisitions = cat_data['Acquisition Count'].sum()
            share = (top_acquirer['Acquisition Count'] / total_cat_acquisitions) * 100

            if share > 20: # Threshold for showing a warning
                st.warning(f"**{top_acquirer['Acquirer']}** is dominating the **{category}** lane, accounting for **{share:.1f}%** of recent historical acquisitions.")
