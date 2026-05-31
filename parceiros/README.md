# Sistema de Prospecção de Parceiros — O Mundo Fantástico

Ferramenta para disparar mensagens WhatsApp para buffets infantis e acompanhar o progresso de parcerias.

## Pré-requisitos

- Python 3.12+
- Google Chrome instalado
- Windows 10/11

## Instalação

```bash
# Na pasta parceiros/
pip install -r requirements.txt
```

## Primeira execução

```bash
# Cria a planilha inicial com os 21 buffets cadastrados
python setup_data.py
```

## Iniciar o dashboard

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

## Fluxo de uso

1. **Aba Contatos** — visualize e filtre os parceiros. Importe uma planilha `.xlsx` se necessário.
2. **Aba Disparar**:
   - Clique em **Abrir WhatsApp Web** (deixe headless desmarcado para ver o QR Code).
   - Escaneie o QR Code com seu celular.
   - Clique em **Confirmar login**.
   - Escolha quantos enviar e clique em **Enviar**.
3. **Aba Histórico** — acompanhe os resultados da sessão e o log completo.
4. **Aba Template** — edite a mensagem e visualize o preview.

## Modos

| Modo | Comportamento |
|------|--------------|
| TESTE | Envia todas as mensagens para o número em `config/config.json → numeros_teste` |
| PRODUCAO | Envia para os números reais da planilha |

Altere o modo no menu lateral do dashboard ou edite `config/config.json` diretamente.

## Estrutura de arquivos

```
parceiros/
├── app.py                  # Dashboard Streamlit
├── setup_data.py           # Cria planilha inicial
├── requirements.txt
├── config/
│   └── config.json         # Configurações gerais
├── data/
│   └── parceiros.xlsx      # Planilha de contatos (gerada pelo setup)
├── logs/
│   └── envios.log          # Log automático
├── templates/
│   └── mensagem_inicial.txt
└── bot/
    ├── config.py
    ├── contacts.py
    ├── messages.py
    └── whatsapp_sender.py
```

## Status dos contatos

| Status | Significado |
|--------|-------------|
| NAO | Ainda não contactado |
| ENVIADO | Mensagem enviada |
| RESPONDEU | Respondeu a mensagem |
| INTERESSADO | Demonstrou interesse |
| SEM_INTERESSE | Não tem interesse |
| PARCERIA_FECHADA | Parceria confirmada |

## Dicas

- A sessão do Chrome é salva em `./chrome_session` — na segunda execução não precisa escanear o QR novamente.
- O intervalo entre envios é aleatório (~18s ± 7s) para evitar bloqueio pelo WhatsApp.
- Faça backups regulares de `data/parceiros.xlsx`.
