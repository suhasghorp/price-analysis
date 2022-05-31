'''
# This is the document title

This is some _markdown_.
'''

import os
import streamlit as st
import azure_kv, auth
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from azure.storage.blob import BlobServiceClient
import pandas as pd

st.set_page_config(page_title="Price Analysis", layout="wide")

headerSection = st.container()
mainSection = st.container()
loginSection = st.container()
logOutSection = st.container()

@st.cache
def load_data():
    bloburl = azure_kv.get_secret("bloburl")
    blobkey = azure_kv.get_secret("blobkey")

    service = BlobServiceClient(account_url=bloburl, credential=blobkey)
    prices_client = service.get_blob_client("prices", "prices.csv", snapshot=None)
    holdings_client = service.get_blob_client("prices", "holdings.csv", snapshot=None)

    with open("prices.csv", "wb") as my_blob:
        blob_data = prices_client.download_blob()
        blob_data.readinto(my_blob)

    with open("holdings.csv", "wb") as my_blob:
        blob_data = holdings_client.download_blob()
        blob_data.readinto(my_blob)

    prices_df = pd.read_csv("prices.csv",encoding = 'ISO-8859-1', low_memory=False)
    holdings_df = pd.read_csv("holdings.csv",encoding = 'ISO-8859-1', low_memory=False)
    prices_df = prices_df.apply(lambda x: 'NONE' if isinstance(x, str) and (x.isspace() or not x or x == '') else x)
    prices_df = prices_df[["Primary Asset ID", "Price", "Provider"]]
    prices_df.set_index("Primary Asset ID", inplace=True)
    holdings_df = holdings_df[["Acct Short Name","Account Description", "Primary Asset ID", "Instrument Class Description","Issue Type Description", "Units"]]
    holdings_df.set_index("Primary Asset ID", inplace=True)

    df = holdings_df.join(prices_df, how="inner")
    return df

def show_main_page():
    with mainSection:

        df = load_data()

        st.sidebar.header('Settings')

        kpi1, kpi2, kpi3 = st.columns(3)

        accts_values = df["Acct Short Name"].unique().tolist()
        accounts_select = st.sidebar.selectbox('Account Short Name', accts_values, index=0)

        # add this
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination()
        gb.configure_side_bar()
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
        gridOptions = gb.build()

        df = df[df['Acct Short Name'].isin([accounts_select])]

        #issue_type_values = prices_df['Issue Type Description'].unique().tolist()
        #default_ix = 0
        #issue_type = st.sidebar.selectbox('Issue Type', issue_type_values, index=default_ix)

        kpi1.metric(label = "Metric1", value = 3.5)
        kpi2.metric(label = "Metric2", value = 3200)
        kpi3.metric(label = "Metric3", value = 0.34)

        AgGrid(df, gridOptions=gridOptions,enable_enterprise_modules=True,
                      allow_unsafe_jscode=True,
                      update_mode=GridUpdateMode.SELECTION_CHANGED)


def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False

def show_logout_page():
    loginSection.empty();
    with logOutSection:
        st.button("Log Out", key="logout", on_click=LoggedOut_Clicked)


def LoggedIn_Clicked(userName, password):
    if auth.login(userName, password):
        st.session_state['loggedIn'] = True
    else:
        st.session_state['loggedIn'] = False;
        st.error("Invalid user name or password")

def show_login_page():
    with loginSection:
        if st.session_state['loggedIn'] == False:
            userName = st.text_input (label="", value="", placeholder="Enter your user name")
            password = st.text_input (label="", value="",placeholder="Enter password", type="password")
            st.button ("Login", on_click=LoggedIn_Clicked, args= (userName, password))

with headerSection:
    col1, col2 = st.columns([3,1])
    col1.markdown("# AB Funds Valuations")
    col1.markdown("### Please add description of the website here...")
    #first run will have nothing in session_state
    if 'loggedIn' not in st.session_state:
        st.session_state['loggedIn'] = False
        show_login_page()
    else:
        if st.session_state['loggedIn']:
            show_logout_page()
            show_main_page()
        else:
            show_login_page()