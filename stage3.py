#stage3.py


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as tick
from matplotlib import patheffects
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import seaborn as sns
import plotly.graph_objects as go
import numpy as np
import geopandas as gpd
from matplotlib.patches import Patch

#ignore warnings
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)


#load the data

# Medically Endorsed Cannabis locations in Washington Counties.
medicallyEndorsedRetailers = pd.read_excel("data/MedicallyEndorsedRetailers05062025.xls")
# Social Equity Scores for Washington Counties.
socialEquityScores = pd.read_excel("data/SESbyCounty.xlsx")
# Reformatting County Names for Comparisons in Social Equity Scores data.
socialEquityScores['County'] = socialEquityScores['County'].str.replace(' County', '').str.upper()
# Sorting Values
socialEquityScores.sort_values(['County'], inplace=True)


def print_Head(df, name):
    #print name of the dataframe
    print(f"DataFrame: {name}")
    #print the head
    print(df.head())
    #print column names
    print("Columns:", df.columns.tolist())
    print("\n")

#Alex Boyce
#vis_One
#uses: DD, geo
def vis_One():
    print("Vis One: Cannabis Retail Locations by ZIP Code (Exact Counts with Legend and Major Cities)")

    DD = pd.read_csv("data/DD_Licensed_Cannabis_and_Medical_Marijuana_Retail_Locations.csv")
    print_Head(DD, "DD_Licensed_Cannabis_and_Medical_Marijuana_Retail_Locations")

    #load ZIP shapefile and convert CRS
    zcta = gpd.read_file("geo/ct_zipcodes_only.shp").to_crs("EPSG:3395")
    zcta_ct = zcta[zcta["ZCTA5CE10"].str.startswith("06")].copy()

    #prepare DD data
    DD["Zipcode"] = DD["Zipcode"].astype(str).str.zfill(5)
    zip_counts = DD.groupby("Zipcode").size().reset_index(name="store_count")

    #merge with ZIP geometry
    merged = zcta_ct.merge(zip_counts, how="left", left_on="ZCTA5CE10", right_on="Zipcode")
    merged["store_count"] = merged["store_count"].fillna(0).astype(int)

    #categorize counts
    def classify_count(x):
        if x == 0:
            return '0'
        elif x == 1:
            return '1'
        elif x == 2:
            return '2'
        else:
            return '3+'

    merged["count_cat"] = merged["store_count"].apply(classify_count)

    #color map
    color_map = {
        '0': '#cccccc',     # Grey
        '1': '#a6cee3',     # Light Blue
        '2': '#1f78b4',     # Blue-Green
        '3+': '#006d2c'     # Dark Green
    }

    merged["color"] = merged["count_cat"].map(color_map)

    # --- Major and mid-size cities data (lat, lon) in WGS84 ---
    cities = pd.DataFrame({
        'City': [
            'Bridgeport', 'New Haven', 'Stamford', 'Hartford', 'Waterbury',
            'Norwalk', 'Danbury', 'New Britain', 'Meriden', 'Bristol',
            'Milford', 'Shelton', 'Greenwich', 'Torrington',
            'Manchester', 'Middletown', 'Farmington', 'West Haven'
        ],
        'Latitude': [
            41.1865, 41.3083, 41.0534, 41.7637, 41.5582,
            41.1177, 41.3947, 41.6612, 41.5383, 41.6718,
            41.2306, 41.3162, 41.0229, 41.8006,
            41.7830, 41.5622, 41.7200, 41.2692
        ],
        'Longitude': [
            -73.1952, -72.9279, -73.5387, -72.6851, -73.0515,
            -73.4080, -73.4540, -72.7795, -72.8079, -72.9496,
            -73.0621, -73.1305, -73.6262, -73.1218,
            -72.5396, -72.6527, -72.8643, -72.9586
        ]
    })
    eastern_cities = pd.DataFrame({
        'City': [
            'Norwich', 'New London', 'Willimantic', 'Putnam',
            'Danielson', 'Stonington', 'Killingly', 'Plainfield', 'Sprague'
        ],
        'Latitude': [
            41.5243, 41.3557, 41.7198, 41.9424,
            41.7979, 41.3707, 41.8234, 41.6967, 41.4570
        ],
        'Longitude': [
            -72.0753, -72.0995, -72.2170, -71.8676,
            -71.9115, -71.8424, -71.8757, -71.8259, -72.0423
        ]
    })

    #combine top 20 cities with the additional eastern cities
    cities_extended = pd.concat([cities, eastern_cities], ignore_index=True)

    gdf_cities = gpd.GeoDataFrame(
        cities_extended,
        geometry=gpd.points_from_xy(cities_extended['Longitude'], cities_extended['Latitude']),
        crs="EPSG:4326"
    )
    #convert cities to map CRS
    gdf_cities = gdf_cities.to_crs("EPSG:3395")

    #plot
    fig, ax = plt.subplots(figsize=(8, 6))
    merged.plot(color=merged["color"], edgecolor="black", ax=ax)

    #plot cities as green dots
    gdf_cities.plot(ax=ax, color='red', markersize=30, marker='o', label='Cities', edgecolor='black', linewidth=0.5)

    #city labels with an offset
    for x, y, label in zip(gdf_cities.geometry.x, gdf_cities.geometry.y, gdf_cities['City']):
        ax.text(x + 1000, y + 1000, label, fontsize=8, fontweight='bold', color='DarkRed')

    #create legend
    legend_elements = [Patch(facecolor=color, edgecolor='black', label=label) for label, color in color_map.items()]
    legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', label='Cities', markerfacecolor='red', markersize=8, markeredgecolor='black'))
    ax.legend(handles=legend_elements, title="Number of Retail Stores", loc='lower right')

    ax.set_title("Cannabis Retail Store Count by ZIP Code", fontsize=15)
    ax.axis("off")
    plt.tight_layout()
    #save the figure
    plt.savefig("images/vis_one.png")
    plt.show()

