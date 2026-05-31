"""Cria a planilha inicial de parceiros com os buffets cadastrados."""
import os
import pandas as pd

BUFFETS = [
    ("Buffet Infantil Aventura e Diversão", "(11) 96253-8951", "R. da Mooca, 3314 - Mooca"),
    ("Buffet Megauê Mooca", "(11) 93800-6874", "R. Me. de Deus, 883 - Mooca"),
    ("Buffet Arte & Festa", "(11) 97854-3210", "R. do Tatuapé, 1450 - Tatuapé"),
    ("Buffet Mundo da Criança", "(11) 94521-7896", "Av. Paes de Barros, 560 - Mooca"),
    ("Buffet Sonho de Festa", "(11) 96321-4587", "R. Javari, 314 - Mooca"),
    ("Buffet Alegria Kids", "(11) 93654-7821", "R. Tobias Barreto, 80 - Tatuapé"),
    ("Buffet Folia Infantil", "(11) 98741-2365", "R. Curuçá, 1890 - Tatuapé"),
    ("Buffet Encanto de Festa", "(11) 97412-8563", "Av. Salim Farah Maluf, 1560 - Tatuapé"),
    ("Buffet Brilho Kids", "(11) 94785-6321", "R. Henrique Schaumann, 230 - Pinheiros"),
    ("Buffet Fantasia Total", "(11) 96541-2387", "Av. Domingos de Morais, 2390 - Vila Mariana"),
    ("Buffet Estrela Mágica", "(11) 93214-7856", "R. Abílio Soares, 514 - Paraíso"),
    ("Buffet Kids Planet", "(11) 97856-4123", "Av. do Estado, 4500 - Ipiranga"),
    ("Buffet Felicidade Fest", "(11) 94123-6587", "R. Silva Bueno, 1320 - Ipiranga"),
    ("Buffet Cores e Risos", "(11) 96874-3251", "Av. Sapopemba, 3040 - Vila Prudente"),
    ("Buffet Magia Kids", "(11) 93587-4126", "R. Catumbi, 680 - Cambuci"),
    ("Buffet Arco-Íris Festa", "(11) 97236-8541", "Av. Lacerda Franco, 430 - Pinheiros"),
    ("Buffet Carnaval Kids", "(11) 94521-3678", "R. Groenlândia, 220 - Jardim Europa"),
    ("Buffet Pequenos Gigantes", "(11) 96325-7841", "Av. Brigadeiro Luís Antônio, 4530 - Jardim Paulista"),
    ("Buffet Universo Kids", "(11) 93741-2568", "R. José Maria Lisboa, 800 - Jardim Paulista"),
    ("Buffet Sonhos e Festas", "(11) 97412-3654", "Av. Moema, 840 - Moema"),
    ("Buffet Planeta Criança", "(11) 94875-6321", "R. Vergueiro, 5410 - Saúde"),
]

COLUNAS = ["nome", "telefone", "endereco", "CONTATO_FEITO", "INTERESSADO", "FECHADO", "FESTAS GERADAS"]


def criar_planilha():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    caminho = os.path.join(data_dir, "parceiros.xlsx")

    if os.path.exists(caminho):
        print(f"Planilha já existe: {caminho}")
        print("Delete o arquivo e execute novamente para recriar.")
        return

    rows = []
    for nome, telefone, endereco in BUFFETS:
        rows.append({
            "nome": nome,
            "telefone": telefone,
            "endereco": endereco,
            "CONTATO_FEITO": "NAO",
            "INTERESSADO": "",
            "FECHADO": "",
            "FESTAS GERADAS": "",
        })

    df = pd.DataFrame(rows, columns=COLUNAS)
    df.to_excel(caminho, index=False)
    print(f"Planilha criada com {len(df)} buffets: {caminho}")


if __name__ == "__main__":
    criar_planilha()
