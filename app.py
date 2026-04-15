def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Lê o arquivo de credenciais e corrige a formatação da chave privada
        with open('credentials.json') as f:
            info = json.load(f)
        info['private_key'] = info['private_key'].replace('\\n', '\n')
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        client = gspread.authorize(creds)
        
        # Abre a planilha exata que você criou
        sheet = client.open("SIMULADOR_COMUNICACAO_2026").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except Exception as e:
        # Mostra o erro na barra lateral para diagnóstico rápido
        st.sidebar.error(f"Erro ao salvar: {e}")
        return False