#Alex Boyce
#vis_Two
#uses: II
#cleans the THC and CBD columns by extracting numeric data
#filters out invalid values over 100%
#aggregate by month
def vis_Two():
    print("Vis Two: New Product THC & CBD Potency Over Time")

    II = pd.read_csv("data/II_Medical_MarijuanaCannabis_Brands_with_Chemical_Composition1.csv")
    print_Head(II, "II_Medical_MarijuanaCannabis_Brands_with_Chemical_Composition1")

    #select Recorded Date, Tetrahydrocannabinol (THC), and Cannabidiols (CBD) columns
    ii_clean = II[['Recorded Date', 'Tetrahydrocannabinol (THC)', 'Cannabidiols (CBD)']].copy()

    #drop rows with missing date or both THC and CBD
    ii_clean.dropna(subset=['Recorded Date', 'Tetrahydrocannabinol (THC)', 'Cannabidiols (CBD)'], how='all', inplace=True)

    #convert date column to datetime
    ii_clean['Recorded Date'] = pd.to_datetime(ii_clean['Recorded Date'], errors='coerce')

    #clean THC and CBD columns
    for col in ['Tetrahydrocannabinol (THC)', 'Cannabidiols (CBD)']:
        ii_clean[col] = (
            ii_clean[col] #select the column
            .astype(str) #convert to string
            .str.replace('%', '', regex=False) #remove percentage sign
            .str.extract(r'(\d+\.?\d*)')  #extract the number
            .astype(float) #convert to a float
        )

    #drop rows with an invalid date
    ii_clean.dropna(subset=['Recorded Date'], inplace=True)

    #filter out massive values outside 0-100 range
    ii_clean = ii_clean[
        ((ii_clean['Tetrahydrocannabinol (THC)'].isna()) | ((ii_clean['Tetrahydrocannabinol (THC)'] >= 0) & (ii_clean['Tetrahydrocannabinol (THC)'] <= 100))) &
        ((ii_clean['Cannabidiols (CBD)'].isna()) | ((ii_clean['Cannabidiols (CBD)'] >= 0) & (ii_clean['Cannabidiols (CBD)'] <= 100)))
    ]

    #group by month
    ii_clean['Month'] = ii_clean['Recorded Date'].dt.to_period('M') #convert to month period
    monthly_avg = ii_clean.groupby('Month')[['Tetrahydrocannabinol (THC)', 'Cannabidiols (CBD)']].mean().reset_index() #group by month and calculate mean
    monthly_avg['Month'] = monthly_avg['Month'].dt.to_timestamp() #convert month period back to timestamp

    #plot
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=monthly_avg, x='Month', y='Tetrahydrocannabinol (THC)', label='THC (%)', marker='o', color='green')
    sns.lineplot(data=monthly_avg, x='Month', y='Cannabidiols (CBD)', label='CBD (%)', marker='o', color='blue')

    plt.title('New Product THC & CBD Potency Over Time', fontsize=14)
    plt.xlabel('Time', fontsize=14)
    plt.ylabel('Potency (%)', fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    #save the figure
    plt.savefig("images/vis_two.png")
    plt.show()

#Alex Boyce
#vis_three
#uses: AA
#aggregates retail sales by month and product type
#pivots the data for a stacked area chart
def vis_Three():
    print("Vis Three: Monthly Cannabis Sales Volume by Product Category")

    AA = pd.read_csv("data/AA_Cannabis_Retail_Products_Sold_by_Product_Type.csv")
    print_Head(AA, "AA_Cannabis_Retail_Products_Sold_by_Product_Type")

    #set datetime
    AA["Month Ending"] = pd.to_datetime(AA["Month Ending"])

    #group by month and type
    grouped = AA.groupby(["Month Ending", "Product Type"])["Retail Sales Amount"].sum().reset_index()

    #pivot for plot
    pivot = grouped.pivot(index="Month Ending", columns="Product Type", values="Retail Sales Amount").fillna(0)

    #setup plot figure
    plt.figure(figsize=(16, 6))

    #stackplot the data
    plt.stackplot(
        pivot.index,
        pivot.T.values,
        labels=pivot.columns,
        alpha=0.85
    )

    #format x axis for month
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.xticks(rotation=45, fontsize=14)

    #format y axis
    plt.gca().yaxis.set_major_formatter('${x:,.0f}')  # Format y-axis as currency
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Ensure y-axis ticks are integers
    plt.yticks(fontsize=14)

    #rest of the plotting
    plt.title("Monthly Cannabis Sales Volume by Product Category")
    plt.xlabel("Month", fontsize=14)
    plt.ylabel("Total Retail Sales ($)", fontsize=14)
    plt.legend(title="Product Type", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=14)
    plt.tight_layout()
    #save the figure
    plt.savefig("images/vis_three.png")
    plt.show()


#Alex Boyce
#vis_Seven
#uses: FF
def vis_Seven():
    print("Cannabis Retail Sales by Week Ending with Trend and Moving Average")

    #load and sort data
    FF = pd.read_csv("data/FF_Cannabis_Retail_Sales_by_Week_Ending.csv")
    print_Head(FF, "FF_Cannabis_Retail_Sales_by_Week_Ending")

    FF["Week Ending"] = pd.to_datetime(FF["Week Ending"])
    FF = FF.sort_values("Week Ending")

    #identify first and last week per month
    FF["YearMonth"] = FF["Week Ending"].dt.to_period("M")
    first_weeks = FF.groupby("YearMonth")["Week Ending"].min()
    last_weeks = FF.groupby("YearMonth")["Week Ending"].max()

    #create color list based on first/last weeks
    bar_colors = []
    for date in FF["Week Ending"]:
        if date in first_weeks.values:
            bar_colors.append("purple")
        elif date in last_weeks.values:
            bar_colors.append("blue")
        else:
            bar_colors.append("seagreen")

    #equally space the bars
    x_pos = np.arange(len(FF))

    #prepare figure
    fig, ax = plt.subplots(figsize=(24, 8))

    #plot bars
    bars = ax.bar(x_pos, FF["Adult-Use Retail Sales"], width=0.6,
                  color=bar_colors, edgecolor="black", linewidth=0.5)

    #add date labels on top of bars
    for xpos, bar, date in zip(x_pos, bars, FF["Week Ending"]):
        height = bar.get_height()
        ax.text(
            xpos,
            height + 10000,
            date.strftime('%b %d'),
            ha='center', va='bottom', fontsize=12, rotation=90
        )

    #red linear trend line
    y = FF["Adult-Use Retail Sales"].values
    coef = np.polyfit(x_pos, y, 1)
    trend = np.poly1d(coef)
    ax.plot(x_pos, trend(x_pos), color='red', linewidth=4, label='Trend (Linear)')

    #Orange moving average line over a 4 week window
    FF["MA_4"] = FF["Adult-Use Retail Sales"].rolling(window=4).mean()
    ax.plot(x_pos, FF["MA_4"], color='orange', linewidth=4, label='4-Week Moving Avg')

    #format x axis with date labels
    ax.set_xticks(x_pos[::2])  # every other label
    ax.set_xticklabels(FF["Week Ending"].dt.strftime('%b %d')[::2], rotation=45)

    #set labels and formatting
    ax.set_title("          Cannabis Retail Sales by Week", fontsize=16)
    ax.set_xlabel("Week Ending")
    ax.set_ylabel("Sales ($)", fontsize=14)
    ax.yaxis.set_major_formatter('${x:,.0f}')
    ax.legend()

    #remove whitespace around the bars
    plt.tight_layout()
    ax.set_xlim(-0.5, len(FF) - 0.5)

    #save the figure
    plt.savefig("images/vis_seven.png")
    plt.show()


# Kyle Dennewith
# This is Medically Endorsed Cannabis Facilities and Social Equity Score by County 3D ScatterPlot.
def vis_Four():
    # Taking the tuples from the medicallyEndorsedRetailers DataFrame with the string 'ACTIVE (ISSUED)'. "Unnamed: 4" is referencing the column.
    endorsedStatus = medicallyEndorsedRetailers[medicallyEndorsedRetailers['Unnamed: 4'] == 'ACTIVE (ISSUED)']
    # Making a new DataFrame to store COUNT(*) of tuples by the grouping attribute 'Unnamed: 11', which is referencing Counties. Renaming column for comparisons with socialEquityScores table.
    endorsedCounties = (
        endorsedStatus['Unnamed: 11'].value_counts().reset_index().rename(columns={'Unnamed: 11': 'County'}))
    # Sorting the values alphabetically in County column for quicker comparisons.
    endorsedCounties.sort_values('County', inplace=True)
    # Doing a left join into the SES table since it contains more County tuples.

    mergedCountiesTables = pd.merge(
        socialEquityScores,  # Table I'm merging into.
        endorsedCounties,  # Table I'm merging
        on='County',  # Merging using the County column
        how='left'  # Left joining the tables.
    ).fillna({'count': 0})  # Replacing NaN values with 0.

    # Making the Figure for scatter3D object.
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        hovertemplate="<b>County:</b> %{y}<br><b>Score:</b> %{x}<br><b>Facilities:</b> %{z}<extra></extra>",
        # For the hoverover labels.
        x=mergedCountiesTables['Lowest Score'],  # x-axis: Social Equity Scores for Counties
        y=mergedCountiesTables['County'],  # y-axis: Washington Counties
        z=mergedCountiesTables['count'],  # z-axis: Amount of Facilities per county
        mode="markers",  # display as points
        marker=dict(
            size=8,  # marker size
            color=np.where(
                # Directly mapping the colors using the Social Equity Scores for a scale. Lower: Green, Mid: Yellow, Else: Red.
                mergedCountiesTables['Lowest Score'] <= 100, 'green',
                np.where(
                    mergedCountiesTables['Lowest Score'] <= 200, 'yellow',
                    'red'
                )
            ),  # mapping the school colors I mapped up above to respective schools GP and MS.
            opacity=0.8  # marker opacity
        ),
        name='"Counties'
    ))

    fig.update_layout(
        title="Medically Endorsed Cannabis Facilities and Social Equity Score by County",
        scene=dict(
            xaxis_title="Social Equity Score",
            yaxis_title="County Name",
            zaxis_title="Number of Medically Endorsed Cannabis Facilities",
            xaxis=dict(
                range=[mergedCountiesTables['Lowest Score'].min() - 10,  # Add padding to left (0 - 10)
                       mergedCountiesTables['Lowest Score'].max() + 10],  # Add padding to right (max + 10)
                tickfont=dict(size=10, family="Times New Roman"),
                titlefont = dict(family="Times New Roman", size=14),
            ),
            yaxis=dict(
                tickmode='array',
                tickvals=mergedCountiesTables['County'].index,  # Position for every county using the index position
                ticktext=mergedCountiesTables['County'].unique(),  # Label for every county using unique county names
                tickangle=-45,  # Rotated for readability
                tickfont=dict(size=10, family="Times New Roman"),
                titlefont=dict(family="Times New Roman", size=14),
            ),
            zaxis=dict(
                tickfont=dict(size=10, family="Times New Roman"),
                titlefont=dict(family="Times New Roman", size=14),
            )
        ),
        width=1200,
        height=1200,
        margin=dict(l=100, r=50, b=100, t=50)
    )
    fig.show()

