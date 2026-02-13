import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

# --- Snowflake接続 ---
@st.cache_resource
def create_session():
    return Session.builder.configs(st.secrets["snowflake"]).create()

session = create_session()

# --- UI ---
name_on_order = st.text_input("Name on Smoothie:")

my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
    .to_pandas()
)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe["FRUIT_NAME"],
    max_selections=5,
)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    if st.button("Submit Order"):
        session.sql(
            "insert into smoothies.public.orders(ingredients, name_on_order) values (?, ?)",
            params=[ingredients_string, name_on_order],
        ).collect()

        st.success("Your Smoothie is ordered!", icon="✅")

        # 🔹 API部分
        for fruit_chosen in ingredients_list:
        
            search_value = my_dataframe.loc[
                my_dataframe["FRUIT_NAME"] == fruit_chosen,
                "SEARCH_ON"
            ].values[0]
        
            st.subheader(fruit_chosen + " Nutrition Information")
        
            smoothiefroot_response = requests.get(
                "https://my.smoothiefroot.com/api/fruit/" + search_value
            )
        
            st.dataframe(
                smoothiefroot_response.json(),
                use_container_width=True,
            )
