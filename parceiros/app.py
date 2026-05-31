"""Dashboard Streamlit para prospecção de parceiros via WhatsApp."""
import os
import time
import logging
import threading
import pandas as pd
import streamlit as st

from bot.config import carregar_config, salvar_modo
from bot.contacts import (
    carregar_parceiros, dataframe_para_parceiros, atualizar_status,
    exportar_para_excel, STATUS_VALUES,
)
from bot.messages import carregar_template, montar_mensagem, preview_mensagem
from bot.whatsapp_sender import WhatsAppSender

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Parceiros — O Mundo Fantástico",
    page_icon="🎉",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------

def _init_state():
    defaults = {
        "sender": None,
        "logado": False,
        "enviando": False,
        "log_envios": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ---------------------------------------------------------------------------
# Sidebar — configuração
# ---------------------------------------------------------------------------

st.sidebar.title("⚙️ Configuração")

try:
    config = carregar_config()
except Exception as e:
    st.sidebar.error(f"Erro ao carregar config: {e}")
    st.stop()

modo_atual = config.modo
novo_modo = st.sidebar.radio("Modo de envio", ["TESTE", "PRODUCAO"], index=0 if modo_atual == "TESTE" else 1)
if novo_modo != modo_atual:
    salvar_modo(novo_modo)
    st.sidebar.success(f"Modo alterado para {novo_modo}")
    st.rerun()

if config.is_teste:
    st.sidebar.info(f"Modo TESTE: enviando para {', '.join(config.numeros_teste)}")
else:
    st.sidebar.warning("Modo PRODUÇÃO: enviando para números reais!")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Empresa:** {config.empresa.nome}")
st.sidebar.markdown(f"**Responsável:** {config.empresa.responsavel}")

# ---------------------------------------------------------------------------
# Tabs principais
# ---------------------------------------------------------------------------

tab_contatos, tab_disparar, tab_historico, tab_template = st.tabs(
    ["📋 Contatos", "🚀 Disparar", "📊 Histórico", "✏️ Template"]
)

# ---------------------------------------------------------------------------
# Tab Contatos
# ---------------------------------------------------------------------------

with tab_contatos:
    st.header("Contatos de Parceiros")

    col_upload, col_info = st.columns([2, 1])

    with col_upload:
        uploaded = st.file_uploader("Importar nova planilha (.xlsx)", type=["xlsx"])
        if uploaded:
            try:
                df_up = pd.read_excel(uploaded, dtype=str).fillna("")
                os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
                exportar_para_excel(df_up, config.caminho_parceiros)
                st.success(f"Planilha importada com {len(df_up)} contatos.")
            except Exception as e:
                st.error(f"Erro ao importar: {e}")

    planilha_existe = os.path.exists(config.caminho_parceiros)

    if planilha_existe:
        df = carregar_parceiros(config.caminho_parceiros)

        with col_info:
            total = len(df)
            pendentes = (df["CONTATO_FEITO"] == "NAO").sum()
            enviados = (df["CONTATO_FEITO"] == "ENVIADO").sum()
            interessados = (df["CONTATO_FEITO"] == "INTERESSADO").sum()
            fechados = (df["CONTATO_FEITO"] == "PARCERIA_FECHADA").sum()

            st.metric("Total", total)
            st.metric("Pendentes", pendentes)
            st.metric("Enviados", enviados)
            st.metric("Interessados", interessados)
            st.metric("Parcerias fechadas", fechados)

        st.markdown("---")

        filtro = st.selectbox("Filtrar por status", ["Todos"] + STATUS_VALUES)
        df_view = df if filtro == "Todos" else df[df["CONTATO_FEITO"] == filtro]

        st.dataframe(df_view, use_container_width=True)

        st.markdown("#### Atualizar status manualmente")
        col_idx, col_col, col_val, col_btn = st.columns([1, 2, 2, 1])
        with col_idx:
            idx_edit = st.number_input("Linha (índice)", min_value=0, max_value=len(df) - 1, step=1)
        with col_col:
            col_edit = st.selectbox("Coluna", ["CONTATO_FEITO", "INTERESSADO", "FECHADO", "FESTAS GERADAS"])
        with col_val:
            val_edit = st.text_input("Novo valor")
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Salvar"):
                atualizar_status(config.caminho_parceiros, idx_edit, col_edit, val_edit)
                st.success("Atualizado!")
                st.rerun()

        st.download_button(
            "⬇️ Baixar planilha atualizada",
            data=open(config.caminho_parceiros, "rb").read(),
            file_name="parceiros.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.warning("Nenhuma planilha encontrada. Execute `python setup_data.py` ou importe uma acima.")

# ---------------------------------------------------------------------------
# Tab Disparar
# ---------------------------------------------------------------------------

with tab_disparar:
    st.header("Disparar Mensagens")

    if not os.path.exists(config.caminho_parceiros):
        st.error("Planilha não encontrada. Vá para a aba Contatos.")
        st.stop()

    df = carregar_parceiros(config.caminho_parceiros)
    parceiros = dataframe_para_parceiros(df)
    pendentes = [p for p in parceiros if p.pode_enviar and p.telefone_formatado]

    st.info(f"{len(pendentes)} contatos pendentes para envio.")

    col_wa, col_status = st.columns([2, 1])

    with col_wa:
        st.markdown("### 1. Iniciar WhatsApp Web")
        if not st.session_state.logado:
            headless = st.checkbox("Headless (sem janela)", value=False,
                                   help="Desmarque para ver o QR Code na tela")
            if st.button("Abrir WhatsApp Web"):
                with st.spinner("Abrindo Chrome..."):
                    try:
                        sender = WhatsAppSender(
                            pausa=config.pausa_entre_envios_segundos,
                            variacao=config.pausa_variacao_segundos,
                        )
                        sender.iniciar(headless=headless)
                        st.session_state.sender = sender
                        st.success("Chrome aberto! Escaneie o QR Code e clique em 'Confirmar login'.")
                    except Exception as e:
                        st.error(f"Erro ao abrir Chrome: {e}")
        else:
            st.success("WhatsApp Web conectado!")
            if st.button("Desconectar"):
                if st.session_state.sender:
                    st.session_state.sender.fechar()
                st.session_state.sender = None
                st.session_state.logado = False
                st.rerun()

        if st.session_state.sender and not st.session_state.logado:
            if st.button("✅ Confirmar login (já escaniei o QR)"):
                with st.spinner("Aguardando confirmação..."):
                    ok = st.session_state.sender.aguardar_login(timeout=30)
                    if ok:
                        st.session_state.logado = True
                        st.success("Logado!")
                        st.rerun()
                    else:
                        st.error("Login não detectado. Tente novamente.")

    with col_status:
        st.markdown("### Status")
        if st.session_state.logado:
            st.success("🟢 Conectado")
        elif st.session_state.sender:
            st.warning("🟡 Aguardando QR")
        else:
            st.error("🔴 Desconectado")

    st.markdown("---")
    st.markdown("### 2. Disparar mensagens")

    if not st.session_state.logado:
        st.warning("Conecte o WhatsApp Web primeiro.")
    elif not pendentes:
        st.success("Todos os contatos já foram contactados!")
    else:
        limite = st.number_input(
            f"Quantos enviar agora? (máx {len(pendentes)})",
            min_value=1, max_value=len(pendentes), value=min(5, len(pendentes))
        )

        if st.button(f"🚀 Enviar para {limite} contato(s)", disabled=st.session_state.enviando):
            st.session_state.enviando = True
            template = carregar_template(config.caminho_template)
            log_placeholder = st.empty()
            progresso = st.progress(0)

            for i, parceiro in enumerate(pendentes[:limite]):
                try:
                    mensagem = montar_mensagem(template, parceiro.nome)
                    alvo = config.numeros_teste[0] if config.is_teste else parceiro.telefone_formatado

                    resultado = st.session_state.sender.enviar_mensagem(alvo, mensagem)

                    if resultado.sucesso:
                        atualizar_status(config.caminho_parceiros, parceiro.indice, "CONTATO_FEITO", "ENVIADO")
                        entry = f"✅ {parceiro.nome} ({parceiro.telefone})"
                    else:
                        entry = f"❌ {parceiro.nome}: {resultado.erro}"

                    st.session_state.log_envios.append(entry)
                    log_placeholder.text("\n".join(st.session_state.log_envios[-20:]))
                    progresso.progress((i + 1) / limite)

                    if i < limite - 1:
                        st.session_state.sender.pausa_aleatoria()

                except Exception as e:
                    st.session_state.log_envios.append(f"💥 {parceiro.nome}: {e}")

            st.session_state.enviando = False
            st.success("Envio concluído!")
            st.rerun()

# ---------------------------------------------------------------------------
# Tab Histórico
# ---------------------------------------------------------------------------

with tab_historico:
    st.header("Histórico de Envios")

    if st.session_state.log_envios:
        for entry in reversed(st.session_state.log_envios):
            st.text(entry)
    else:
        st.info("Nenhum envio realizado nesta sessão.")

    log_path = config.caminho_log
    if os.path.exists(log_path):
        st.markdown("---")
        st.markdown("### Log do arquivo")
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            linhas = f.readlines()
        st.text_area("envios.log", value="".join(linhas[-100:]), height=300)
        st.download_button(
            "⬇️ Baixar log completo",
            data=open(log_path, "rb").read(),
            file_name="envios.log",
        )

# ---------------------------------------------------------------------------
# Tab Template
# ---------------------------------------------------------------------------

with tab_template:
    st.header("Template da Mensagem")

    template_path = config.caminho_template

    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            conteudo_atual = f.read()
    else:
        conteudo_atual = ""

    novo_conteudo = st.text_area(
        "Editar template (use {nome_buffet} como variável)",
        value=conteudo_atual,
        height=300,
    )

    col_salvar, col_preview = st.columns(2)

    with col_salvar:
        if st.button("💾 Salvar template"):
            os.makedirs(os.path.dirname(template_path), exist_ok=True)
            with open(template_path, "w", encoding="utf-8") as f:
                f.write(novo_conteudo)
            st.success("Template salvo!")

    with col_preview:
        nome_exemplo = st.text_input("Nome para preview", value="Buffet Exemplo")
        if st.button("👁️ Visualizar"):
            try:
                preview = montar_mensagem(novo_conteudo, nome_exemplo)
                st.text_area("Preview", value=preview, height=250)
            except ValueError as e:
                st.error(str(e))
