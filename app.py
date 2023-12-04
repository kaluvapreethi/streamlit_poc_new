import pandas as pd
from databricks import sql
import streamlit as st
import configparser
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient


def authenticate_azure(config):
  TENANT = config_file["AzureServicePrinciple"]["TENANT"]
  CLIENT_ID = config_file["AzureServicePrinciple"]["CLIENT_ID"]
  CLIENT_SECRET = config_file["AzureServicePrinciple"]["CLIENT_SECRET"]
  VAULT_URL = config_file["AzureServicePrinciple"]["VAULT_URL"]

  credential = ClientSecretCredential(TENANT,CLIENT_ID,CLIENT_SECRET)
  client = SecretClient(vault_url=VAULT_URL, credential=credential)
  return client


def fetch_data_from_db(config):
  
  client = authenticate_azure(config)
  http_path = client.get_secret("http-path").value
  server_hostname = client.get_secret("server-hostname").value
  access_token = client.get_secret("access-token").value

  with sql.connect(server_hostname = server_hostname,
                    http_path       = http_path,
                    access_token    = access_token) as connection:

    with connection.cursor() as cursor:
      res = cursor.execute("SELECT * FROM member_data LIMIT 10")

      df = pd.DataFrame(res.fetchall())
      df.columns=[x[0] for x in res.description]
      # print(df)
      st.dataframe(df)
      st.write("Displaying only top 10 rows")


if __name__=="__main__": 
  st.set_page_config(page_title="DB data", layout="wide")
  config_file = configparser.ConfigParser()
  config_file.read("configurations.ini")

  with st.container():
      st.subheader("DB POC")
      st.title("Fetching data from DB tables")
      st.write("POC")

  fetch_data_from_db(config_file)



