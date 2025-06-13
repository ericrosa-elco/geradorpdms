import streamlit as st
import json
import os
import pandas as pd
import numpy as np

versao = "V1.0.0-beta"
#Vmajor.minor.patch-(alpha,beta,rc1)

# --- Configuração Inicial da Página ---
st.set_page_config(
    page_title="Sistema PDMS",
    page_icon="images/logo_elco_ajustado.png",
    layout="wide"
)

st.logo(
    "images/logo_elco.png",
    link=None,
    icon_image=None
)

# --- Funções de Autenticação ---

def carregar_usuarios():
    """Carrega os dados dos usuários do arquivo JSON."""
    if os.path.exists("dados_cadastrais.json"):
        with open("dados_cadastrais.json", "r", encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def salvar_usuarios(usuarios):
    """Salva os dados dos usuários no arquivo JSON."""
    with open("dados_cadastrais.json", "w", encoding='utf-8') as file:
        json.dump(usuarios, file, indent=4, ensure_ascii=False)

def cadastrar_usuario(nome_de_usuario, senha, usuarios):
    """Cadastra um novo usuário."""
    if nome_de_usuario in usuarios:
        return False
    
    usuarios[nome_de_usuario] = senha
    salvar_usuarios(usuarios)
    return True

def autenticar_usuario(nome_de_usuario, senha, usuarios):
    """Verifica se o usuário e a senha são válidos."""
    if nome_de_usuario in usuarios and usuarios[nome_de_usuario] == senha:
        return True
    return False

# --- Interfaces das Páginas ---

def pagina_login_cadastro():
    """Exibe a interface de login e cadastro."""
    st.title("Autenticação de Usuário")
    menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro"])
    usuarios = carregar_usuarios()
    st.sidebar.divider()
    st.sidebar.text(versao)
    st.sidebar.text('''Uso livre para testar o sistema.
Faça cadastro caso não possua uma conta.
A segurança será melhorada nas versões subsequentes.''')

    if menu == "Login":
        st.subheader("Login")
        with st.form("login_form"):
            nome_de_usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar")
            
            if submitted:
                if autenticar_usuario(nome_de_usuario, senha, usuarios):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = nome_de_usuario
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

    elif menu == "Cadastro":
        st.subheader("Cadastro")
        with st.form("cadastro_form"):
            novo_nome_de_usuario = st.text_input("Insira um nome de usuário")
            nova_senha = st.text_input("Insira uma senha", type="password")
            confirmar_senha = st.text_input("Confirme a senha", type="password")
            submitted = st.form_submit_button("Cadastrar Usuário")
            
            if submitted:
                if confirmar_senha == nova_senha:
                    if novo_nome_de_usuario and nova_senha and confirmar_senha:
                        if cadastrar_usuario(novo_nome_de_usuario, nova_senha, usuarios):
                            st.success("Usuário criado com sucesso! Faça login para continuar.")
                        else:
                            st.error("Este nome de usuário já existe. Por favor, escolha outro.")
                    else:
                        st.warning("Por favor, preencha todos os campos.")
                else:
                    st.warning("As senhas não coincidem")

def pagina_principal():
    """Exibe a aplicação principal após o login."""
    
    # --- Sidebar com Logout e Navegação ---
    st.sidebar.title(f"Logado como: {st.session_state.get('username', '')}")
    if st.sidebar.button("Terminar sessão"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.rerun()

    st.sidebar.divider()
    st.sidebar.title("Navegação")
    pagina_selecionada = st.sidebar.radio(
        "Selecione uma página:",
        ("Gerador de Descrição", "Cadastro/Edição de Itens")
    )

    #SESSÃO DE SUPORTE 
    st.sidebar.divider()
    st.sidebar.title("Suporte")
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        st.markdown(
            '[Contato](mailto:nelluana.ribas@elco.com.br)',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            '[Manual do Sistema](link do documento)',
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            '[Manual PDMS](link do documento)',
            unsafe_allow_html=True
        )

    st.sidebar.divider()
    st.sidebar.text(versao)

    # Página: Gerador de Descrição
    if pagina_selecionada == "Gerador de Descrição":
        st.title("Padrão Descritivo de Materiais e Serviços")
        
        regras = {}
        caminho_json = "parametros.json"

        if os.path.exists(caminho_json):
            with open(caminho_json, "r", encoding="utf-8") as f:
                try:
                    regras = json.load(f)
                except json.JSONDecodeError:
                    st.error("⚠️ Erro: O arquivo 'parametros.json' está vazio ou mal formatado.")
        else:
            st.warning("⚠️ Arquivo 'parametros.json' não encontrado. Cadastre um item para começar.")

        if regras:
            # ### MUDANÇA PRINCIPAL ### Adicionado index=None para não pré-selecionar
            item = st.selectbox(
                "Escolha o item:", 
                sorted(list(regras.keys())),
                index=None,
                placeholder="Selecione o tipo de item..."
            )
            
            # O código abaixo só roda se um item for selecionado
            if item:
                descricao = [item]
                ordem = regras[item].get("ordem", [])
                valores = regras[item].get("valores_comuns", {})

                for campo in ordem:
                    opcoes = valores.get(campo, []) 
                    if not opcoes: # Se não houver opções, pula este campo
                        continue
                    
                    # ### MUDANÇA SECUNDÁRIA ### Também adicionado index=None aqui
                    escolha = st.selectbox(
                        f"{campo.upper()}:", 
                        sorted(opcoes),
                        index=None,
                        placeholder=f"Escolha o valor para {campo.lower()}..."
                    )
                    
                    # Adiciona a escolha à descrição apenas se o usuário selecionar algo
                    if escolha:
                        descricao.append(escolha.upper())
                
                resultado = " ".join(descricao)
                st.text_area("Descrição final:", resultado, height=100)
        else:
            st.info("Adicione itens na página de 'Cadastro/Edição' para começar.")

    # Página: Cadastro/Editar Itens
    elif pagina_selecionada == "Cadastro/Edição de Itens":
        # (O código desta seção permanece o mesmo da versão anterior, sem alterações)
        st.title("Cadastro e Edição de Itens")
        
        ARQ = "parametros.json"

        def carregar_regras():
            if os.path.exists(ARQ):
                with open(ARQ, "r", encoding="utf-8") as f:
                    try: return json.load(f)
                    except json.JSONDecodeError:
                        st.error("Arquivo JSON mal formatado."); return {}
            return {}

        def salvar_regras(dados):
            with open(ARQ, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)

        regras = carregar_regras()
        modo = st.radio("Escolha a ação:", ["Cadastrar Novo Item", "Editar Item Existente", "Excluir Item"])

        if modo == "Cadastrar Novo Item":
            st.subheader("Cadastrar novo item")
            with st.form("cadastro_item_form"):
                nome_item = st.text_input("Nome do novo item (ex: JOELHO)").strip().upper()
                ordem_str = st.text_input("Ordem dos parâmetros (separados por vírgula, ex: ângulo,finalidade,material)").strip()
                valores_comuns = {}; ordem = []
                if nome_item and ordem_str:
                    ordem = [o.strip() for o in ordem_str.split(",") if o.strip()]
                    st.write("Defina os valores iniciais para cada parâmetro (opcional):")
                    for param in ordem:
                        vals = st.text_area(f"Valores para '{param.upper()}' (separar por vírgula)").strip()
                        lista_vals = [v.strip() for v in vals.split(",") if v.strip()]
                        valores_comuns[param] = lista_vals
                submitted = st.form_submit_button("Cadastrar Item")
                if submitted:
                    if not nome_item or not ordem_str: st.error("Nome do item e Ordem dos parâmetros são obrigatórios.")
                    elif nome_item in regras: st.error("Item já existe! Use o modo 'Editar' para modificar.")
                    else:
                        regras[nome_item] = {"ordem": ordem, "valores_comuns": valores_comuns}
                        salvar_regras(regras)
                        st.success(f"Item '{nome_item}' cadastrado com sucesso!"); st.rerun()

        elif modo == "Editar Item Existente":
            st.subheader("Editar item existente")
            
            if not regras:
                st.warning("Nenhum item cadastrado ainda.")
            else:
                # Selecionando o item
                if 'item_selecionado' not in st.session_state:
                    st.session_state['item_selecionado'] = None
                
                item_selecionado = st.selectbox("Selecione o item para editar:", sorted(list(regras.keys())), index=None)
                
                # Atualiza o item selecionado no estado da sessão
                if item_selecionado != st.session_state['item_selecionado']:
                    st.session_state['item_selecionado'] = item_selecionado
                
                if st.session_state['item_selecionado']:
                    item_data = regras[st.session_state['item_selecionado']]
                    st.write(f"Parâmetros na ordem: `{'`, `'.join(item_data['ordem'])}`")
                    
                    # Edição da ordem dos parâmetros
                    # Edição da ordem dos parâmetros
            # Edição da ordem dos parâmetros (agora é opcional)
# Edição da ordem dos parâmetros (agora é opcional)
            st.subheader("Editar Ordem dos Parâmetros (Opcional)")

            # Caixa de texto para editar a ordem dos parâmetros
            novos_parametros = st.text_area(
                "Edite a ordem dos parâmetros (separados por vírgula, ex: ângulo,finalidade,material)",
                value=", ".join(item_data['ordem'])
            ).strip()

            # Botão para salvar a ordem dos parâmetros
            if st.button("Salvar Ordem"):
                if novos_parametros:
                    # Dividir os parâmetros inseridos na caixa de texto e remover espaços extras
                    nova_ordem = [p.strip() for p in novos_parametros.split(",") if p.strip()]
                    
                    # Verificar se a nova ordem tem a mesma quantidade de parâmetros
                    if len(nova_ordem) != len(item_data['ordem']):
                        st.error("A quantidade de parâmetros não corresponde. Verifique os itens inseridos.")
                    else:
                        # Validar se todos os parâmetros existentes estão presentes e sem repetições
                        if sorted(nova_ordem) != sorted(item_data['ordem']):
                            st.error("Os parâmetros inseridos não correspondem aos parâmetros existentes.")
                        else:
                            # Atualizar a ordem dos parâmetros
                            item_data['ordem'] = nova_ordem
                            salvar_regras(regras)
                            st.success(f"Ordem dos parâmetros do item '{st.session_state['item_selecionado']}' foi atualizada.")
                else:
                    st.warning("A ordem dos parâmetros não foi alterada.")  # Caso o campo seja deixado vazio


            # Edição dos valores dos parâmetros (pode ser feita independentemente da ordem)
            st.subheader("Edição de Valores dos Parâmetros")

            # Campo para escolher o parâmetro a ser editado
            param_selecionado = st.selectbox(
                "Selecione o parâmetro para adicionar novo valor:",
                item_data["ordem"]
            )

            # Campo para adicionar um novo valor ao parâmetro
            novo_valor = st.text_input(f"Novo valor para '{param_selecionado.upper()}'").strip()

            # Botão para adicionar o valor ao parâmetro
            if st.button(f"Adicionar valor para '{param_selecionado.upper()}'"):
                if novo_valor:
                    if novo_valor.upper() in [v.upper() for v in item_data["valores_comuns"].get(param_selecionado, [])]:
                        st.warning("Este valor já existe nesse parâmetro.")
                    else:
                        item_data["valores_comuns"].setdefault(param_selecionado, []).append(novo_valor)
                        item_data["valores_comuns"][param_selecionado].sort()
                        salvar_regras(regras)
                        st.success(f"Valor '{novo_valor}' adicionado ao parâmetro '{param_selecionado}' do item '{st.session_state['item_selecionado']}'.")
                else:
                    st.error("Digite um valor válido para adicionar.")

                    # Edição dos valores dos parâmetros
                    param_selecionado = st.selectbox(
                        "Selecione o parâmetro para adicionar novo valor:",
                        item_data["ordem"]
                    )
                    with st.form("add_valor_form"):
                        novo_valor = st.text_input(f"Novo valor para '{param_selecionado.upper()}'").strip()
                        submitted = st.form_submit_button("Adicionar valor")
                        if submitted:
                            if novo_valor:
                                if novo_valor.upper() in [v.upper() for v in item_data["valores_comuns"].get(param_selecionado, [])]:
                                    st.warning("Este valor já existe nesse parâmetro.")
                                else:
                                    item_data["valores_comuns"].setdefault(param_selecionado, []).append(novo_valor)
                                    item_data["valores_comuns"][param_selecionado].sort()
                                    salvar_regras(regras)
                                    st.success(f"Valor '{novo_valor}' adicionado ao parâmetro '{param_selecionado}' do item '{st.session_state['item_selecionado']}'.")
                            
                            else:
                                st.error("Digite um valor válido para adicionar.")
                    
                    # Edição de nome de parâmetros
                    st.subheader("Editar Nome dos Parâmetros")

                    for param in item_data['ordem']:
                        novo_nome = st.text_input(f"Novo nome para o parâmetro '{param}'", value=param).strip()
                        
                        if novo_nome != param:
                            if novo_nome not in item_data['ordem']:
                                item_data['ordem'][item_data['ordem'].index(param)] = novo_nome
                                st.success(f"Parâmetro '{param}' foi renomeado para '{novo_nome}'.")
                            else:
                                st.warning(f"O nome '{novo_nome}' já existe na lista de parâmetros.")
                    
                    salvar_regras(regras)


        elif modo == "Excluir Item":
            st.subheader("Excluir item")
            if not regras: st.warning("Nenhum item para excluir.")
            else:
                item_para_excluir = st.selectbox("Selecione o item para excluir:", sorted(list(regras.keys())))
                if st.button(f"Excluir permanentemente o item '{item_para_excluir}'", type="primary"):
                    if item_para_excluir in regras:
                        del regras[item_para_excluir]
                        salvar_regras(regras)
                        st.success(f"Item '{item_para_excluir}' foi excluído."); st.rerun()

# Lógica Principal de Roteamento
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    pagina_principal()
else:
    pagina_login_cadastro()

# Estilo do projeto fora o config.toml
st.markdown(
f"""
    <style>
        :root {{
            --button-bg-light: #FFD700;
            --primary-color-light: #2e2e2e;
        }}
        .stButton > button {{
            background-color: {"var(--button-bg-light)"}; 
            color: {"var(--primary-color-light)"}; /* Cor do texto do botão */
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
        }}
        .stButton > button:hover {{
            background-color: {'#FFCC00'};
            color: var(--primary-color-light);
        }}
    </style>
""",
    unsafe_allow_html=True
)