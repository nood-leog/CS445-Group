#stage3.py


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

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

def print_head(df, name):
    #print name of the dataframe
    print(f"DataFrame: {name}")
    #print the head
    print(df.head())
    #print column names
    print("Columns:", df.columns.tolist())
    print("\n")

def vis_One():
    print("Vis One")

def vis_Two():
    print("Vis Two")


#vis_three uses: AA
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


def main():

    #print the head of everything - Intended for debugging
    print_head(AA, "AA_Cannabis_Retail_Products_Sold_by_Product_Type")
    print_head(BB, "BB_Average_Price_Per_Gram_of_Usable_Cannabis")
    print_head(CC, "CC_Cannabis_Retailers1")
    print_head(DD, "DD_Licensed_Cannabis_and_Medical_Marijuana_Retail_Locations")
    print_head(EE, "EE_Cannabis_Brand_Registrations_By_Type")
    print_head(FF, "FF_Cannabis_Retail_Sales_by_Week_Ending")
    print_head(GG, "GG_Number_of_Medical_Marijuana_Registrants_by_Month")
    print_head(HH, "HH_Medical_Marijuana_Dispensary_License1")
    print_head(II, "II_Medical_MarijuanaCannabis_Brands_with_Chemical_Composition1")

    #Visualizations:
    vis_One()
    vis_Two()
    vis_Three()

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

