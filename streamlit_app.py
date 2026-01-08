# Import python packages.
import streamlit as st
# Snowflake Snowpark (in-Snowflake streamlit runtime)
from snowflake.snowpark.functions import col
import os

# Write directly to the app.
st.title(f"🥤 Customize Your Smoothie! 🥤") 

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# display dataframe 
# st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect('Choose up to 5 ingredients:'
                                 , my_dataframe,
                                  max_selections = 5
                                 )

ingredients_string = ''

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    
    # st.write(ingredients_string)

my_insert_stmt = f"""
INSERT INTO smoothies.public.orders (ingredients, name_on_order)
VALUES ('{ingredients_string}', '{name_on_order}')
"""
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response.json())
sf_df= st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
#st.write(my_insert_stmt)

time_to_insert = st.button('Submit Order')

if time_to_insert: 
    session.sql(my_insert_stmt).collect()

    st.success(f"✅Your Smoothie is ordered, {name_on_order}!") 
    
