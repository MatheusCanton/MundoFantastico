# -*- coding: utf-8 -*-
"""
Lê a Google Agenda do Disque ao vivo (formato iCal) e gera disponibilidade.json.

Regras (definidas com quem faz as chamadas):
  - chamada de 30 min, uma a cada 1h, em hora cheia
  - uma chamada por vez: horário vendido fecha para TODAS as princesas
  - trocar de princesa exige 1h30 entre o fim de uma chamada e o início da
    próxima; com horários em hora cheia, o horário de antes e o de depois de uma
    reserva ficam só para a mesma princesa
  - só o mês atual aparece no site
  - nos dias 1, 2 e 3 de cada mês não há chamada (feriado é dia normal). A Google
    Agenda não sabe repetir "ter/qua/qui, menos dias 1 a 3", então a regra fica aqui
  - as regras de TEMPO (24h de antecedência, horário que já passou) ficam com a
    página, que usa o relógio real de quem visita. Assim o arquivo só muda quando
    a agenda muda (e uma vez por dia, quando some o dia anterior) — sem commit à toa.

Como marcar na agenda:
  - "Disque" (evento com horário, ex.: ter/qua/qui 12h–20h, repetindo toda semana) = quando há
    atendimento; o robô recorta em 12:00, 13:00 ... 19:00
  - venda: evento no horário com o nome da princesa no título
    (ex.: "Reservado - Elsa - Maria")
  - "Reservado ..." sem princesa reconhecida = fecha o horário e os vizinhos
    para todas (por segurança, já que não sabemos a princesa)
  - evento de DIA INTEIRO (festa, folga...) = o dia some do site
  - qualquer outro compromisso com horário = fecha só os horários que ele cobre
  - eventos "Livre" (regra antiga) são ignorados

Privacidade: o JSON contém só data, hora, situação e a princesa de cada horário
restrito. Títulos, nomes, descrições e convidados nunca saem da agenda.

Uso:
  AGENDA_ICS_URL=https://... python sync_agenda.py saida.json
  python sync_agenda.py saida.json --arquivo agenda.ics [--agora 2026-09-11T20:00]
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import unicodedata
import urllib.request
from zoneinfo import ZoneInfo

import icalendar
import recurring_ical_events

FUSO = ZoneInfo("America/Sao_Paulo")
DURACAO = dt.timedelta(minutes=30)     # duração de cada chamada
PASSO = dt.timedelta(hours=1)          # uma chamada a cada 1h
TROCA = dt.timedelta(minutes=90)       # tempo para trocar de princesa
DIAS_SEM_CHAMADA = {1, 2, 3}           # dias do mês sem atendimento

# chave usada no site -> apelidos aceitos no título (a ordem importa: "rainha"
# antes de "branca", porque a Rainha Má também é da história da Branca de Neve)
PRINCESAS = [
    ("rainha",   ["rainha"]),
    ("branca",   ["branca de neve", "branca"]),
    ("elsa",     ["elsa", "frozen", "congelante"]),
    ("ariel",    ["ariel", "sereia"]),
    ("rapunzel", ["rapunzel", "torre"]),
    ("jasmine",  ["jasmine", "jasmin"]),
    ("barbie",   ["barbie"]),
    ("alice",    ["alice"]),
]


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    return "".join(c for c in texto if not unicodedata.combining(c)).strip().lower()


def princesa_do_titulo(titulo):
    t = normalizar(titulo)
    for chave, apelidos in PRINCESAS:
        for a in apelidos:
            if re.search(r"\b" + re.escape(a) + r"\b", t):
                return chave
    return None


def baixar_ics(url):
    url = url.strip().replace("webcal://", "https://", 1)
    req = urllib.request.Request(url, headers={"User-Agent": "omundofantastico-agenda/2.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def no_fuso(valor):
    if valor.tzinfo is None:                       # hora "flutuante": assume o fuso local
        valor = valor.replace(tzinfo=FUSO)
    return valor.astimezone(FUSO)


def proxima_hora_cheia(t):
    return t if (t.minute == 0 and t.second == 0) else \
        t.replace(minute=0, second=0, microsecond=0) + dt.timedelta(hours=1)


def montar_disponibilidade(ics_bytes, agora):
    cal = icalendar.Calendar.from_ical(ics_bytes)
    inicio_janela = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    # só o mês atual: até o primeiro instante do mês seguinte
    fim_janela = (agora.replace(day=28) + dt.timedelta(days=4)).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0)

    blocos, reservas, compromissos, fechados = [], [], [], set()
    avisos = []
    for ev in recurring_ical_events.of(cal).between(inicio_janela, fim_janela):
        if normalizar(ev.get("STATUS")) == "cancelled":
            continue
        titulo = ev.get("SUMMARY")
        ini = ev.get("DTSTART").dt
        fim = ev.get("DTEND").dt if ev.get("DTEND") else None

        if not isinstance(ini, dt.datetime):       # dia inteiro: fecha o(s) dia(s)
            fim = fim or ini + dt.timedelta(days=1)
            d = ini
            while d < fim:                          # DTEND é exclusivo
                fechados.add(d)
                d += dt.timedelta(days=1)
            continue

        ini = no_fuso(ini)
        fim = no_fuso(fim) if isinstance(fim, dt.datetime) else ini + DURACAO
        t = normalizar(titulo)
        if t.startswith("livre"):
            continue                                # regra antiga: ignorado
        if t.startswith("disque"):
            blocos.append((ini, fim))
            continue
        princesa = princesa_do_titulo(titulo)
        if princesa or t.startswith("reservado"):
            if not princesa:
                avisos.append("reserva sem princesa reconhecida em %s" % ini.strftime("%d/%m %H:%M"))
            reservas.append((ini, max(fim, ini + DURACAO), princesa))
        else:
            compromissos.append((ini, fim))

    # horários = recortes dos blocos "Disque", em hora cheia, cabendo a chamada inteira
    horarios = set()
    for b_ini, b_fim in blocos:
        s = proxima_hora_cheia(b_ini)
        while s + DURACAO <= b_fim:
            horarios.add(s)
            s += PASSO

    dias = {}
    for s in sorted(horarios):
        if (s.date() < agora.date() or s >= fim_janela or s.date() in fechados
                or s.day in DIAS_SEM_CHAMADA):
            continue
        e = s + DURACAO
        sobrepoe = lambda a, b: a < e and s < b    # noqa: E731

        if any(sobrepoe(r[0], r[1]) for r in reservas) or any(sobrepoe(c[0], c[1]) for c in compromissos):
            item = {"hora": s.strftime("%H:%M"), "status": "ocupado"}
        else:
            # reservas perto demais para trocar de princesa
            vizinhas = {r[2] for r in reservas
                        if (s >= r[1] and s - r[1] < TROCA) or (e <= r[0] and r[0] - e < TROCA)}
            if not vizinhas:
                item = {"hora": s.strftime("%H:%M"), "status": "livre"}
            elif len(vizinhas) == 1 and None not in vizinhas:
                item = {"hora": s.strftime("%H:%M"), "status": "so", "princesa": vizinhas.pop()}
            else:                                   # princesas diferentes dos dois lados, ou desconhecida
                item = {"hora": s.strftime("%H:%M"), "status": "ocupado"}
        dias.setdefault(s.date().isoformat(), []).append(item)

    return [{"data": d, "horarios": h} for d, h in sorted(dias.items())], avisos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("saida", help="caminho do disponibilidade.json")
    ap.add_argument("--arquivo", help="ler um .ics local em vez da URL (teste)")
    ap.add_argument("--agora", help="simular data/hora atual, ex.: 2026-09-11T20:00 (teste)")
    args = ap.parse_args()

    if args.arquivo:
        with open(args.arquivo, "rb") as f:
            ics = f.read()
    else:
        url = os.environ.get("AGENDA_ICS_URL")
        if not url:
            sys.exit("Defina AGENDA_ICS_URL com o endereço iCal da agenda.")
        ics = baixar_ics(url)

    agora = dt.datetime.fromisoformat(args.agora).replace(tzinfo=FUSO) if args.agora \
        else dt.datetime.now(FUSO)
    dias, avisos = montar_disponibilidade(ics, agora)
    for a in avisos:
        print("AVISO:", a)

    # só regrava se a disponibilidade mudou — evita commit a cada hora à toa
    if os.path.exists(args.saida):
        with open(args.saida, encoding="utf-8") as f:
            try:
                if json.load(f).get("dias") == dias:
                    print("Sem mudanças na agenda.")
                    return
            except json.JSONDecodeError:
                pass

    os.makedirs(os.path.dirname(os.path.abspath(args.saida)), exist_ok=True)
    with open(args.saida, "w", encoding="utf-8") as f:
        json.dump({"atualizado": agora.isoformat(timespec="minutes"), "dias": dias},
                  f, ensure_ascii=False, indent=2)
    livres = sum(1 for d in dias for h in d["horarios"] if h["status"] != "ocupado")
    print("Agenda atualizada: %d dia(s), %d horário(s) disponível(is)." % (len(dias), livres))


if __name__ == "__main__":
    main()
