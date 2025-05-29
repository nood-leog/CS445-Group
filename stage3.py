#stage3.py


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.graph_objects as go
import numpy as np

#ignore warnings
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)


#load the data
AA = pd.read_csv("data/AA_Cannabis_Retail_Products_Sold_by_Product_Type.csv") #Used by vis_Three()
BB = pd.read_csv("data/BB_Average_Price_Per_Gram_of_Usable_Cannabis.csv")
CC = pd.read_csv("data/CC_Cannabis_Retailers1.csv")
DD = pd.read_csv("data/DD_Licensed_Cannabis_and_Medical_Marijuana_Retail_Locations.csv")
EE = pd.read_csv("data/EE_Cannabis_Brand_Registrations_By_Type.csv")
FF = pd.read_csv("data/FF_Cannabis_Retail_Sales_by_Week_Ending.csv")
GG = pd.read_csv("data/GG_Number_of_Medical_Marijuana_Registrants_by_Month.csv")
HH = pd.read_csv("data/HH_Medical_Marijuana_Dispensary_License1.csv")
II = pd.read_csv("data/II_Medical_MarijuanaCannabis_Brands_with_Chemical_Composition1.csv")
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
# Alex Boyce
def vis_One():
    print("Vis One")
# Alex Boyce
def vis_Two():
    print("Vis Two")


#vis_three uses: AA. Alex Boyce
def vis_Three():
    print("Vis Three")

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
    plt.show()
    #save the figure
    plt.savefig("images/vis_three.png")

# This is Medically Endorsed Cannabis Facilities and Social Equity Score by County 3D ScatterPlot. Kyle Dennewith.
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


def main():

    #print the head of everything - Intended for debugging
    print_Head(AA, "AA_Cannabis_Retail_Products_Sold_by_Product_Type")
    print_Head(BB, "BB_Average_Price_Per_Gram_of_Usable_Cannabis")
    print_Head(CC, "CC_Cannabis_Retailers1")
    print_Head(DD, "DD_Licensed_Cannabis_and_Medical_Marijuana_Retail_Locations")
    print_Head(EE, "EE_Cannabis_Brand_Registrations_By_Type")
    print_Head(FF, "FF_Cannabis_Retail_Sales_by_Week_Ending")
    print_Head(GG, "GG_Number_of_Medical_Marijuana_Registrants_by_Month")
    print_Head(HH, "HH_Medical_Marijuana_Dispensary_License1")
    print_Head(II, "II_Medical_MarijuanaCannabis_Brands_with_Chemical_Composition1")

    #Visualizations:
    vis_One()
    vis_Two()
    vis_Three()
    vis_Four()


main()




'''
VIS ONE:
#Average Cannabis Sales in Connecticut by City/Town (20XX)]

Relevant Data: FF, DD, CC

We will use a choropleth map of Connecticut where each city/town is
associated with a colored square based on its average cannabis sales volume
over the span of a year. Areas with higher sales will be shaded in darker
green, while areas with lower sales will be shaded in darker blue, with a
gradient of colors in between

Rationale:
This visualization would address the question: “Where are cannabis sales
concentrated within the state, and are there significant regional sales
disparities in the legal cannabis market?”

Expected Insights:
This visualization would help us understand if sales are clustered in urban
centers, near state borders, or if other geographic factors influence sales
volume.

VIS TWO:
#THC Potency vs. Avg Price Per Gram]

Relevant Data: II, BB

We will use a Scatter Plot of THC Potency vs. Avg Price Per Gram and
include color coding to differentiate between Product Type.

Rationale:
This visualization would show the market valuation of potency and whether
consumers are paying a consistent premium for higher THC levels.
"Is there a strong correlation between THC potency and price in the
Connecticut cannabis market, and does this relationship differ by product
type?"
Expected Insights:
We could be able to show the relationship between potency and price. By
including product type, this also could show some types with a stronger price-
potency correlation than others.

VIS THREE:
Product Sales by Type in Connecticut (Quarterly)]

Relevant Data: AA, FF, II

We will use a stacked area chart where the x-axis represents time in quarters,
and the y axis represents total sales volume. Each colored area represents a
specific cannabis product category, and the height of each colored segment
indicates the "popularity" of that product category at that point in time.

Rationale:
This visualization would be able to illustrate changes in the relative popularity
and demand for different product categories. It clearly shows which categories
are growing, shrinking, or maintaining a stable share of the market. It would
also show both category growth and overall market growth.
"How have consumer preferences for different types of cannabis products
shifted in Connecticut over the past X years?"

Expected Insights:
With this visualization, we would be able to identify which product categories
initially dominated the market and whether their dominance has persisted
been overtaken by another market trend. This would also show shifting
consumer consumption, whether that be due to seasonal usage year round, or
regulatory changes affecting certain product types.


'''