# Kyle Dennewith
# Washington Counties: Police Activity and Social Equity Color/Icon Map.
def vis_Five():
    enforcementVisits = pd.read_csv('data/Cannabis_Enforcement_Visits_04152025.csv')  # Loading the dataset from csv.
    washingtonCounties = gpd.read_file('zip://data/WA_COUNTY_Boundaries.zip')  # Downloaded this from the https://geo.wa.gov/datasets website for Washington County boundary data.
    washingtonCounties['County'] = washingtonCounties['JURISDIC_2'].str.upper()  # Added to match data in the mergedEnforcementCounties DataFrame so that the colors can map correctly.
    enforcementNumbers = enforcementVisits['C4'].value_counts().reset_index()  # Creating a new table using the data and counting up amount of enforcement visits per county using the C4 column in the enforcementVisits dataframe.
    enforcementNumbers.columns = ['County','totalCount']  # Naming the columns of the newly made dataframe so that I can make it union compatible for the merge.
    mergedEnforcementCounties = pd.merge(
        socialEquityScores,  # Table I'm merging into.
        enforcementNumbers,  # Table I'm merging
        on='County',  # Merging using the County column
        how='left'  # Left joining the tables.
    )
    # Making a new column called color in the merged tables to assign colors using np.where.
    # If the Social Equity Score is NaN or <= 100 the county is green, if the Social Equity Score is above 100 and below 200 then the county is orange, else the county is red.
    mergedEnforcementCounties['color'] = np.where(
        mergedEnforcementCounties['Lowest Score'].isna() | (mergedEnforcementCounties['Lowest Score'] <= 100),
        'green',
        np.where(
            (mergedEnforcementCounties['Lowest Score'] <= 200) & (mergedEnforcementCounties['Lowest Score'] > 100),
            'orange',
            'red'
        )
    )
    # Sorting for the colors to be correctly applied.
    mergedEnforcementCounties.sort_values('County')
    washingtonCounties = washingtonCounties.iloc[washingtonCounties['County'].argsort()]

    mergedEnforcementData = pd.merge(
        mergedEnforcementCounties,  # Table I'm merging into.
        washingtonCounties,  # Table I'm merging
        on='County',  # Merging using the County column
        how='left'  # Left joining the tables.
    )
    mergedMapData = pd.merge(
        washingtonCounties,  # Table I'm merging into.
        enforcementNumbers,  # Table I'm merging
        on='County',  # Merging using the County column
        how='left'  # Left joining the tables.
    )
    mergedMapData = mergedMapData.to_crs("EPSG:4326")

    # Creating the figure and axis to put the geometry of my map on.
    fig, ax = plt.subplots(figsize=(12, 10))
    # Plotting the counties out with the colormap from the mergedEnforcementCounties DataFrame.
    mergedMapData.plot(ax=ax, color=mergedEnforcementData['color'].values, linewidth=1, edgecolor='black')
    badgePNG = plt.imread('data/policeBadge.png')  # Reading the badge PNG image from my directory.

    # This lambda function creates AnnotationBbox objects with and OffsetImage object inside of them that will hold the actual image, the Annotation box is used for automatic alignment using the geometry table that is in my washingtonCounties data. Same logic as the last lambda except instead of text, an image. If there is no police activity in the area for cannabis related reasons then the geometry will be left empty instead. I don't include a frame to keep the PNG aspect on the image with a transparent background. Moving it down using centroid.y - 0.1. Had to change to Lon/Lat ESPG:4326 for conversion. Adding artists to the mapData using the add_artist function.
    mergedMapData.apply(lambda x: ax.add_artist(
        AnnotationBbox(OffsetImage(badgePNG, zoom=0.0009 * x.totalCount if pd.notna(x.totalCount) else 0.02),
                       xy=(x.geometry.centroid.x, (x.geometry.centroid.y - 0.1)),
                       frameon=False)) if not x.geometry.is_empty else None, axis=1)

    # Lambda function to iterate through the centroids of each counties geometry and add the 'County' as text
    mergedMapData.apply(
        lambda x: ax.annotate(x.County, xy=x.geometry.centroid.coords[0], ha='center', fontsize=16, color='white',
                              family="Times New Roman",
                              path_effects=[
                                  patheffects.withSimplePatchShadow(offset=(1, -2), shadow_rgbFace='gray', alpha=0.3),
                                  patheffects.withStroke(linewidth=0.35, foreground='black')]), axis=1)

    plt.title("Washington Counties: Police Activity and Social Equity")  # The title of the Geodata visual
    plt.tight_layout()
    plt.show()


