import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import ast

# Set the page layout to wide
st.set_page_config(layout="wide")

# Function to convert the players string to a sorted dictionary and then back to a sorted string
def parse_and_sort_players(players_str):
    players_list = ast.literal_eval(players_str)  # Convert string representation of list to an actual list
    players_dict = {k: int(v) for k, v in (item.split(": ") for item in players_list)}  # Create a dictionary
    sorted_players = dict(sorted(players_dict.items(), key=lambda item: item[1], reverse=True))  # Sort the dictionary
    
    sorted_players_str = []
    for k, v in sorted_players.items():
        if k == "DlouhejProvaz":
            sorted_players_str.append(f"**{k}: {v}**")
        else:
            sorted_players_str.append(f"{k}: {v}")
    
    return ", ".join(sorted_players_str)  # Join the list into a single string

# Define the function to load data and create the plots
@st.cache_data(ttl=60)
def load_data():
    # Load the data
    df = pd.read_csv("probihajici_f.csv")
    df.progression = df.progression.apply(lambda x: int(x[:-1]))
    return df

def load_and_display_data():
    df = load_data()
    st.title("Board Game Progression")

    # Define a fixed figure width and height
    fig_width = 8
    fig_height = 0.5

    # Create figure and axis objects outside the loop
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    sections = df["section"].unique()
    for section in sections:
        st.subheader(section.capitalize())
        section_data = df[df["section"] == section]
        
        for index, row in section_data.iterrows():
            col1, col2, col3 = st.columns([2, 5, 9])  # Adjust the ratios as needed
            
            with col1:
                game_name = row['game_names']
                game_url = row['urls']
                st.markdown(f'<a href="{game_url}" style="text-decoration:none;">{game_name}</a>', unsafe_allow_html=True)
            
            with col2:
                # Clear the previous plot
                ax.clear()
                
                # Plot the progression in light green
                ax.barh([0], [row['progression']], color='lightgreen', height=0.3)
                # Plot the remainder in yellow
                ax.barh([0], [100 - row['progression']], left=row['progression'], color='yellow', height=0.3)
                
                ax.set_xlim(0, 100)
                ax.yaxis.set_visible(False)  # Hide the y-axis label
                ax.xaxis.set_visible(False)  # Hide the x-axis labels
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                
                # Add the percentage text only for the light green bars
                ax.text(row['progression'] + 1, 0, f'{int(row["progression"])}%', ha='left', va='center')
                
                st.pyplot(fig)
            
            with col3:
                players_sorted_str = parse_and_sort_players(row['players'])
                st.markdown(players_sorted_str)  # Use st.markdown to render the bold text

# Main function to load and display data
load_and_display_data()

