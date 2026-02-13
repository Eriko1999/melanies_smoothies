import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

# --- Snowflake接続 ---
@st.cache_resource
def create_session():
    return Session.builder.getOrCreate()

session = create_session()

# --- UI ---
name_on_order = st.text_input("Name on Smoothie:")

my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#Convert the Snowflake Dataframe to a Pandas Dataframe so we can use the LOC Function
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"],
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
        
            search_on = pd_df.loc[
                pd_df["FRUIT_NAME"] == fruit_chosen,
                "SEARCH_ON"
            ].iloc[0]    

            search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
            
            st.subheader(fruit_chosen + " Nutrition Information")
        
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )
        
            st.dataframe(
                smoothiefroot_response.json(),
                use_container_width=True,
            )
