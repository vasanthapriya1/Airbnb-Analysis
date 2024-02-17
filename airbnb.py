#Importing 

import pandas as pd
import pymongo
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
from PIL import Image
import geopandas as gpd
import plotly.graph_objs as go


# Creating option menu in the side bar

with st.sidebar:     # Navbar
        selected = option_menu(
                                menu_title="Airbnb",
                                options=['Intro',"Analysis","Map","SWOT Analysis","Tableau Dashboard"],
                                icons = ['mic-fill','cash-stack','map','geo-alt-fill'],
                                menu_icon='alexa',
                                default_index=0,
                              )
    
# # CREATING CONNECTION WITH MONGODB ATLAS AND RETRIEVING THE DATA
# client = pymongo.MongoClient("mongodb+srv://vasanthapriya00106:Priya0101@cluster0.wlilb4y.mongodb.net/")
# db = client.sample_airbnb
# col = db.listingsAndReviews

# #connection and converting df 

# rel_data = []
# for i in col.find():
#     data = dict(Id = i['_id'],
#                 Listing_url = i['listing_url'],
#                 Name = i.get('name'),
#                 Description = i['description'],
#                 House_rules = i.get('house_rules'),
#                 Property_type = i['property_type'],
#                 Room_type = i['room_type'],
#                 Bed_type = i['bed_type'],
#                 Min_nights = int(i['minimum_nights']),
#                 Max_nights = int(i['maximum_nights']),
#                 Cancellation_policy = i['cancellation_policy'],
#                 Accomodates = i['accommodates'],
#                 Total_bedrooms = i.get('bedrooms'),
#                 Bathrooms = i.get('bathrooms'),
#                 Total_beds = i.get('beds'),
#                 Availability_365 = i['availability']['availability_365'],
#                 Price = i['price'],
#                 Security_deposit = i.get('security_deposit'),
#                 Cleaning_fee = i.get('cleaning_fee'),
#                 Extra_people = i['extra_people'],
#                 Guests_included= i['guests_included'],
#                 No_of_reviews = i['number_of_reviews'],
#                 Review_scores = i['review_scores'].get('review_scores_rating'),
#                 Amenities = ', '.join(i['amenities']),
#                 Host_id = i['host']['host_id'],
#                 Host_name = i['host']['host_name'],
#                 Host_neighbourhood=i['host']['host_neighbourhood'],
#                 Street = i['address']['street'],
#                 Country = i['address']['country'],
#                 Country_code = i['address']['country_code'],
#                 Location_type = i['address']['location']['type'],
#                 Longitude = i['address']['location']['coordinates'][0],
#                 Latitude = i['address']['location']['coordinates'][1],
#                 Is_location_exact = i['address']['location']['is_location_exact']
#     )
#     rel_data.append(data)

# df = pd.DataFrame(rel_data)

# Converting dataframe to csv file and saving it

# df.to_csv('Airbnb_data.csv',index=False)

df = pd.read_csv('Airbnb_data.csv')

# Convert specific columns to numeric data types

numeric_columns = ['Total_bedrooms', 'Total_beds', 'No_of_reviews', 'Bathrooms', 'Price', 'Cleaning_fee', 'Review_scores']
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

# HOME PAGE

if selected == "Intro":
    st.title("Welcome")
    col1, col2 = st.columns([2,1])
    with col1:
        st.write('### :green[Project Name]: Airbnb Analysis')
        st.write('### :green[Technologies Used]: Python scripting, Data Preprocessing, Visualization, EDA, Streamlit, MongoDb, Tableau')
        st.write('### :green[Domain]: Travel Industry, Property Management and Tourism')
    with col2:
        image = Image.open("C:/Users/Priya/OneDrive/Desktop/Airbnb Project/Title.jpg")
        st.image(image)
    st.write(
        '''### :green[Overview]: This project is about a dashboard that displays information and insights from the Airbnb data in an interactive and visually appealing manner.'''
    )
    
# Analysis PAGE
    
elif selected == "Analysis":
    with st.sidebar:
        countries = df['Country'].unique()
        country = st.multiselect(label='Select a Country', options=countries)
    col1,col2,col3,col4,col5 = st.columns(5)
    with col1:
        all = st.checkbox('All Host_neighbourhood')
    with col2:
        cities = df[df['Country'].isin(country)]['Host_neighbourhood'].unique()
        city = st.selectbox(label='Select a Host_neighbourhood', options=cities, disabled=all)
    with col3:
        prop_type = st.selectbox(label="Select a Property",options=['Property_type', 'Room_type', 'Bed_type'])
    with col4:
        measure = st.selectbox(label='Select a Measure',options=numeric_columns)
    with col5:
        metric = st.radio(label="Select One",options=['Sum','Avg'])
    
    # Perform aggregation based on user selections
    if metric == 'Avg':
        a = df.groupby(['Host_neighbourhood', prop_type])[numeric_columns].mean().reset_index()
    else:
        a = df.groupby(['Host_neighbourhood', prop_type])[numeric_columns].sum().reset_index()

    if not all:
        b = a[a['Host_neighbourhood'] == city] 
    else:
        if metric == 'Avg':
            a = df.groupby(['Country', prop_type])[numeric_columns].mean().reset_index()
        else:
            a = df.groupby(['Country', prop_type])[numeric_columns].sum().reset_index()
        b = a[a['Country'].isin(country)]
    
    # Display result
        
    st.header(f"{metric} of {measure}")
    with st.expander('View Dataframe'):
        st.write(b.style.background_gradient(cmap="Reds"))

    try:
        b['text'] = b['Country'] + '<br>' + b[measure].astype(str)
        fig = px.bar(b, x=prop_type, y=measure, color='Country', text='text')
    except:
        b['text'] = b['Host_neighbourhood'].astype(str) + '<br>' + b[measure].fillna(0).astype(str)
        fig = px.bar(b, x=prop_type, y=measure, color=prop_type, text='text')
    st.plotly_chart(fig, use_container_width=True)
    
    # donut chart

    fig = px.pie(b, names=prop_type, values=measure, color=measure,hole=0.5)
    fig.update_traces(textposition='outside', textinfo='label+percent')
    st.plotly_chart(fig, use_container_width=True)
    # ['label', 'text', 'value', 'percent']
    
