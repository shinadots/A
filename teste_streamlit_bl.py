pip install -r requirements.txt
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

st.set_page_config(page_title="Dashboard de Trafego Pago", layout="wide")

SHEET_ID = "1VT1WK03ainI-2ILFvoBGNBrsD_Czeck5IBcZbNw_718"  # Pegue da URL do Google Sheets
CREDENTIALS_FILE = "C:/Users/Joao/Downloads/chave.json"  # Credenciais do Google

# --- CONECTAR AO GOOGLE SHEETS ---
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"])
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet("Dados_MetaAds")

# --- CARREGAR OS DADOS ---
data = sheet.get_all_records()

# Tentativa de forÃ§ar a decodificaÃ§Ã£o correta
def clean_data(data):
    cleaned_data = []
    for row in data:
        cleaned_row = {}
        for key, value in row.items():
            try:
                # Garantir que cada cÃ©lula seja convertida para string e ignorar caracteres invÃ¡lidos
                cleaned_row[key] = str(value).encode('utf-8', 'ignore').decode('utf-8')
            except Exception as e:
                cleaned_row[key] = str(value)  # Caso haja erro, sÃ³ converte para string
        cleaned_data.append(cleaned_row)
    return cleaned_data

# Aplicar a limpeza dos dados
cleaned_data = clean_data(data)

# Criar DataFrame com os dados limpos
df = pd.DataFrame(cleaned_data)
df = df.rename(columns={'account_name':'Conta','spend': 'Gasto','actions_lead': 'Leads','impressions': 'Impressões','clicks': 'Cliques','date': 'Data','cost_per_action_type_lead':'Custo por Lead'})

# --- CONFIGURAÃ‡ÃƒO DO DASHBOARD ---
st.title("Dashboard de Trafego Pago")
st.sidebar.header("Filtros")

# --- FILTROS ---
# Filtro de clientes com caixa de seleÃ§Ã£o
clientes = df["Conta"].unique()  # Obter lista Ãºnica de clientes
clientes_selecionados = st.sidebar.multiselect("Selecione os Clientes", options=["Todos"] + list(clientes), default=["Todos"])

# Filtro por data (Certifique-se de que a coluna 'date' seja convertida para datetime)
df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)  # Ajuste o parÃ¢metro dayfirst conforme necessÃ¡rio

# Agora, defina os filtros corretamente
data_inicial = st.sidebar.date_input("Data Inicial", df["Data"].min())
data_final = st.sidebar.date_input("Data Final", df["Data"].max())

# Aplicar filtros
df_filtrado = df[(df["Data"] >= pd.Timestamp(data_inicial)) & (df["Data"] <= pd.Timestamp(data_final))]
 
# Ajustar outras colunas numéricas
df_filtrado['Leads'] = pd.to_numeric(df_filtrado['Leads'], errors='coerce').fillna(0)
df_filtrado['Impressões'] = pd.to_numeric(df_filtrado['Impressões'], errors='coerce').fillna(0)
df_filtrado['Cliques'] = pd.to_numeric(df_filtrado['Cliques'], errors='coerce').fillna(0)

# Exibir a tabela com os dados
st.write("Detalhamento por Campanha")
df_filtrado['Data'] = pd.to_datetime(df_filtrado['Data']).dt.strftime('%d/%m/%y')
# --- EXIBIR AS MÉTRICAS ---
col1, col2, col3, col4 = st.columns(4)
col2.metric("Impressões", f"{df_filtrado['Impressões'].sum()}") 
col3.metric("Cliques", f"{df_filtrado['Cliques'].sum()}")
col4.metric("Leads", f"{df_filtrado['Leads'].sum()}")

st.dataframe(df_filtrado)
