import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go

# Set up page config with light blue background
st.set_page_config(page_title="Dustbin Monitoring", page_icon="🗑️", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: #e0f2f7; /* Light blue */
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Function to fetch data from Flask server
@st.cache_data(ttl=60)  # Cache the data for 60 seconds
def fetch_data():
    url = "http://127.0.0.1:5000/get_dustbin_data"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data: {response.status_code}")
            return {}
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return {}



# Display Last Item Image Section
st.subheader("📸 Last Received Trash Item")
with st.container():
    image_path = "last_item.png"
    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image, caption="Last Item Received", use_column_width=True)
    else:
        st.warning("No recent item detected. Please check again later.")

        
# Fetch and prepare data
dustbins_data = fetch_data().get('dustbins', [])
if dustbins_data:
    dustbin_df = pd.DataFrame(dustbins_data)
    dustbin_df['color'] = dustbin_df['overall_fill_percentage'].apply(
        lambda x: [255, 0, 0, 180] if x > 85 else ([255, 255, 0, 180] if x > 50 else [0, 255, 0, 180])
    )

# Function to display bin details
def display_bin_details(bin_data):
    st.subheader(f"Bin code: {bin_data['code']}")
    st.write(f"**📍 Address**: {bin_data['address']}")
    st.write(f"**🗑️ Overall Fill Percentage**: {bin_data['overall_fill_percentage']}%")

    # Display Overall Progress Bar
    st.progress(bin_data['overall_fill_percentage'] / 100)

    # Function to create pie chart using Plotly
    compartments = {
        "Recyclable Bio": bin_data['recyclable_bio'],
        "Recyclable Non-Bio": bin_data['recyclable_nonbio'],
        "Non-Recyclable Bio": bin_data['nonrecyclable_bio'],
        "Non-Recyclable Non-Bio": bin_data['nonrecyclable_nonbio']
    }

    colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3']  # Colors for each compartment

    # Create Pie chart for each compartment in one horizontal line
    col1, col2, col3, col4 = st.columns(4)  # Create 4 equal columns for pie charts

    # Pie Chart Layout Adjustments
    pie_chart_layout = {
        'width': 200,  # Set a uniform width for each pie chart
        'height': 200,  # Set a uniform height for each pie chart
        'margin': dict(t=20, b=20, l=20, r=20)  # Set uniform margins
    }

    with col1:
        fig = go.Figure(data=[go.Pie(labels=["Filled", "Remaining"],
                                     values=[bin_data['recyclable_bio'], 100 - bin_data['recyclable_bio']],
                                     marker_colors=[colors[0], "#e6e6e6"], hole=0)])
        fig.update_layout(title="Recyclable Bio", **pie_chart_layout)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure(data=[go.Pie(labels=["Filled", "Remaining"],
                                     values=[bin_data['recyclable_nonbio'], 100 - bin_data['recyclable_nonbio']],
                                     marker_colors=[colors[1], "#e6e6e6"], hole=0)])
        fig.update_layout(title="Recyclable Non-Bio", **pie_chart_layout)
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        fig = go.Figure(data=[go.Pie(labels=["Filled", "Remaining"],
                                     values=[bin_data['nonrecyclable_bio'], 100 - bin_data['nonrecyclable_bio']],
                                     marker_colors=[colors[2], "#e6e6e6"], hole=0)])
        fig.update_layout(title="Non-Recyclable Bio", **pie_chart_layout)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        fig = go.Figure(data=[go.Pie(labels=["Filled", "Remaining"],
                                     values=[bin_data['nonrecyclable_nonbio'], 100 - bin_data['nonrecyclable_nonbio']],
                                     marker_colors=[colors[3], "#e6e6e6"], hole=0)])
        fig.update_layout(title="Non-Recyclable Non-Bio", **pie_chart_layout)
        st.plotly_chart(fig, use_container_width=True)
        
# Image and Classification Display (NEW CODE - Add this section)
st.subheader("Trash Image and Classification")
  
# Layout: Map on top, bin data below
st.header("Dustbin Monitoring Dashboard")

# "Update" Button to refresh the page
update_button = st.button("Update Page")

if update_button:
    # Trigger re-fetching of data when the button is clicked
    dustbins_data = fetch_data().get('dustbins', [])
    if dustbins_data:
        dustbin_df = pd.DataFrame(dustbins_data)
        dustbin_df['color'] = dustbin_df['overall_fill_percentage'].apply(
            lambda x: [255, 0, 0, 180] if x > 85 else ([255, 255, 0, 180] if x > 50 else [0, 255, 0, 180])
        )
        st.success("Page Updated!")

# Map at the top, toggled by a checkbox
show_map = st.checkbox("Show Map", value=True)

if show_map:
    # Map at the top
    with st.container():
        st.subheader("📍 Dustbin Locations in Mumbai")
        layer = pdk.Layer(
            "ScatterplotLayer",
            dustbin_df,
            get_position=["longitude", "latitude"],
            get_color="color",
            get_radius=80
        )

        view_state = pdk.ViewState(
            latitude=dustbin_df["latitude"].mean(),
            longitude=dustbin_df["longitude"].mean(),
            zoom=12
        )

        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

# Bin data section below the map
with st.container():
    selected_bin = st.selectbox("🔍 Select a Dustbin", dustbin_df['code'])
    bin_data = next((bin for bin in dustbins_data if bin['code'] == selected_bin), None)
    if bin_data:
        display_bin_details(bin_data)

# 🔥 Display notification panel for bins filled above 80% (left sidebar)
with st.sidebar:
    st.header("🚨 Notification Panel")
    high_fill_bins = [bin for bin in dustbins_data if bin['overall_fill_percentage'] > 80]

    if high_fill_bins:
        for bin in high_fill_bins:
            st.markdown(f"### Bin {bin['code']} - {bin['overall_fill_percentage']}% Full")
            st.markdown(f"**📍 Location**: {bin['address']}")
            st.markdown(f"**⏱ Last Updated**: {bin['timestamp']}")
            st.markdown("---")
    else:
        st.markdown("No bins are above 80% full at the moment.")

# 🔄 Disable automatic refresh
# st_autorefresh(interval=10000, key="refresh_dashboard")