elif selected == 'Map':
    with st.sidebar:
        measure = st.selectbox(label='Select a measure', options=['Total_bedrooms', 'Total_beds', 'No_of_reviews', 'Bathrooms', 'Price', 'Cleaning_fee','Review_scores'])

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    merged_data = pd.merge(world, df, left_on='name', right_on='Country', how='inner')

    a = merged_data.groupby('Country')[['Total_bedrooms', 'Total_beds', 'No_of_reviews', 'Bathrooms', 'Price', 'Cleaning_fee','Review_scores']].mean().reset_index()
    b = merged_data.groupby('Country')['iso_a3'].first()
    c = pd.merge(a,b,left_on='Country', right_on='Country', how='inner')
    fig = px.choropleth(c,
                        locations='iso_a3',
                        color=measure,
                        hover_name='Country',
                        projection='natural earth', # 'natural earth','equirectangular', 'mercator', 'orthographic', 'azimuthal equal area'
                        color_continuous_scale='YlOrRd')
    fig.update_layout(
        title=f'Avg {measure}',
        geo=dict(
            showcoastlines=True,
            coastlinecolor='Black',
            showland=True,
            landcolor='white'
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    a = merged_data.groupby('Country')[['Total_bedrooms', 'Total_beds', 'No_of_reviews', 'Bathrooms', 'Price', 'Cleaning_fee','Review_scores']].sum().reset_index()
    b = merged_data.groupby('Country')['iso_a3'].first()
    c = pd.merge(a, b, left_on='Country', right_on='Country', how='inner')
    fig = px.choropleth(c,
                        locations='iso_a3',
                        color=measure,
                        hover_name='Country',
                        projection='natural earth',
                        # 'natural earth','equirectangular', 'mercator', 'orthographic', 'azimuthal equal area'
                        color_continuous_scale='YlOrRd')
    fig.update_layout(
        title=f'Total {measure}',
        geo=dict(
            showcoastlines=True,
            coastlinecolor='Black',
            showland=True,
            landcolor='white'
        )
    )
    st.plotly_chart(fig, use_container_width=True)

#SWOT Analysis
    
swot_data = {
    'Strength': [
        "Airbnb Enjoys First-Mover Advantage",
        "Innovative Business Model",
        "Offers a Unique Traveling Experience"
    ],
    'Weakness': [
        "Some Hosts Charge Inflated Prices",
        "Claims of Fraudulent Activities"
    ],
    'Opportunity': [
        "Expansion Into New Markets",
        "Increased Focus on Luxury Rentals"
    ],
    'Threats': [
        "Increased Competition",
        "Negative Guest Experiences",
        "User Data Security Leaks"
    ]
}

# Function to plot SWOT analysis
def plot_swot(category):
    data = swot_data.get(category, [])
    if data:
        fig = go.Figure(go.Bar(
            x=[1] * len(data),
            y=data,
            orientation='h',
            marker_color='lightskyblue'
        ))
        fig.update_layout(
            title=f"{category} Analysis",
            xaxis=dict(title="Count"),
            yaxis=dict(title="Factors"),
            showlegend=False
        )
        return fig
    else:
        return None

# Display SWOT analysis tabs and plots
if selected == "SWOT Analysis":
    st.title("SWOT Report")
    tab1, tab2, tab3, tab4 = st.tabs(["Strength", "Weakness", "Opportunity", "Threats"])

    with tab1:
        st.header("Strength")
        fig_strength = plot_swot("Strength")
        if fig_strength:
            st.plotly_chart(fig_strength, use_container_width=True)

    with tab2:
        st.header("Weakness")
        fig_weakness = plot_swot("Weakness")
        if fig_weakness:
            st.plotly_chart(fig_weakness, use_container_width=True)

    with tab3:
        st.header("Opportunity")
        fig_opportunity = plot_swot("Opportunity")
        if fig_opportunity:
            st.plotly_chart(fig_opportunity, use_container_width=True)

    with tab4:
        st.header("Threats")
        fig_threats = plot_swot("Threats")
        if fig_threats:
            st.plotly_chart(fig_threats, use_container_width=True)

elif selected == 'Tableau Dashboard':
    image = Image.open("C:/Users/Priya/OneDrive/Desktop/Airbnb Project/Dashboard.jpg")
    st.image(image)


