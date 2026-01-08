
# Import python packages.
import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title("🥤 Customize Your Smoothie! 🥤") 

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

st.write("""Choose the fruits you want in your custom Smoothie!""")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options (ensure column names match exactly as stored)
my_dataframe = (
    session.table("smoothies.public.fruit_options")
           .select(col('FRUIT_NAME'), col('SEARCH_ON'))
)
pd_df = my_dataframe.to_pandas()

# Use the FRUIT_NAME column as the selection options
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

ingredients_string = ''

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        # Find the SEARCH_ON value for the chosen fruit safely
        row = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']
        if row.empty:
            st.warning(f"No search value found for '{fruit_chosen}'.")
            continue

        search_on = row.iloc[0]  # <-- correct variable name

        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Use f-string so the variable is interpolated
        url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        try:
            smoothiefroot_response = requests.get(url, timeout=10)
            smoothiefroot_response.raise_for_status()
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        except requests.RequestException as e:
            st.error(f"Failed to fetch nutrition info for {fruit_chosen}: {e}")

# Build the insert statement (consider using parameterized SQL to avoid injection)
my_insert_stmt = f"""
INSERT INTO smoothies.public.orders (ingredients, name_on_order)
VALUES ('{ingredients_string}', '{name_on_order}')
"""

time_to_insert = st.button('Submit Order')

if time_to_insert: 
    # Optional: validate inputs before inserting
    if not name_on_order:
        st.error("Please enter the name on your smoothie before submitting.")
    else:
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
