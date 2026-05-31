"""
Script de Prospecção de Buffets — O Mundo Fantástico
Gera mensagens personalizadas de abordagem para buffets infantis em SP.
"""

import csv
import urllib.parse
from datetime import datetime

MENSAGEM_TEMPLATE = """Olá, {contato}! Tudo bem? 😊

Meu nome é {meu_nome}, sou da empresa *O Mundo Fantástico* — somos especializados em personagens vivos para festas infantis aqui em {cidade}.

Trabalhamos com *Elsa, Ariel, Branca de Neve, Barbie, Hermione, Wandinha* e outros personagens muito amados pelas crianças. ✨

Gostaria de propor uma *parceria* com o {nome_buffet}: quando uma família fechar festa com vocês, podemos oferecer nossos personagens como um diferencial exclusivo — e você ganha uma comissão por cada indicação confirmada! 🎉

Posso te contar mais detalhes? Quando teria 10 minutinhos para conversar?"""

MINHA_INFO = {
    "nome": "Matheus",
    "whatsapp": "5511950577511",
    "instagram": "@omundo.fantastico",
}

# Base inicial — adicione mais buffets aqui
BUFFETS_SP = [
    {"nome": "Buffet Mundo Kids", "cidade": "São Paulo", "contato": "responsável", "whatsapp": ""},
    {"nome": "Buffet Encantado", "cidade": "Santo André", "contato": "responsável", "whatsapp": ""},
    {"nome": "Buffet Sonho de Festa", "cidade": "São Bernardo", "contato": "responsável", "whatsapp": ""},
    {"nome": "Buffet Estrela Mágica", "cidade": "São Caetano", "contato": "responsável", "whatsapp": ""},
    {"nome": "Buffet Pequeno Príncipe", "cidade": "Campinas", "contato": "responsável", "whatsapp": ""},
    {"nome": "Buffet Reino da Alegria", "cidade": "Jundiaí", "contato": "responsável", "whatsapp": ""},
    {"nome": "Buffet Fada Madrinha", "cidade": "São Paulo", "contato": "responsável", "whatsapp": ""},
    {"nome": "Buffet Arco-Íris", "cidade": "Guarulhos", "contato": "responsável", "whatsapp": ""},
]


def gerar_mensagem(buffet: dict) -> str:
    return MENSAGEM_TEMPLATE.format(
        contato=buffet.get("contato", "responsável"),
        meu_nome=MINHA_INFO["nome"],
        cidade=buffet["cidade"],
        nome_buffet=buffet["nome"],
    )


def gerar_link_whatsapp(numero: str, mensagem: str) -> str:
    if not numero:
        return "— número não cadastrado"
    numero_limpo = "".join(filter(str.isdigit, numero))
    if not numero_limpo.startswith("55"):
        numero_limpo = "55" + numero_limpo
    return f"https://wa.me/{numero_limpo}?text={urllib.parse.quote(mensagem)}"


def exportar_csv(buffets_com_msgs: list, arquivo: str = "prospeccao/lista_buffets.csv"):
    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["nome", "cidade", "contato", "whatsapp", "status", "data_contato", "observacoes"],
        )
        writer.writeheader()
        for b in buffets_com_msgs:
            writer.writerow({
                "nome": b["nome"],
                "cidade": b["cidade"],
                "contato": b.get("contato", ""),
                "whatsapp": b.get("whatsapp", ""),
                "status": "Não contatado",
                "data_contato": "",
                "observacoes": "",
            })
    print(f"\n✅ Lista exportada: {arquivo}")


def main():
    print("=" * 60)
    print("  O MUNDO FANTÁSTICO — Script de Prospecção de Buffets")
    print("=" * 60)
    print(f"  Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"  Total de buffets na base: {len(BUFFETS_SP)}")
    print("=" * 60)

    for i, buffet in enumerate(BUFFETS_SP, 1):
        mensagem = gerar_mensagem(buffet)
        link = gerar_link_whatsapp(buffet.get("whatsapp", ""), mensagem)

        print(f"\n📍 [{i}/{len(BUFFETS_SP)}] {buffet['nome']} — {buffet['cidade']}")
        print("-" * 50)
        print(mensagem)
        print(f"\n🔗 Link WhatsApp: {link}")
        print("=" * 60)

    exportar_csv(BUFFETS_SP)
    print("\n💡 Próximos passos:")
    print("   1. Pesquise buffets no Google Maps: 'buffet infantil São Paulo'")
    print("   2. Adicione nome, cidade, contato e WhatsApp na lista BUFFETS_SP acima")
    print("   3. Execute este script novamente para gerar os links")
    print("   4. Registre o status de cada contato na planilha exportada")
    print("   5. Follow-up em 3 dias para quem não respondeu\n")


if __name__ == "__main__":
    main()
