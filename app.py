'''
# This is the document title

This is some _markdown_.
'''

import os
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from azure.storage.blob import BlobServiceClient
import pandas as pd
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

st.set_page_config(page_title="Price Analysis", layout="wide")
#st.title("Price analysis")

st.markdown("# AB Funds Valuations")
st.markdown("### Please add description of the website here...")
st.markdown("### The below grid is just a placeholder while Greg is working on the design")

@st.cache
def load_data():
    keyVaultName = "pricingappkv"
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)
    bloburl = client.get_secret("bloburl").value
    blobkey = client.get_secret("blobkey").value


    service = BlobServiceClient(account_url=bloburl, credential=blobkey)
    blob_client = service.get_blob_client("prices", "prices-mini.csv", snapshot=None)


    with open("prices.csv", "wb") as my_blob:
        blob_data = blob_client.download_blob()
        blob_data.readinto(my_blob)
    prices_df = pd.read_csv("prices.csv",encoding = 'ISO-8859-1', low_memory=False)
    prices_df = prices_df.apply(lambda x: 'NONE' if isinstance(x, str) and (x.isspace() or not x or x == '') else x)
    #os.remove("prices.csv")
    return prices_df

prices_df = load_data()

st.sidebar.header('Settings')

kpi1, kpi2, kpi3 = st.columns(3)

invest_type_values = ['Structured Product', 'Derivatives', 'Equity', 'Debt', 'Unique Assets']
default_ix = invest_type_values.index('Debt')
invest_type = st.sidebar.selectbox('Investment Type', invest_type_values, index=default_ix)

# add this
gb = GridOptionsBuilder.from_dataframe(prices_df)
gb.configure_pagination()
gb.configure_side_bar()
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
gridOptions = gb.build()

prices_df = prices_df[prices_df['Investment Type Description'].isin([invest_type])]

issue_type_values = prices_df['Issue Type Description'].unique().tolist()
default_ix = 0
issue_type = st.sidebar.selectbox('Issue Type', issue_type_values, index=default_ix)

kpi1.metric(label = "Metric1", value = 3.5)
kpi2.metric(label = "Metric2", value = 3200)
kpi3.metric(label = "Metric3", value = 0.34)

AgGrid(prices_df, gridOptions=gridOptions,enable_enterprise_modules=True,
              allow_unsafe_jscode=True,
              update_mode=GridUpdateMode.SELECTION_CHANGED)