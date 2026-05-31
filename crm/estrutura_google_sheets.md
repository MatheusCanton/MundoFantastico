# CRM O Mundo Fantástico — Google Sheets

## Como configurar

Crie uma planilha no Google Sheets com as abas abaixo.

---

## Aba 1: LEADS

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| Data entrada | Data | Quando o lead chegou |
| Nome | Texto | Nome da mãe/pai |
| WhatsApp | Tel | Número de contato |
| Cidade | Texto | Cidade da festa |
| Data da festa | Data | Data do evento |
| Personagem | Lista | Elsa / Ariel / Barbie / etc |
| Pacote | Lista | Encanto / Mágico / Real |
| Origem | Lista | Instagram / Indicação / Buffet / Google / Site |
| Indicado por | Texto | Nome de quem indicou |
| Status | Lista | Novo / Em negociação / Proposta enviada / Fechado / Perdido |
| Valor | Número | Valor combinado |
| Observações | Texto | Notas livres |

### Status sugeridos (use validação de dados):
- 🔵 Novo
- 🟡 Em negociação
- 🟠 Proposta enviada
- 🟢 Fechado
- 🔴 Perdido

---

## Aba 2: AGENDA

| Coluna | Tipo |
|--------|------|
| Data | Data |
| Horário | Hora |
| Cliente | Texto |
| Personagem | Texto |
| Pacote | Texto |
| Endereço | Texto |
| Valor | Número |
| Sinal pago | Sim/Não |
| Saldo | Número |
| Status | Lista: Confirmado / Pendente / Cancelado |

---

## Aba 3: PARCEIROS (Buffets)

| Coluna | Tipo |
|--------|------|
| Nome do buffet | Texto |
| Cidade | Texto |
| Contato | Texto |
| WhatsApp | Tel |
| Instagram | Texto |
| Data 1º contato | Data |
| Último contato | Data |
| Status | Lista: Não contatado / Aguardando / Parceiro ativo / Não tem interesse |
| Indicações geradas | Número |
| Festas fechadas | Número |
| Comissão paga | Número |
| Observações | Texto |

---

## Aba 4: FINANCEIRO

| Coluna | Tipo |
|--------|------|
| Mês | Texto |
| Festas realizadas | Número |
| Faturamento bruto | Número |
| Ticket médio | Fórmula: =B2/A2 |
| Leads recebidos | Número |
| Taxa de conversão | Fórmula: =A2/E2 |
| Origem principal | Texto |

---

## Dicas de automação no Sheets

1. **Alerta de follow-up:** Use Extensões > Apps Script para enviar email quando um lead ficar 3 dias sem atualização.
2. **Dashboard automático:** Use a aba Financeiro com fórmulas SUMIF para calcular por mês.
3. **Formulário de entrada:** Conecte um Google Forms à planilha para registrar novos leads automaticamente.

---

## Fórmulas úteis

```
# Total de fechamentos no mês
=COUNTIFS(Leads!H:H,"Fechado",Leads!A:A,">="&DATEVALUE("01/06/2025"))

# Faturamento do mês
=SUMIFS(Leads!K:K,Leads!H:H,"Fechado")

# Taxa de conversão
=COUNTIF(Leads!H:H,"Fechado")/COUNTA(Leads!A:A)-1
```