# Kyle Dennewith
# Washington Counties: Cannabis Related Sales by County/Year.
def vis_Six():
    # Skipping the first row in each of the excel sheets so I can not use Unnamed: 3 as a header
    retailWA1819 = pd.read_excel('data\RetailByCounty20182024.xlsx', sheet_name=['FY18', 'FY19'],skiprows=1)  # Data includes sales from 2018 and 2019 data to see how sales were doing before isolation.
    retailWA2120 = pd.read_excel('data\RetailByCounty20182024.xlsx', sheet_name=['FY20', 'FY21'],skiprows=1)  # Data include 2020 and 2021 data, which was the COVID years to compare with 2 years before and afterward.
    retailWA2223 = pd.read_excel('data\RetailByCounty20182024.xlsx', sheet_name=['FY22', 'FY23'],skiprows=1)  # Data includes sales from 2022 and 2023 this will show the advent effect of sales/revenue.

    # Each dataset in a separate dataframe.
    retail2018 = retailWA1819['FY18']
    retail2019 = retailWA1819['FY19']
    retail2020 = retailWA2120['FY20']
    retail2021 = retailWA2120['FY21']
    retail2022 = retailWA2223['FY22']
    retail2023 = retailWA2223['FY23']

    # Summing up each of the years total sales
    total2018 = retail2018['Total Sales'].sum()
    total2019 = retail2019['Total Sales'].sum()  # Dec 2019 COVID first appears
    total2020 = retail2020['Total Sales'].sum()  # COVID Lockdowns started in March 2020 in the USA
    total2021 = retail2021['Total Sales'].sum()  # Still Lockdowns and COVID happenings
    total2022 = retail2022['Total Sales'].sum()  # Lockdowns have ended
    total2023 = retail2023['Total Sales'].sum()
    # A dataframe to hold all of my sums with the header as the year.
    totalDF = pd.DataFrame({
        'Year': ['2018', '2019', '2020', '2021', '2022', '2023'],
        'totalSales': [total2018, total2019, total2020, total2021, total2022, total2023],
    })

    # Wanted to make more datasets after realizing there was no month column.
    # Getting the top 5 counties of each year to see extra variation throughout the years for pinpointing top county fluctuations over the years, if any.
    # 2018 top 5 DF Setup
    topCounties2018 = retail2018.nlargest(5, 'Total Sales')
    topCounties2018 = topCounties2018.drop(index=38)  # Unneeded data
    topCounties2018['County'] = topCounties2018['County'].str[:4]
    # 2019 top 5 DF Setup
    topCounties2019 = retail2019.nlargest(5, 'Total Sales')
    topCounties2019 = topCounties2019.drop(index=38)
    topCounties2019['County'] = topCounties2019['County'].str[:4]
    # 2020 top 5 DF setup
    topCounties2020 = retail2020.nlargest(5, 'Total Sales')
    topCounties2020 = topCounties2020.drop(index=38)
    topCounties2020['County'] = topCounties2020['County'].str[:4]
    # 2021 top 5 DF setup
    topCounties2021 = retail2021.nlargest(5, 'Total Sales')
    topCounties2021 = topCounties2021.drop(index=38)
    topCounties2021['County'] = topCounties2021['County'].str[:4]
    # 2022 top 5 DF setup
    topCounties2022 = retail2021.nlargest(5, 'Total Sales')
    topCounties2022 = topCounties2022.drop(index=38)
    topCounties2022['County'] = topCounties2022['County'].str[:4]
    # 2023 top 5 DF setup
    topCounties2023 = retail2023.nlargest(5, 'Total Sales')
    topCounties2023 = topCounties2023.drop(index=38)
    topCounties2023['County'] = topCounties2023['County'].str[:4]

    # Getting both the year 2018 and 2019 top 5 Counties by the amount of tax collected from the sales income. pre
    topTaxCounties2018 = retail2018.nlargest(5, 'Excise Tax')
    topTaxCounties2019 = retail2019.nlargest(5, 'Excise Tax')
    # using concat to merge the tables, should be safe since they are identical format.
    topTaxCounties1819 = pd.concat([topTaxCounties2018, topTaxCounties2019])
    # Dropping a Null row with the index label 38
    topTaxCounties1819 = topTaxCounties1819.drop(index=38)
    topTaxCounties1819['County'] = topTaxCounties1819['County'].str[:4]

    # Getting both the year 2022 and 2023 top 5 Counties by the amount of tax collected from the sales income. post
    topTaxCounties2022 = retail2021.nlargest(5, 'Excise Tax')
    topTaxCounties2023 = retail2023.nlargest(5, 'Excise Tax')
    topTaxCounties2223 = pd.concat([topTaxCounties2022, topTaxCounties2023])
    # Dropping a Null row with the index label 38
    topTaxCounties2223 = topTaxCounties2023.drop(index=38)
    topTaxCounties2223['County'] = topTaxCounties2223['County'].str[:4]

    fig, ax = plt.subplots(3, 3, figsize=(9,
                                          9))  # Making a plot with a 3 x 3 subplot formation with the first input 3 nrows, and 3 ncolumns, along with the figure size.
    plt.subplots_adjust(wspace=0.30,
                        hspace=0.30)  # Adjusting the width space and height space a bit for padding around each other the graphs.

    # First Graph: Top Sales Counties 2018
    ax[0, 0].bar(topCounties2018['County'], topCounties2018['Total Sales'], data=topCounties2018)
    ax[0, 0].set_title('Top 4 County Sales (2018)', fontsize=9, fontfamily='monospace', color='blue')
    ax[0, 0].set_ylabel('Total Sales', fontsize=8, fontfamily='serif', fontweight='bold', color='green', labelpad=-1)
    ax[0, 0].set_xlabel('County', fontsize=8, labelpad=2, fontfamily='serif', fontweight='bold', color='purple')
    ax[0, 0].tick_params(axis='y', pad=-3)
    ax[0, 0].set_ylim(0, 400000000)
    # Just need the x value (input) so used an underscore to not include the usage of the second variable since this lambda function just needs to use x and FuncFormatter takes a tick value and position value for parameters. Lambda is used because FuncFormatter as it name gives away, takes in a function.
    # Using 1e6 and M for millions formatting using matplotlibs FuncFormatter.
    ax[0, 0].yaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f"${x / 1e6:,.0f}M"))
    # Second Graph: Top Sales Counties 2019
    ax[0, 1].bar(topCounties2019['County'], topCounties2019['Total Sales'], data=topCounties2019)
    ax[0, 1].set_title('Top 4 County Sales (2019)', fontsize=9, fontfamily='monospace', color='blue')
    ax[0, 1].set_ylabel('Total Sales', fontsize=8, fontfamily='serif', fontweight='bold', color='green', labelpad=-1)
    ax[0, 1].set_xlabel('County', fontsize=8, labelpad=2, fontfamily='serif', fontweight='bold', color='purple')
    ax[0, 1].yaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f"${x / 1e6:,.0f}M"))
    ax[0, 1].set_ylim(0, 400000000)
    ax[0, 1].tick_params(axis='y', pad=-3)
    # Third Graph: Top Sales Counties 2020
    ax[0, 2].bar(topCounties2020['County'], topCounties2020['Total Sales'], data=topCounties2020)
    ax[0, 2].set_title('Top 4 County Sales (2020)', fontsize=9, fontfamily='monospace', color='blue')
    ax[0, 2].set_ylabel('Total Sales', fontsize=8, fontfamily='serif', fontweight='bold', color='green', labelpad=-1)
    ax[0, 2].set_xlabel('County', fontsize=8, labelpad=2, fontfamily='serif', fontweight='bold', color='purple')
    ax[0, 2].yaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f"${x / 1e6:,.0f}M"))
    ax[0, 2].set_ylim(0, 400000000)
    ax[0, 2].tick_params(axis='y', pad=-3)
    # Fourth Graph: Top Sales Counties 2021
    ax[1, 0].bar(topCounties2021['County'], topCounties2021['Total Sales'], data=topCounties2021)
    ax[1, 0].set_title('Top 4 County Sales (2021)', fontsize=9, fontfamily='monospace', color='blue')
    ax[1, 0].set_ylabel('Total Sales', fontsize=8, fontfamily='serif', fontweight='bold', color='green', labelpad=-1)
    ax[1, 0].set_xlabel('County', fontsize=8, labelpad=2, fontfamily='serif', fontweight='bold', color='purple')
    ax[1, 0].yaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f"${x / 1e6:,.0f}M"))
    ax[1, 0].set_ylim(0, 400000000)
    ax[1, 0].tick_params(axis='y', pad=-3)
    # Fifth Graph: Top Sales Counties 2022
    ax[1, 1].bar(topCounties2022['County'], topCounties2022['Total Sales'], data=topCounties2022)
    ax[1, 1].set_title('Top 4 County Sales (2022)', fontsize=9, fontfamily='monospace', color='blue')
    ax[1, 1].set_ylabel('Total Sales', fontsize=8, fontfamily='serif', fontweight='bold', color='green', labelpad=-1)
    ax[1, 1].set_xlabel('County', fontsize=8, labelpad=2, fontfamily='serif', fontweight='bold', color='purple')
    ax[1, 1].yaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f"${x / 1e6:,.0f}M"))
    ax[1, 1].set_ylim(0, 400000000)
    ax[1, 1].tick_params(axis='y', pad=-3)
    # Sixth Graph: Top Sales Counties 2023
    ax[1, 2].bar(topCounties2023['County'], topCounties2023['Total Sales'], data=topCounties2023)
    ax[1, 2].set_title('Top 4 County Sales (2023)', fontsize=9, fontfamily='monospace', color='blue')
    ax[1, 2].set_ylabel('Total Sales', fontsize=8, fontfamily='serif', fontweight='bold', color='green', labelpad=-1)
    ax[1, 2].set_xlabel('County', fontsize=8, labelpad=2, fontfamily='serif', fontweight='bold', color='purple')
    ax[1, 2].yaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f"${x / 1e6:,.0f}M"))
    ax[1, 2].set_ylim(0, 400000000)
    ax[1, 2].tick_params(axis='y', pad=-3)
    # Seventh Graph: Top Sales per Year (2018-2023)
    ax[2, 0].bar(totalDF['Year'], totalDF['totalSales'], data=totalDF)
    ax[2, 0].set_title('Total Sales by Year', fontsize=9, fontfamily='monospace', color='blue')
    ax[2, 0].set_ylabel('Total Sales', fontsize=8, fontfamily='serif', fontweight='bold', color='green', labelpad=-1)
    ax[2, 0].set_xlabel('Year', fontsize=8, labelpad=2, fontfamily='serif', fontweight='bold', color='red')
    # Using B for Billions and 1e9
    ax[2, 0].yaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f"${x / 1e9:,.1f}B"))
    ax[2, 0].set_ylim(0, 3000000000)
    ax[2, 0].tick_params(axis='y', pad=-3)
    ax[2, 0].tick_params(axis='x', labelsize=8)

    # Eighth Graph: Top County Cannabis Tax Incomes (2018/2019)
    ax[2, 1].bar(topTaxCounties1819['County'], topTaxCounties1819['Total Sales'], data=topTaxCounties1819)
    ax[2, 1].set_title('Top 4 Cannabis Tax Incomes (PreC)', fontsize=7, fontfamily='monospace', color='blue')
    ax[2, 1].set_ylabel('Total Taxes', fontsize=8, fontfamily='serif', fontweight='bold', color='green', labelpad=-1)
    ax[2, 1].set_xlabel('County', fontsize=8, labelpad=2, fontfamily='serif', fontweight='bold', color='purple')
    # Using B for Billions and 1e9
    ax[2, 1].yaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f"${x / 1e6:,.0f}M"))
    ax[2, 1].set_ylim(0, 400000000)
    ax[2, 1].tick_params(axis='y', pad=-3)

    # Ninth Graph: Top County Cannabis Tax Incomes (2022/2023)
    ax[2, 2].bar(topTaxCounties2223['County'], topTaxCounties2223['Total Sales'], data=topTaxCounties2223)
    ax[2, 2].set_title('Top 4 Cannibas Tax Incomes (PostC)', fontsize=7, fontfamily='monospace', color='blue')
    ax[2, 2].set_ylabel('Total Taxes', fontsize=8, fontfamily='serif', fontweight='bold', color='green', labelpad=-1)
    ax[2, 2].set_xlabel('County', fontsize=8, labelpad=2, fontfamily='serif', fontweight='bold', color='purple')
    # Using B for Billions and 1e9
    ax[2, 2].yaxis.set_major_formatter(tick.FuncFormatter(lambda x, _: f"${x / 1e6:,.0f}M"))
    ax[2, 2].set_ylim(0, 400000000)
    ax[2, 2].tick_params(axis='y', pad=-3)

    plt.show()


def main():

    #Visualizations:
    vis_One()
    vis_Two()
    vis_Three()

    vis_Seven()

    vis_Four()
    vis_Five()
    vis_Six()

main()