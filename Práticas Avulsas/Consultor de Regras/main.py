"""
Consulta de Regras de Portabilidade

Programa simples para consultar bancos destino disponíveis com base em uma planilha Excel editável.

Dependências:
    pip install -r requirements.txt

Executar:
    python main.py
"""

import os
import re
import sys
import unicodedata
import subprocess
from pathlib import Path
from datetime import datetime

import pandas as pd
import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk


APP_TITLE = "Consulta de Regras de Portabilidade"
EXCEL_FILE = "regras_portabilidade.xlsx"
SHEET_NAME = "Regras"

REQUIRED_COLUMNS = [
    "Banco_Destino",
    "Banco_Origem",
    "Categoria_Origem",
    "Minimo_Parcelas_Pagas",
    "Status",
    "Regra_Descricao",
    "Observacao",
]

CATEGORIAS = [
    "BANCO_DE_REDE",
    "BANCO_ORIGEM_CORBAN",
]

INITIAL_CSV = r"""Banco_Destino;Banco_Origem;Categoria_Origem;Minimo_Parcelas_Pagas;Status;Regra_Descricao;Observacao;Fonte_Pagina;Fonte_Arquivo
BMG;C6;BANCO_ESPECIFICO;;CONDICIONAL;Consulte seu gerente comercial.;Consulte seu gerente comercial.;3;REGRA DE PMT PAGA (6) (1).pdf
BMG;DAYCOVAL;BANCO_ESPECIFICO;;CONDICIONAL;Consulte seu gerente comercial.;Consulte seu gerente comercial.;3;REGRA DE PMT PAGA (6) (1).pdf
BMG;PAN;BANCO_ESPECIFICO;;CONDICIONAL;Consulte seu gerente comercial.;Consulte seu gerente comercial.;3;REGRA DE PMT PAGA (6) (1).pdf
BMG;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;Consulte seu gerente comercial.;Consulte seu gerente comercial.;3;REGRA DE PMT PAGA (6) (1).pdf
BMG;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;Consulte seu gerente comercial.;Consulte seu gerente comercial.;3;REGRA DE PMT PAGA (6) (1).pdf
BMG;SAFRA;BANCO_ESPECIFICO;12;SIM;Mínimo de 12 pagas.;;3;REGRA DE PMT PAGA (6) (1).pdf
BMG;BANCOS COM RETORNO DE ORIGEM CORBAN;BANCO_ORIGEM_CORBAN;0;SIM;Bancos com retorno de origem corban: 0 pagas.;Deve-se verificar comissionamento.;3;REGRA DE PMT PAGA (6) (1).pdf
BMG;BANCOS DE REDE;BANCO_DE_REDE;0;SIM;Bancos de rede: 0 parcelas pagas.;;3;REGRA DE PMT PAGA (6) (1).pdf
BMG;BCV;BANCO_ESPECIFICO;;NAO;Não porta: BCV.;Banco não aceito para portabilidade.;3;REGRA DE PMT PAGA (6) (1).pdf
BMG;CIFRA;BANCO_ESPECIFICO;;NAO;Não porta: CIFRA.;Banco não aceito para portabilidade.;3;REGRA DE PMT PAGA (6) (1).pdf
BMG;AGIBANK;BANCO_ESPECIFICO;;NAO;Não porta: AGIBANK.;Banco não aceito para portabilidade.;3;REGRA DE PMT PAGA (6) (1).pdf
BMG;ITAÚ BBA;BANCO_ESPECIFICO;;NAO;Não porta: ITAÚ BBA.;Banco não aceito para portabilidade.;3;REGRA DE PMT PAGA (6) (1).pdf
BMG;OLÉ;BANCO_ESPECIFICO;;NAO;Não porta: OLÉ.;Banco não aceito para portabilidade.;3;REGRA DE PMT PAGA (6) (1).pdf
BMG;PICPAY;BANCO_ESPECIFICO;;NAO;Não porta: PICPAY.;Banco não aceito para portabilidade.;3;REGRA DE PMT PAGA (6) (1).pdf
BANRISUL;C6;BANCO_ESPECIFICO;;CONDICIONAL;Consulte seu gerente comercial.;Consulte seu gerente comercial.;4;REGRA DE PMT PAGA (6) (1).pdf
BANRISUL;DAYCOVAL;BANCO_ESPECIFICO;;CONDICIONAL;Consulte seu gerente comercial.;Consulte seu gerente comercial.;4;REGRA DE PMT PAGA (6) (1).pdf
BANRISUL;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;Consulte seu gerente comercial.;Consulte seu gerente comercial.;4;REGRA DE PMT PAGA (6) (1).pdf
BANRISUL;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;Consulte seu gerente comercial.;Consulte seu gerente comercial.;4;REGRA DE PMT PAGA (6) (1).pdf
BANRISUL;PAN;BANCO_ESPECIFICO;30;SIM;Mínimo de 30 pagas.;;4;REGRA DE PMT PAGA (6) (1).pdf
BANRISUL;SAFRA;BANCO_ESPECIFICO;15;SIM;Mínimo de 15 pagas.;;4;REGRA DE PMT PAGA (6) (1).pdf
BANRISUL;INBURSA;BANCO_ESPECIFICO;15;SIM;Mínimo de 15 pagas.;;4;REGRA DE PMT PAGA (6) (1).pdf
BANRISUL;DEMAIS BANCOS CIP;DEMAIS_BANCOS_CIP;12;SIM;Demais bancos participantes da CIP: 12 pagas.;Regra genérica.;4;REGRA DE PMT PAGA (6) (1).pdf
BANRISUL;BANCOS DE REDE;BANCO_DE_REDE;1;SIM;Bancos de rede: 1 parcela paga.;Regra genérica.;4;REGRA DE PMT PAGA (6) (1).pdf
BANRISUL;BARIGUI;BANCO_ESPECIFICO;;NAO;Não porta: BARIGUI.;Banco não aceito para portabilidade.;4;REGRA DE PMT PAGA (6) (1).pdf
BRB (INCONTA);BANCOS DE ORIGEM CORBAN;BANCO_ORIGEM_CORBAN;12;SIM;Porta a partir de 12 parcelas pagas bancos de origem Corban.;;5;REGRA DE PMT PAGA (6) (1).pdf
BRB (INCONTA);BANCOS DE ORIGEM AGÊNCIA;BANCO_ORIGEM_AGENCIA;1;SIM;Porta a partir de 1 parcela paga bancos de origem agência.;;5;REGRA DE PMT PAGA (6) (1).pdf
BRB (INCONTA);INBURSA;BANCO_ESPECIFICO;;NAO;Não porta: INBURSA.;;5;REGRA DE PMT PAGA (6) (1).pdf
BRB (INCONTA);PICPAY;BANCO_ESPECIFICO;;NAO;Não porta: PICPAY.;;5;REGRA DE PMT PAGA (6) (1).pdf
BRB (INCONTA);PAGBANK;BANCO_ESPECIFICO;;NAO;Não porta: PAGBANK.;;5;REGRA DE PMT PAGA (6) (1).pdf
BRB (INCONTA);BRADESCARD S.A;BANCO_ESPECIFICO;;NAO;Não porta: BRADESCARD S.A.;;5;REGRA DE PMT PAGA (6) (1).pdf
BRB (INCONTA);SANTINVEST;BANCO_ESPECIFICO;;NAO;Não porta: SANTINVEST.;;5;REGRA DE PMT PAGA (6) (1).pdf
BRB (INCONTA);C6;BANCO_ESPECIFICO;;NAO;Não porta: C6.;;5;REGRA DE PMT PAGA (6) (1).pdf
BRB (INCONTA);AGIBANK;BANCO_ESPECIFICO;;NAO;Não porta: AGIBANK.;;5;REGRA DE PMT PAGA (6) (1).pdf
BRB (CONSIG360);BANCOS DE ORIGEM CORBAN;BANCO_ORIGEM_CORBAN;12;SIM;Bancos de origem Corban: a partir de 12 parcelas pagas.;;6;REGRA DE PMT PAGA (6) (1).pdf
BRB (CONSIG360);BANCOS DE ORIGEM AGÊNCIA;BANCO_ORIGEM_AGENCIA;1;SIM;Bancos de origem agência: a partir de 1 parcela paga.;;6;REGRA DE PMT PAGA (6) (1).pdf
BRB (CONSIG360);PINE;BANCO_ESPECIFICO;1;SIM;PINE: a partir de 1 parcela paga.;;6;REGRA DE PMT PAGA (6) (1).pdf
BRB (CONSIG360);MERCANTIL;BANCO_ESPECIFICO;1;SIM;MERCANTIL: a partir de 1 parcela paga.;;6;REGRA DE PMT PAGA (6) (1).pdf
BRB (CONSIG360);QI TECH;BANCO_ESPECIFICO;1;SIM;QI TECH: a partir de 1 parcela paga.;;6;REGRA DE PMT PAGA (6) (1).pdf
BRB (CONSIG360);DAYCOVAL;BANCO_ESPECIFICO;1;SIM;DAYCOVAL: a partir de 1 parcela paga.;;6;REGRA DE PMT PAGA (6) (1).pdf
BRB (CONSIG360);PARATI;BANCO_ESPECIFICO;1;SIM;PARATI: a partir de 1 parcela paga.;;6;REGRA DE PMT PAGA (6) (1).pdf
BRB (CONSIG360);INTER;BANCO_ESPECIFICO;1;SIM;INTER: a partir de 1 parcela paga.;;6;REGRA DE PMT PAGA (6) (1).pdf
BRB (CONSIG360);INBURSA;BANCO_ESPECIFICO;;NAO;Não porta: INBURSA.;;6;REGRA DE PMT PAGA (6) (1).pdf
BRB (CONSIG360);PICPAY;BANCO_ESPECIFICO;;NAO;Não porta: PICPAY.;;6;REGRA DE PMT PAGA (6) (1).pdf
BRB (CONSIG360);AGIBANK;BANCO_ESPECIFICO;;NAO;Não porta: AGIBANK.;;6;REGRA DE PMT PAGA (6) (1).pdf
BRB (CONSIG360);C6;BANCO_ESPECIFICO;;NAO;Não porta: C6.;;6;REGRA DE PMT PAGA (6) (1).pdf
C6;CONTRATO DE ORIGEM AGÊNCIA;BANCO_ORIGEM_AGENCIA;0;SIM;Contrato de origem agência: 0 pagas.;;7;REGRA DE PMT PAGA (6) (1).pdf
C6;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ / SANTANDER: consulte seu gerente comercial.;;7;REGRA DE PMT PAGA (6) (1).pdf
C6;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ / SANTANDER: consulte seu gerente comercial.;;7;REGRA DE PMT PAGA (6) (1).pdf
C6;CONTRATO DE ORIGEM CORBAN;BANCO_ORIGEM_CORBAN;12;SIM;Contrato de origem corban: 12 pagas ou 360 dias.;Também aceita por 360 dias.;7;REGRA DE PMT PAGA (6) (1).pdf
C6;PAN;BANCO_ESPECIFICO;37;SIM;PAN: mínimo de 37 pagas.;;7;REGRA DE PMT PAGA (6) (1).pdf
C6;FACTA;BANCO_ESPECIFICO;13;SIM;FACTA: mínimo de 13 pagas.;;7;REGRA DE PMT PAGA (6) (1).pdf
C6;PARANÁ;BANCO_ESPECIFICO;13;SIM;PARANÁ: mínimo de 13 pagas.;;7;REGRA DE PMT PAGA (6) (1).pdf
C6;MERCANTIL;BANCO_ESPECIFICO;13;SIM;MERCANTIL: mínimo de 13 pagas.;;7;REGRA DE PMT PAGA (6) (1).pdf
C6;DAYCOVAL;BANCO_ESPECIFICO;;NAO;Não porta: DAYCOVAL.;;7;REGRA DE PMT PAGA (6) (1).pdf
C6;AGIBANK;BANCO_ESPECIFICO;;NAO;Não porta: AGIBANK.;;7;REGRA DE PMT PAGA (6) (1).pdf
C6;INBURSA;BANCO_ESPECIFICO;;NAO;Não porta: INBURSA.;;7;REGRA DE PMT PAGA (6) (1).pdf
C6;BRB;BANCO_ESPECIFICO;;NAO;Não porta: BRB.;;7;REGRA DE PMT PAGA (6) (1).pdf
C6;SAFRA;BANCO_ESPECIFICO;;NAO;Não porta: SAFRA.;;7;REGRA DE PMT PAGA (6) (1).pdf
C6;QI TECH;BANCO_ESPECIFICO;;NAO;Não porta: QI TECH.;;7;REGRA DE PMT PAGA (6) (1).pdf
DAYCOVAL;FACTA;BANCO_ESPECIFICO;24;SIM;FACTA: mínimo de 24 pagas.;;8;REGRA DE PMT PAGA (6) (1).pdf
DAYCOVAL;BANCO NBC;BANCO_ESPECIFICO;24;SIM;BANCO NBC: mínimo de 24 pagas.;;8;REGRA DE PMT PAGA (6) (1).pdf
DAYCOVAL;PAN;BANCO_ESPECIFICO;;CONDICIONAL;PAN: consulte seu gerente comercial.;;8;REGRA DE PMT PAGA (6) (1).pdf
DAYCOVAL;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ: consulte seu gerente comercial.;;8;REGRA DE PMT PAGA (6) (1).pdf
DAYCOVAL;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;SANTANDER: consulte seu gerente comercial.;;8;REGRA DE PMT PAGA (6) (1).pdf
DAYCOVAL;INBURSA;BANCO_ESPECIFICO;13;SIM;INBURSA: mínimo de 13 pagas.;;8;REGRA DE PMT PAGA (6) (1).pdf
DAYCOVAL;AGIBANK;BANCO_ESPECIFICO;15;SIM;AGIBANK: mínimo de 15 pagas.;;8;REGRA DE PMT PAGA (6) (1).pdf
DAYCOVAL;BANCOS COM ORIGEM CORBAN E AGÊNCIA;ORIGEM_CORBAN_AGENCIA;6;SIM;Bancos com origem corban e agência: mínimo de 6 parcelas pagas.;Conferir comissionamento.;8;REGRA DE PMT PAGA (6) (1).pdf
DAYCOVAL;ALFA;BANCO_ESPECIFICO;;NAO;Não porta: ALFA.;;8;REGRA DE PMT PAGA (6) (1).pdf
DAYCOVAL;SAFRA;BANCO_ESPECIFICO;;NAO;Não porta: SAFRA.;;8;REGRA DE PMT PAGA (6) (1).pdf
DAYCOVAL;C6;BANCO_ESPECIFICO;;NAO;Não porta: C6.;;8;REGRA DE PMT PAGA (6) (1).pdf
DIGA;DAYCOVAL;BANCO_ESPECIFICO;;CONDICIONAL;DAYCOVAL: consulte seu gerente comercial.;;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;PAN;BANCO_ESPECIFICO;;CONDICIONAL;PAN: consulte seu gerente comercial.;;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ: consulte seu gerente comercial.;;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;SANTANDER: consulte seu gerente comercial.;;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;AGIBANK;BANCO_ESPECIFICO;12;SIM;AGIBANK: permitido somente a partir de 12 parcelas pagas.;Canal Corban quando aplicável.;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;MERCANTIL;BANCO_ESPECIFICO;12;SIM;MERCANTIL: permitido somente a partir de 12 parcelas pagas.;Canal Corban quando aplicável.;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;PARANÁ BANCO;BANCO_ESPECIFICO;12;SIM;PARANÁ BANCO: permitido somente a partir de 12 parcelas pagas.;Canal Corban quando aplicável.;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;PARATI;BANCO_ESPECIFICO;12;SIM;PARATI: permitido somente a partir de 12 parcelas pagas.;Canal Corban quando aplicável.;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;BANRISUL;BANCO_ESPECIFICO;12;SIM;BANRISUL: permitido somente a partir de 12 parcelas pagas.;Canal Corban quando aplicável.;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;BRB;BANCO_ESPECIFICO;;NAO;Não porta: BRB.;;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;QI TECH;BANCO_ESPECIFICO;;NAO;Não porta: QI TECH.;;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;C6;BANCO_ESPECIFICO;;NAO;Não porta: C6.;;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;FACTA;BANCO_ESPECIFICO;;NAO;Não porta: FACTA.;;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;SAFRA;BANCO_ESPECIFICO;;NAO;Não porta: SAFRA.;;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;ALFA;BANCO_ESPECIFICO;;NAO;Não porta: ALFA.;;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;BNP PARIBAS;BANCO_ESPECIFICO;;NAO;Não porta: BNP PARIBAS.;;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;PICPAY;BANCO_ESPECIFICO;;NAO;Não porta: PICPAY.;;9;REGRA DE PMT PAGA (6) (1).pdf
DIGA;DEMAIS BANCOS;DEMAIS_BANCOS;1;SIM;Demais bancos: a partir de 1 parcela paga.;;9;REGRA DE PMT PAGA (6) (1).pdf
DIGIO;C6;BANCO_ESPECIFICO;;CONDICIONAL;C6: consulte seu gerente comercial.;;10;REGRA DE PMT PAGA (6) (1).pdf
DIGIO;DAYCOVAL;BANCO_ESPECIFICO;;CONDICIONAL;DAYCOVAL: consulte seu gerente comercial.;;10;REGRA DE PMT PAGA (6) (1).pdf
DIGIO;PAN;BANCO_ESPECIFICO;;CONDICIONAL;PAN: consulte seu gerente comercial.;;10;REGRA DE PMT PAGA (6) (1).pdf
DIGIO;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ: consulte seu gerente comercial.;;10;REGRA DE PMT PAGA (6) (1).pdf
DIGIO;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;SANTANDER: consulte seu gerente comercial.;;10;REGRA DE PMT PAGA (6) (1).pdf
DIGIO;DEMAIS BANCOS CIP;DEMAIS_BANCOS_CIP;12;SIM;Demais bancos participantes da CIP, origem corban: 12 pagas.;;10;REGRA DE PMT PAGA (6) (1).pdf
DIGIO;BANCOS DE REDE;BANCO_DE_REDE;0;SIM;Bancos de rede, origem agência: 0 pagas.;;10;REGRA DE PMT PAGA (6) (1).pdf
DIGIO;BRADESCO S.A;BANCO_ESPECIFICO;;NAO;Não porta: BRADESCO S.A.;;10;REGRA DE PMT PAGA (6) (1).pdf
DIGIO;BANRISUL;BANCO_ESPECIFICO;;NAO;Não porta: BANRISUL.;;10;REGRA DE PMT PAGA (6) (1).pdf
DIGIO;BANCO DO BRASIL;BANCO_ESPECIFICO;;NAO;Não porta: BANCO DO BRASIL.;;10;REGRA DE PMT PAGA (6) (1).pdf
DIGIO;BRADESCO FINANCIAMENTO;BANCO_ESPECIFICO;;NAO;Não porta: BRADESCO FINANCIAMENTO.;;10;REGRA DE PMT PAGA (6) (1).pdf
FACTA;BMG;BANCO_ESPECIFICO;12;SIM;BMG: mínimo de 12 pagas.;;11;REGRA DE PMT PAGA (6) (1).pdf
FACTA;C6;BANCO_ESPECIFICO;;CONDICIONAL;C6: consulte seu gerente comercial.;;11;REGRA DE PMT PAGA (6) (1).pdf
FACTA;DAYCOVAL;BANCO_ESPECIFICO;;CONDICIONAL;DAYCOVAL: consulte seu gerente comercial.;;11;REGRA DE PMT PAGA (6) (1).pdf
FACTA;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ: consulte seu gerente comercial.;;11;REGRA DE PMT PAGA (6) (1).pdf
FACTA;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;SANTANDER: consulte seu gerente comercial.;;11;REGRA DE PMT PAGA (6) (1).pdf
FACTA;AGIBANK;BANCO_ESPECIFICO;15;SIM;AGIBANK: mínimo de 15 pagas.;;11;REGRA DE PMT PAGA (6) (1).pdf
FACTA;PARANÁ;BANCO_ESPECIFICO;15;SIM;PARANÁ: mínimo de 15 pagas.;;11;REGRA DE PMT PAGA (6) (1).pdf
FACTA;PAN;BANCO_ESPECIFICO;30;SIM;PAN: mínimo de 30 pagas.;;11;REGRA DE PMT PAGA (6) (1).pdf
FACTA;DEMAIS BANCOS;DEMAIS_BANCOS;0;SIM;Demais bancos mínimo de 0 parcelas pagas.;Conferir comissionamento.;11;REGRA DE PMT PAGA (6) (1).pdf
FACTA;PAULISTA;BANCO_ESPECIFICO;;NAO;Não porta: PAULISTA.;;11;REGRA DE PMT PAGA (6) (1).pdf
FACTA;INBURSA;BANCO_ESPECIFICO;;NAO;Não porta: INBURSA.;;11;REGRA DE PMT PAGA (6) (1).pdf
FACTA;PINE;BANCO_ESPECIFICO;;NAO;Não porta: PINE.;;11;REGRA DE PMT PAGA (6) (1).pdf
FACTA;SOCICRED;BANCO_ESPECIFICO;;NAO;Não porta: SOCICRED.;;11;REGRA DE PMT PAGA (6) (1).pdf
FOX;CONSULTAR SUPORTE OPERACIONAL;SUPORTE_OPERACIONAL;;CONDICIONAL;Não porta: consultar com suporte operacional.;Verificar suporte operacional antes de seguir.;12;REGRA DE PMT PAGA (6) (1).pdf
FOX;SANTANDER;BANCO_ESPECIFICO;12;SIM;SANTANDER: 12 parcelas pagas.;;12;REGRA DE PMT PAGA (6) (1).pdf
FOX;BANRISUL;BANCO_ESPECIFICO;12;SIM;BANRISUL: 12 parcelas pagas.;;12;REGRA DE PMT PAGA (6) (1).pdf
FOX;BRB;BANCO_ESPECIFICO;12;SIM;BRB: 12 parcelas pagas.;;12;REGRA DE PMT PAGA (6) (1).pdf
FOX;AGIBANK;BANCO_ESPECIFICO;12;SIM;AGIBANK: 12 parcelas pagas.;;12;REGRA DE PMT PAGA (6) (1).pdf
FOX;PARATI;BANCO_ESPECIFICO;12;SIM;PARATI: 12 parcelas pagas.;;12;REGRA DE PMT PAGA (6) (1).pdf
FOX;FINANCEIRA MERCANTIL;BANCO_ESPECIFICO;12;SIM;FINANCEIRA MERCANTIL: 12 parcelas pagas.;;12;REGRA DE PMT PAGA (6) (1).pdf
FOX;PAN;BANCO_ESPECIFICO;12;SIM;PAN: 12 parcelas pagas.;;12;REGRA DE PMT PAGA (6) (1).pdf
FOX;DAYCOVAL;BANCO_ESPECIFICO;12;SIM;DAYCOVAL: 12 parcelas pagas.;;12;REGRA DE PMT PAGA (6) (1).pdf
FOX;BRB FINANCEIRA;BANCO_ESPECIFICO;12;SIM;BRB FINANCEIRA: 12 parcelas pagas.;;12;REGRA DE PMT PAGA (6) (1).pdf
FOX;MERCANTIL;BANCO_ESPECIFICO;12;SIM;MERCANTIL: 12 parcelas pagas.;;12;REGRA DE PMT PAGA (6) (1).pdf
FOX;DEMAIS BANCOS;DEMAIS_BANCOS;1;SIM;Demais bancos: a partir de 1 parcela paga.;;12;REGRA DE PMT PAGA (6) (1).pdf
HAPPY;PAN;BANCO_ESPECIFICO;12;SIM;PAN: mínimo de 12 pagas.;;13;REGRA DE PMT PAGA (6) (1).pdf
HAPPY;DEMAIS BANCOS;DEMAIS_BANCOS;1;SIM;Quantidade de parcelas pagas: a partir de 1 parcela paga.;;13;REGRA DE PMT PAGA (6) (1).pdf
HAPPY;CAIXA ECONÔMICA;BANCO_ESPECIFICO;;NAO;Não porta: CAIXA ECONÔMICA.;;13;REGRA DE PMT PAGA (6) (1).pdf
HAPPY;NBC BANK;BANCO_ESPECIFICO;;NAO;Não porta: NBC BANK.;;13;REGRA DE PMT PAGA (6) (1).pdf
HAPPY;PICPAY;BANCO_ESPECIFICO;;NAO;Não porta: PICPAY.;;13;REGRA DE PMT PAGA (6) (1).pdf
HAPPY;PINE;BANCO_ESPECIFICO;;NAO;Não porta: PINE.;;13;REGRA DE PMT PAGA (6) (1).pdf
HAPPY;INBURSA;BANCO_ESPECIFICO;;NAO;Não porta: INBURSA.;;13;REGRA DE PMT PAGA (6) (1).pdf
HAPPY;C6;BANCO_ESPECIFICO;;NAO;Não porta: C6.;;13;REGRA DE PMT PAGA (6) (1).pdf
ICRED;PAN;BANCO_ESPECIFICO;12;SIM;PAN: mínimo de 12 pagas.;;14;REGRA DE PMT PAGA (6) (1).pdf
ICRED;C6;BANCO_ESPECIFICO;;CONDICIONAL;C6: temporariamente indisponível.;Verificar disponibilidade antes de seguir.;14;REGRA DE PMT PAGA (6) (1).pdf
ICRED;DEMAIS BANCOS;DEMAIS_BANCOS;1;SIM;Demais bancos: 1 paga.;;14;REGRA DE PMT PAGA (6) (1).pdf
ICRED;INBURSA;BANCO_ESPECIFICO;;NAO;Não porta: INBURSA.;;14;REGRA DE PMT PAGA (6) (1).pdf
ICRED;QI SOCIEDADE DE CRÉDITO DIRETO;BANCO_ESPECIFICO;;NAO;Não porta: QI SOCIEDADE DE CRÉDITO DIRETO.;;14;REGRA DE PMT PAGA (6) (1).pdf
ICRED;PINE;BANCO_ESPECIFICO;;NAO;Não porta: PINE.;;14;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;DAYCOVAL;BANCO_ESPECIFICO;;CONDICIONAL;DAYCOVAL: consulte seu gerente comercial.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;PAN;BANCO_ESPECIFICO;;CONDICIONAL;PAN: consulte seu gerente comercial.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ: consulte seu gerente comercial.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;SANTANDER: consulte seu gerente comercial.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;AGIBANK;BANCO_ESPECIFICO;13;SIM;AGIBANK: a partir de 13 parcelas pagas.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;PARANÁ;BANCO_ESPECIFICO;13;SIM;PARANÁ: a partir de 13 parcelas pagas.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;PARATI;BANCO_ESPECIFICO;13;SIM;PARATI: a partir de 13 parcelas pagas.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;MERCANTIL;BANCO_ESPECIFICO;13;SIM;MERCANTIL: a partir de 13 parcelas pagas.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;DEMAIS BANCOS;DEMAIS_BANCOS;2;SIM;Demais bancos: 02 parcelas pagas.;Canal agência.;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;SABEMI;BANCO_ESPECIFICO;;NAO;Não porta: SABEMI.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;QI;BANCO_ESPECIFICO;;NAO;Não porta: QI.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;SAFRA;BANCO_ESPECIFICO;;NAO;Não porta: SAFRA.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;FACTA;BANCO_ESPECIFICO;;NAO;Não porta: FACTA.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;BNP;BANCO_ESPECIFICO;;NAO;Não porta: BNP.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;PICPAY;BANCO_ESPECIFICO;;NAO;Não porta: PICPAY.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;C6;BANCO_ESPECIFICO;;NAO;Não porta: C6.;;15;REGRA DE PMT PAGA (6) (1).pdf
INBURSA;ALFA;BANCO_ESPECIFICO;;NAO;Não porta: ALFA.;;15;REGRA DE PMT PAGA (6) (1).pdf
PAGBANK;C6;BANCO_ESPECIFICO;;CONDICIONAL;C6: consulte seu gerente comercial.;;16;REGRA DE PMT PAGA (6) (1).pdf
PAGBANK;DAYCOVAL;BANCO_ESPECIFICO;;CONDICIONAL;DAYCOVAL: consulte seu gerente comercial.;;16;REGRA DE PMT PAGA (6) (1).pdf
PAGBANK;PAN;BANCO_ESPECIFICO;;CONDICIONAL;PAN: consulte seu gerente comercial.;;16;REGRA DE PMT PAGA (6) (1).pdf
PAGBANK;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ: consulte seu gerente comercial.;;16;REGRA DE PMT PAGA (6) (1).pdf
PAGBANK;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;SANTANDER: consulte seu gerente comercial.;;16;REGRA DE PMT PAGA (6) (1).pdf
PAGBANK;BANCOS DE REDE;BANCO_DE_REDE;12;SIM;Banco de rede, origem agência ou corban: mínimo de 12 parcelas pagas.;;16;REGRA DE PMT PAGA (6) (1).pdf
PAN;INBURSA;BANCO_ESPECIFICO;12;SIM;INBURSA: 12 pagas.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;QI TECH;BANCO_ESPECIFICO;12;SIM;QI TECH: 12 pagas.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;ZEMA;BANCO_ESPECIFICO;12;SIM;ZEMA: 12 pagas.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;PINE;BANCO_ESPECIFICO;12;SIM;PINE: 12 pagas.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;ITAÚ CONSIGNADO;BANCO_ESPECIFICO;15;SIM;ITAÚ CONSIGNADO: 15 pagas.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;SAFRA;BANCO_ESPECIFICO;15;SIM;SAFRA: 15 pagas.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;FACTA FINANCEIRA;BANCO_ESPECIFICO;16;SIM;FACTA FINANCEIRA: 16 pagas.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;BANRISUL;BANCO_ESPECIFICO;30;SIM;BANRISUL: 30 pagas.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;C6;BANCO_ESPECIFICO;;CONDICIONAL;C6: consulte seu gerente comercial.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;DAYCOVAL;BANCO_ESPECIFICO;;CONDICIONAL;DAYCOVAL: consulte seu gerente comercial.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ: consulte seu gerente comercial.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;SANTANDER: consulte seu gerente comercial.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;BANCOS DE REDE;BANCO_DE_REDE;1;SIM;Banco de rede, origem agência: 01 parcela paga.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;DEMAIS BANCOS CIP;DEMAIS_BANCOS_CIP;12;SIM;Demais bancos da CIP, origem corban: mínimo de 12 parcelas pagas.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;AGIBANK;BANCO_ESPECIFICO;;NAO;Não porta: AGIBANK.;;17;REGRA DE PMT PAGA (6) (1).pdf
PAN;BRB;BANCO_ESPECIFICO;;NAO;Não porta: BRB.;;17;REGRA DE PMT PAGA (6) (1).pdf
PARANÁ BANCO;C6;BANCO_ESPECIFICO;;CONDICIONAL;C6: consulte seu gerente comercial.;;18;REGRA DE PMT PAGA (6) (1).pdf
PARANÁ BANCO;DAYCOVAL;BANCO_ESPECIFICO;;CONDICIONAL;DAYCOVAL: consulte seu gerente comercial.;;18;REGRA DE PMT PAGA (6) (1).pdf
PARANÁ BANCO;PAN;BANCO_ESPECIFICO;;CONDICIONAL;PAN: consulte seu gerente comercial.;;18;REGRA DE PMT PAGA (6) (1).pdf
PARANÁ BANCO;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ: consulte seu gerente comercial.;;18;REGRA DE PMT PAGA (6) (1).pdf
PARANÁ BANCO;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;SANTANDER: consulte seu gerente comercial.;;18;REGRA DE PMT PAGA (6) (1).pdf
PARANÁ BANCO;BANCOS DE REDE;BANCO_DE_REDE;1;SIM;Banco de rede, origem agência: 01 parcela paga.;;18;REGRA DE PMT PAGA (6) (1).pdf
PARANÁ BANCO;DEMAIS BANCOS CIP;DEMAIS_BANCOS_CIP;12;SIM;Demais bancos da CIP, origem corban: mínimo de 12 parcelas pagas.;;18;REGRA DE PMT PAGA (6) (1).pdf
PARANÁ BANCO;BARIGUI;BANCO_ESPECIFICO;;NAO;Não porta: BARIGUI.;;18;REGRA DE PMT PAGA (6) (1).pdf
PARANÁ BANCO;FACTA;BANCO_ESPECIFICO;;NAO;Não porta: FACTA.;;18;REGRA DE PMT PAGA (6) (1).pdf
PARANÁ BANCO;MERCANTIL;BANCO_ESPECIFICO;;NAO;Não porta: MERCANTIL.;;18;REGRA DE PMT PAGA (6) (1).pdf
PICPAY;C6;BANCO_ESPECIFICO;;CONDICIONAL;C6: consulte seu gerente comercial.;;19;REGRA DE PMT PAGA (6) (1).pdf
PICPAY;DAYCOVAL;BANCO_ESPECIFICO;;CONDICIONAL;DAYCOVAL: consulte seu gerente comercial.;;19;REGRA DE PMT PAGA (6) (1).pdf
PICPAY;PAN;BANCO_ESPECIFICO;;CONDICIONAL;PAN: consulte seu gerente comercial.;;19;REGRA DE PMT PAGA (6) (1).pdf
PICPAY;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ: consulte seu gerente comercial.;;19;REGRA DE PMT PAGA (6) (1).pdf
PICPAY;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;SANTANDER: consulte seu gerente comercial.;;19;REGRA DE PMT PAGA (6) (1).pdf
PICPAY;BANCOS DE REDE;BANCO_DE_REDE;1;SIM;Banco de rede, origem agência: 01 parcela paga.;;19;REGRA DE PMT PAGA (6) (1).pdf
PICPAY;DEMAIS BANCOS CIP;DEMAIS_BANCOS_CIP;12;SIM;Demais bancos da CIP, origem corban: mínimo de 12 parcelas pagas.;;19;REGRA DE PMT PAGA (6) (1).pdf
PICPAY;MERCANTIL;BANCO_ESPECIFICO;;NAO;Não porta: MERCANTIL.;;19;REGRA DE PMT PAGA (6) (1).pdf
PICPAY;INBURSA;BANCO_ESPECIFICO;;NAO;Não porta: INBURSA.;;19;REGRA DE PMT PAGA (6) (1).pdf
PICPAY;BRB;BANCO_ESPECIFICO;;NAO;Não porta: BRB.;;19;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT PURA COM REDUÇÃO;AGIBANK;BANCO_ESPECIFICO;12;SIM;AGIBANK: mínimo de 12 pagas.;Regra 1: port pura com redução de parcela.;20;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT PURA COM REDUÇÃO;BANRISUL;BANCO_ESPECIFICO;12;SIM;BANRISUL: mínimo de 12 pagas.;Regra 1: port pura com redução de parcela.;20;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT PURA COM REDUÇÃO;BRB;BANCO_ESPECIFICO;12;SIM;BRB: mínimo de 12 pagas.;Regra 1: port pura com redução de parcela.;20;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT PURA COM REDUÇÃO;MERCANTIL;BANCO_ESPECIFICO;12;SIM;MERCANTIL: mínimo de 12 pagas.;Regra 1: port pura com redução de parcela.;20;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT PURA COM REDUÇÃO;PAGBANK;BANCO_ESPECIFICO;12;SIM;PAGBANK: mínimo de 12 pagas.;Regra 1: port pura com redução de parcela.;20;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT PURA COM REDUÇÃO;PARATI;BANCO_ESPECIFICO;12;SIM;PARATI: mínimo de 12 pagas.;Regra 1: port pura com redução de parcela.;20;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT PURA COM REDUÇÃO;SANTANDER;BANCO_ESPECIFICO;12;SIM;SANTANDER: mínimo de 12 pagas.;Regra 1: port pura com redução de parcela.;20;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT PURA COM REDUÇÃO;C6;BANCO_ESPECIFICO;;CONDICIONAL;C6: consulte seu gerente comercial.;;20;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT PURA COM REDUÇÃO;DAYCOVAL;BANCO_ESPECIFICO;;CONDICIONAL;DAYCOVAL: consulte seu gerente comercial.;;20;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT PURA COM REDUÇÃO;PAN;BANCO_ESPECIFICO;;CONDICIONAL;PAN: consulte seu gerente comercial.;;20;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT PURA COM REDUÇÃO;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ: consulte seu gerente comercial.;;20;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT PURA COM REDUÇÃO;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;SANTANDER: consulte seu gerente comercial.;;20;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT PURA COM REDUÇÃO;DEMAIS BANCOS;DEMAIS_BANCOS;1;SIM;Demais bancos: a partir de 1 parcela paga.;;20;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT PURA COM REDUÇÃO;CONSULTAR SUPORTE OPERACIONAL;SUPORTE_OPERACIONAL;;CONDICIONAL;Não porta: consultar lista com o suporte operacional.;;20;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;AGIBANK;BANCO_ESPECIFICO;12;SIM;AGIBANK: mínimo de 12 pagas.;Regra 1: port + refin.;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;BANRISUL;BANCO_ESPECIFICO;12;SIM;BANRISUL: mínimo de 12 pagas.;Regra 1: port + refin.;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;BRB;BANCO_ESPECIFICO;12;SIM;BRB: mínimo de 12 pagas.;Regra 1: port + refin.;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;MERCANTIL;BANCO_ESPECIFICO;12;SIM;MERCANTIL: mínimo de 12 pagas.;Regra 1: port + refin.;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;PAGBANK;BANCO_ESPECIFICO;12;SIM;PAGBANK: mínimo de 12 pagas.;Regra 1: port + refin.;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;PARATI;BANCO_ESPECIFICO;12;SIM;PARATI: mínimo de 12 pagas.;Regra 1: port + refin.;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;SANTANDER;BANCO_ESPECIFICO;12;SIM;SANTANDER: mínimo de 12 pagas.;Regra 1: port + refin.;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;C6;BANCO_ESPECIFICO;;CONDICIONAL;C6: consulte seu gerente comercial.;;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;DAYCOVAL;BANCO_ESPECIFICO;;CONDICIONAL;DAYCOVAL: consulte seu gerente comercial.;;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;PAN;BANCO_ESPECIFICO;;CONDICIONAL;PAN: consulte seu gerente comercial.;;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ: consulte seu gerente comercial.;;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;SANTANDER: consulte seu gerente comercial.;;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;SALDOS A PARTIR DE 6000;SALDO_A_PARTIR_6000;1;SIM;Para saldos a partir de R$ 6.000,00: liberação com 1 parcela paga.;Regra especial por saldo.;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;SALDOS DE 2000 A 5999;SALDO_2000_5999;15;SIM;Saldos de R$ 2.000,00 a R$ 5.999,00: 15 pagas para todos os bancos passíveis de port.;Regra especial por saldo.;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;DEMAIS BANCOS;DEMAIS_BANCOS;1;SIM;Demais bancos: a partir de 1 parcela paga.;;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - PORT + REFIN;CONSULTAR SUPORTE OPERACIONAL;SUPORTE_OPERACIONAL;;CONDICIONAL;Não porta: consultar lista com o suporte operacional.;;21;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - REGRA 2;BRB;BANCO_ESPECIFICO;12;SIM;BRB: mínimo de 12 pagas.;;22;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - REGRA 2;C6;BANCO_ESPECIFICO;;CONDICIONAL;C6: consulte seu gerente comercial.;;22;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - REGRA 2;DAYCOVAL;BANCO_ESPECIFICO;;CONDICIONAL;DAYCOVAL: consulte seu gerente comercial.;;22;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - REGRA 2;PAN;BANCO_ESPECIFICO;;CONDICIONAL;PAN: consulte seu gerente comercial.;;22;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - REGRA 2;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ: consulte seu gerente comercial.;;22;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - REGRA 2;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;SANTANDER: consulte seu gerente comercial.;;22;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - REGRA 2;DEMAIS BANCOS;DEMAIS_BANCOS;1;SIM;Demais bancos: liberação com 1 parcela paga.;;22;REGRA DE PMT PAGA (6) (1).pdf
QUALIBANKING - REGRA 2;CONSULTAR SUPORTE OPERACIONAL;SUPORTE_OPERACIONAL;;CONDICIONAL;Não porta: consultar lista com o suporte operacional.;;22;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;ITAÚ BMG;BANCO_ESPECIFICO;12;SIM;ITAÚ BMG: a partir de 12 pagas.;;23;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;PAN;BANCO_ESPECIFICO;;CONDICIONAL;PAN: consulte seu gerente comercial.;;23;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ: consulte seu gerente comercial.;;23;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;SANTANDER: consulte seu gerente comercial.;;23;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;AGIBANK;BANCO_ESPECIFICO;15;SIM;AGIBANK: a partir de 15 parcelas pagas.;;23;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;INBURSA;BANCO_ESPECIFICO;13;SIM;INBURSA: a partir de 13 pagas.;;23;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;FACTA;BANCO_ESPECIFICO;24;SIM;FACTA: a partir de 24 parcelas pagas.;;23;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;NBC;BANCO_ESPECIFICO;24;SIM;NBC: a partir de 24 parcelas pagas.;;23;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;BANCOS DE REDE;BANCO_DE_REDE;6;SIM;Bancos de Rede: contratos originados em agência, mínimo de 6 pagas.;;23;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;DEMAIS BANCOS;DEMAIS_BANCOS;;CONDICIONAL;Demais bancos: a partir de 360 dias da contratação.;Regra por tempo, não por parcelas.;23;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;C6;BANCO_ESPECIFICO;;NAO;Não porta: C6.;;23;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;SAFRA;BANCO_ESPECIFICO;;NAO;Não porta: SAFRA.;;23;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;ALFA;BANCO_ESPECIFICO;;NAO;Não porta: ALFA.;;23;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;DAYCOVAL;BANCO_ESPECIFICO;;NAO;Não porta: DAYCOVAL.;;23;REGRA DE PMT PAGA (6) (1).pdf
QUERO MAIS CRÉDITO;SANTANDER;BANCO_ESPECIFICO;;NAO;Não porta: SANTANDER.;;23;REGRA DE PMT PAGA (6) (1).pdf
SAFRA;C6;BANCO_ESPECIFICO;;CONDICIONAL;C6: consulte seu gerente comercial.;;24;REGRA DE PMT PAGA (6) (1).pdf
SAFRA;PAN;BANCO_ESPECIFICO;;CONDICIONAL;PAN: consulte seu gerente comercial.;;24;REGRA DE PMT PAGA (6) (1).pdf
SAFRA;OLÉ;BANCO_ESPECIFICO;;CONDICIONAL;OLÉ: consulte seu gerente comercial.;;24;REGRA DE PMT PAGA (6) (1).pdf
SAFRA;SANTANDER;BANCO_ESPECIFICO;;CONDICIONAL;SANTANDER: consulte seu gerente comercial.;;24;REGRA DE PMT PAGA (6) (1).pdf
SAFRA;FACTA;BANCO_ESPECIFICO;24;SIM;FACTA: a partir de 24 parcelas pagas.;;24;REGRA DE PMT PAGA (6) (1).pdf
SAFRA;BANCOS DE REDE;BANCO_DE_REDE;0;SIM;Portar com 0 pagas: só banco de rede.;Sem correspondente bancário.;24;REGRA DE PMT PAGA (6) (1).pdf
SAFRA;DAYCOVAL;BANCO_ESPECIFICO;;NAO;Não porta: DAYCOVAL.;;24;REGRA DE PMT PAGA (6) (1).pdf
SAFRA;INBURSA;BANCO_ESPECIFICO;;NAO;Não porta: INBURSA.;;24;REGRA DE PMT PAGA (6) (1).pdf
SAFRA;ALFA;BANCO_ESPECIFICO;;NAO;Não porta: ALFA.;;24;REGRA DE PMT PAGA (6) (1).pdf
"""


def resource_path(relative_path: str) -> Path:
    """
    Retorna o caminho correto do arquivo tanto rodando em Python normal
    quanto empacotado pelo PyInstaller.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / relative_path
    return Path(__file__).resolve().parent / relative_path


def normalizar_texto(texto) -> str:
    """
    Padroniza textos para comparação:
    - remove acentos
    - deixa maiúsculo
    - remove espaços duplicados
    - trata barras e hífens
    """
    if texto is None or pd.isna(texto):
        return ""

    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = texto.replace("/", " ")
    texto = texto.replace("-", " ")
    texto = texto.replace(".", " ")
    texto = texto.replace(",", " ")
    texto = " ".join(texto.split())

    # Remove códigos bancários usados antes do nome.
    # Ex.: "121 AGIBANK" vira "AGIBANK"; "169 OLE" vira "OLE".
    texto = re.sub(r"^\d{2,4}\s+", "", texto)

    # Variações comuns
    substituicoes = {
        "OLE": "OLE",
        "OLÉ": "OLE",
        "C6 BANK": "C6",
        "BANCO C6": "C6",
        "PARANA BANCO": "PARANA",
        "PARANÁ BANCO": "PARANA",
        "BANCO PARANA": "PARANA",
        "BANCO PARANÁ": "PARANA",
        "BANCO PAN": "PAN",
        "BANCO DAYCOVAL": "DAYCOVAL",
        "BANCO SAFRA": "SAFRA",
        "BANCO BMG": "BMG",
        "MERCANTIL DO BRASIL": "MERCANTIL",
        "BANCO AGIBANK": "AGIBANK",
    }

    return substituicoes.get(texto, texto)


def criar_excel_modelo(caminho: Path):
    """
    Cria um Excel inicial caso o arquivo não exista.
    O arquivo é criado a partir do CSV interno para facilitar manutenção.
    """
    from io import StringIO

    df = pd.read_csv(StringIO(INITIAL_CSV), sep=";")
    with pd.ExcelWriter(caminho, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=SHEET_NAME)

        ajuda = pd.DataFrame({
            "Campo": [
                "Banco_Destino",
                "Banco_Origem",
                "Categoria_Origem",
                "Minimo_Parcelas_Pagas",
                "Status",
                "Regra_Descricao",
                "Observacao",
            ],
            "Descrição": [
                "Banco onde a proposta será digitada.",
                "Banco de onde o contrato está vindo.",
                "Categoria para regras genéricas.",
                "Quantidade mínima de parcelas pagas.",
                "SIM, NAO ou CONDICIONAL.",
                "Descrição completa da regra.",
                "Observações adicionais.",
            ],
        })
        ajuda.to_excel(writer, index=False, sheet_name="Como editar")


def abrir_arquivo(caminho: Path):
    if not caminho.exists():
        messagebox.showerror("Arquivo não encontrado", f"O arquivo não foi encontrado:\n{caminho}")
        return

    try:
        if os.name == "nt":
            os.startfile(caminho)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(caminho)], check=False)
        else:
            subprocess.run(["xdg-open", str(caminho)], check=False)
    except Exception as erro:
        messagebox.showerror("Erro", f"Não foi possível abrir o arquivo.\n\n{erro}")


class ConsultaPortabilidadeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.title(APP_TITLE)
        self.geometry("1120x720")
        self.minsize(980, 640)

        self.excel_path = resource_path(EXCEL_FILE)
        self.df = pd.DataFrame()

        self._criar_layout()
        self.carregar_regras(inicial=True)

    def _criar_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="Consulta de Regras de Portabilidade",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        titulo.grid(row=0, column=0, padx=20, pady=(18, 8), sticky="w")

        subtitulo = ctk.CTkLabel(
            self,
            text="Digite o banco de origem e a quantidade de parcelas pagas para ver onde pode digitar a proposta.",
            text_color="gray",
        )
        subtitulo.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        painel = ctk.CTkFrame(self)
        painel.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        painel.grid_columnconfigure(0, weight=0)
        painel.grid_columnconfigure(1, weight=1)
        painel.grid_rowconfigure(0, weight=1)

        filtros = ctk.CTkFrame(painel, width=310)
        filtros.grid(row=0, column=0, padx=14, pady=14, sticky="nsw")
        filtros.grid_propagate(False)

        ctk.CTkLabel(filtros, text="Filtros", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=16, pady=(18, 12))

        ctk.CTkLabel(filtros, text="Banco de origem").pack(anchor="w", padx=16, pady=(8, 4))
        self.banco_origem_var = ctk.StringVar()
        self.bancos_origem_lista = []

        self.banco_origem = ctk.CTkEntry(
            filtros,
            textvariable=self.banco_origem_var,
            placeholder_text="Digite para pesquisar. Ex.: Agibank",
            width=270,
        )
        self.banco_origem.pack(anchor="w", padx=16, pady=(0, 6))
        self.banco_origem.bind("<KeyRelease>", self.atualizar_sugestoes_bancos)
        self.banco_origem.bind("<FocusIn>", self.atualizar_sugestoes_bancos)

        self.sugestoes_frame = ctk.CTkScrollableFrame(filtros, width=270, height=110)
        self.sugestoes_frame.pack(anchor="w", padx=16, pady=(0, 10))
        self.sugestoes_frame.pack_forget()

        ctk.CTkLabel(filtros, text="Parcelas pagas").pack(anchor="w", padx=16, pady=(8, 4))
        self.parcelas_entry = ctk.CTkEntry(filtros, placeholder_text="Ex.: 12", width=270)
        self.parcelas_entry.pack(anchor="w", padx=16, pady=(0, 10))

        ctk.CTkLabel(filtros, text="Tipo da origem").pack(anchor="w", padx=16, pady=(8, 4))
        self.categoria_var = ctk.StringVar(value="BANCO_ORIGEM_CORBAN")
        self.categoria = ctk.CTkComboBox(filtros, variable=self.categoria_var, values=CATEGORIAS, width=270)
        self.categoria.pack(anchor="w", padx=16, pady=(0, 10))

        self.mostrar_recusados_var = ctk.BooleanVar(value=False)
        self.mostrar_recusados = ctk.CTkCheckBox(
            filtros,
            text="Mostrar recusados/insuficientes",
            variable=self.mostrar_recusados_var,
        )
        self.mostrar_recusados.pack(anchor="w", padx=16, pady=(10, 10))

        consultar_btn = ctk.CTkButton(filtros, text="Consultar Bancos Disponíveis", command=self.consultar)
        consultar_btn.pack(anchor="w", padx=16, pady=(12, 8), fill="x")

        limpar_btn = ctk.CTkButton(filtros, text="Limpar", fg_color="gray", hover_color="#555555", command=self.limpar)
        limpar_btn.pack(anchor="w", padx=16, pady=(0, 8), fill="x")

        abrir_btn = ctk.CTkButton(filtros, text="Abrir Excel de Regras", command=lambda: abrir_arquivo(self.excel_path))
        abrir_btn.pack(anchor="w", padx=16, pady=(18, 8), fill="x")

        recarregar_btn = ctk.CTkButton(filtros, text="Recarregar Regras", command=self.carregar_regras)
        recarregar_btn.pack(anchor="w", padx=16, pady=(0, 8), fill="x")

        self.status_label = ctk.CTkLabel(filtros, text="", text_color="gray", wraplength=260, justify="left")
        self.status_label.pack(anchor="w", padx=16, pady=(20, 8))

        resultado_frame = ctk.CTkFrame(painel)
        resultado_frame.grid(row=0, column=1, padx=(0, 14), pady=14, sticky="nsew")
        resultado_frame.grid_columnconfigure(0, weight=1)
        resultado_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            resultado_frame,
            text="Resultado da consulta",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, padx=14, pady=(14, 10), sticky="w")

        columns = ("Banco_Destino", "Status", "Parcelas_Minimas", "Regra", "Observacao")
        self.tree = ttk.Treeview(resultado_frame, columns=columns, show="headings", height=18)
        self.tree.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="nsew")

        self.tree.heading("Banco_Destino", text="Banco destino")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Parcelas_Minimas", text="Mínimo")
        self.tree.heading("Regra", text="Regra")
        self.tree.heading("Observacao", text="Observação")

        self.tree.column("Banco_Destino", width=190, anchor="w")
        self.tree.column("Status", width=110, anchor="center")
        self.tree.column("Parcelas_Minimas", width=80, anchor="center")
        self.tree.column("Regra", width=360, anchor="w")
        self.tree.column("Observacao", width=260, anchor="w")

        scrollbar = ttk.Scrollbar(resultado_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 14))

    def atualizar_sugestoes_bancos(self, event=None):
        termo = normalizar_texto(self.banco_origem_var.get())

        for widget in self.sugestoes_frame.winfo_children():
            widget.destroy()

        if not termo:
            self.sugestoes_frame.pack_forget()
            return

        resultados = []
        for banco in self.bancos_origem_lista:
            banco_norm = normalizar_texto(banco)
            if termo in banco_norm:
                resultados.append(banco)

        resultados = resultados[:8]

        if not resultados:
            self.sugestoes_frame.pack_forget()
            return

        self.sugestoes_frame.pack(anchor="w", padx=16, pady=(0, 10))

        for banco in resultados:
            botao = ctk.CTkButton(
                self.sugestoes_frame,
                text=banco,
                height=28,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray85", "gray25"),
                anchor="w",
                command=lambda valor=banco: self.selecionar_banco_sugerido(valor),
            )
            botao.pack(fill="x", padx=4, pady=2)

    def selecionar_banco_sugerido(self, banco):
        self.banco_origem_var.set(banco)
        self.sugestoes_frame.pack_forget()

    def carregar_regras(self, inicial=False):
        try:
            if not self.excel_path.exists():
                criar_excel_modelo(self.excel_path)
                if not inicial:
                    messagebox.showinfo("Excel criado", f"Arquivo modelo criado em:\n{self.excel_path}")

            try:
                self.df = pd.read_excel(self.excel_path, sheet_name=SHEET_NAME)
            except ValueError:
                # Se a aba Regras não existir, tenta ler a primeira aba.
                self.df = pd.read_excel(self.excel_path)

            # Limpa e padroniza nomes de colunas vindos do Excel.
            self.df.columns = [
                str(col).strip().replace(" ", "_").replace("-", "_")
                for col in self.df.columns
            ]

            # Aceita variações comuns de nomes de colunas.
            column_aliases = {
                "BancoDestino": "Banco_Destino",
                "Banco_Destino_": "Banco_Destino",
                "Destino": "Banco_Destino",
                "BancoOrigem": "Banco_Origem",
                "Banco_Origem_": "Banco_Origem",
                "Origem": "Banco_Origem",
                "Categoria": "Categoria_Origem",
                "CategoriaOrigem": "Categoria_Origem",
                "Tipo_Origem": "Categoria_Origem",
                "Tipo": "Categoria_Origem",
                "MinimoParcelasPagas": "Minimo_Parcelas_Pagas",
                "Minimo_Parcelas": "Minimo_Parcelas_Pagas",
                "Parcelas_Minimas": "Minimo_Parcelas_Pagas",
                "Parcelas": "Minimo_Parcelas_Pagas",
                "Regra": "Regra_Descricao",
                "Descricao": "Regra_Descricao",
                "Regra_Descrição": "Regra_Descricao",
                "Observação": "Observacao",
                "Obs": "Observacao",
            }

            self.df = self.df.rename(columns=column_aliases)

            # Se o Excel estiver muito quebrado, mostra um erro mais claro.
            faltando = [col for col in REQUIRED_COLUMNS if col not in self.df.columns]
            if faltando:
                colunas_encontradas = ", ".join(map(str, self.df.columns.tolist()))
                raise ValueError(
                    "O Excel foi encontrado, mas a aba de regras não está no formato esperado.\n\n"
                    f"Colunas ausentes: {', '.join(faltando)}\n\n"
                    f"Colunas encontradas: {colunas_encontradas}\n\n"
                    "Solução rápida:\n"
                    "1. Feche o programa.\n"
                    "2. Apague ou renomeie o arquivo regras_portabilidade.xlsx da pasta do programa.\n"
                    "3. Abra o programa novamente para ele criar um Excel modelo correto.\n\n"
                    "Ou use o arquivo regras_portabilidade.xlsx que veio no ZIP atualizado."
                )

            # Garante colunas extras opcionais para evitar erro.
            for coluna in ["Fonte_Pagina", "Fonte_Arquivo"]:
                if coluna not in self.df.columns:
                    self.df[coluna] = ""

            self.df["Banco_Origem_Norm"] = self.df["Banco_Origem"].apply(normalizar_texto)
            self.df["Banco_Destino_Norm"] = self.df["Banco_Destino"].apply(normalizar_texto)
            self.df["Categoria_Origem"] = self.df["Categoria_Origem"].fillna("").astype(str).str.upper().str.strip()
            self.df["Status"] = self.df["Status"].fillna("").astype(str).str.upper().str.strip()

            bancos_origem = sorted(set(
                str(b).strip()
                for b in self.df["Banco_Origem"].dropna().tolist()
                if str(b).strip()
            ))
            self.bancos_origem_lista = bancos_origem

            destinos = self.df["Banco_Destino"].nunique()
            regras = len(self.df)
            self.status_label.configure(
                text=f"Regras carregadas: {regras}\nBancos destino: {destinos}\nArquivo: {self.excel_path.name}"
            )

        except Exception as erro:
            messagebox.showerror("Erro ao carregar regras", str(erro))
            self.status_label.configure(text="Erro ao carregar regras.")

    def limpar(self):
        self.banco_origem_var.set("")
        self.parcelas_entry.delete(0, "end")
        self.categoria_var.set("BANCO_ORIGEM_CORBAN")
        self.mostrar_recusados_var.set(False)
        self.sugestoes_frame.pack_forget()
        self.limpar_tabela()

    def limpar_tabela(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _parcelas_digitadas(self):
        texto = self.parcelas_entry.get().strip()
        if not texto:
            return 0

        try:
            return int(texto)
        except ValueError:
            raise ValueError("Informe a quantidade de parcelas pagas usando apenas números.")

    def _regra_aplicavel_para_destino(self, grupo, banco_origem_norm, categoria):
        """
        Prioridade:
        1. Regra específica do banco de origem digitado.
        2. Tipo da origem selecionado:
           - BANCO_DE_REDE
           - BANCO_ORIGEM_CORBAN
        3. Regras genéricas equivalentes, quando existirem.
        """
        regras_especificas = grupo[grupo["Banco_Origem_Norm"] == banco_origem_norm]
        if not regras_especificas.empty:
            return regras_especificas

        equivalencias = {
            "BANCO_DE_REDE": [
                "BANCO_DE_REDE",
                "BANCO_ORIGEM_AGENCIA",
            ],
            "BANCO_ORIGEM_CORBAN": [
                "BANCO_ORIGEM_CORBAN",
                "DEMAIS_BANCOS_CIP",
                "ORIGEM_CORBAN_AGENCIA",
                "DEMAIS_BANCOS",
            ],
        }

        categorias_busca = equivalencias.get(categoria, [categoria])

        regras_categoria = grupo[grupo["Categoria_Origem"].isin(categorias_busca)]
        if not regras_categoria.empty:
            return regras_categoria

        return pd.DataFrame(columns=grupo.columns)

    def consultar(self):
        self.limpar_tabela()

        if self.df.empty:
            messagebox.showwarning("Atenção", "Nenhuma regra carregada.")
            return

        banco_origem = self.banco_origem_var.get().strip()
        if not banco_origem:
            messagebox.showwarning("Atenção", "Informe o banco de origem.")
            return

        try:
            parcelas = self._parcelas_digitadas()
        except ValueError as erro:
            messagebox.showwarning("Atenção", str(erro))
            return

        banco_origem_norm = normalizar_texto(banco_origem)
        categoria = self.categoria_var.get().strip().upper()
        mostrar_recusados = self.mostrar_recusados_var.get()

        resultados = []

        for banco_destino, grupo in self.df.groupby("Banco_Destino", sort=True):
            # Segurança: nunca mostra o mesmo banco como destino.
            # Ex.: C6, C6 BANK e BANCO C6 são tratados como o mesmo banco.
            if normalizar_texto(banco_destino) == banco_origem_norm:
                continue

            regras = self._regra_aplicavel_para_destino(grupo, banco_origem_norm, categoria)

            if regras.empty:
                continue

            # Se existir mais de uma regra aplicável no mesmo destino, mostra todas.
            for _, regra in regras.iterrows():
                status = str(regra.get("Status", "")).upper().strip()
                minimo = regra.get("Minimo_Parcelas_Pagas", "")
                descricao = str(regra.get("Regra_Descricao", "") or "")
                observacao = str(regra.get("Observacao", "") or "")

                minimo_num = None
                if pd.notna(minimo) and str(minimo).strip() != "":
                    try:
                        minimo_num = int(float(minimo))
                    except ValueError:
                        minimo_num = None

                if status == "NAO":
                    if mostrar_recusados:
                        resultados.append((banco_destino, "NÃO PORTA", minimo_num, descricao, observacao))
                    continue

                if status == "CONDICIONAL":
                    resultados.append((banco_destino, "CONDICIONAL", minimo_num, descricao, observacao))
                    continue

                if status == "SIM":
                    if minimo_num is None or parcelas >= minimo_num:
                        resultados.append((banco_destino, "SIM", minimo_num, descricao, observacao))
                    elif mostrar_recusados:
                        resultados.append((banco_destino, "INSUFICIENTE", minimo_num, descricao, observacao))

        if not resultados:
            self.tree.insert("", "end", values=(
                "Nenhum banco encontrado",
                "-",
                "-",
                "Não há regra compatível para os dados informados.",
                "Tente alterar a categoria ou marque 'mostrar recusados'.",
            ))
            return

        ordem_status = {"SIM": 0, "CONDICIONAL": 1, "INSUFICIENTE": 2, "NÃO PORTA": 3}
        resultados.sort(key=lambda item: (ordem_status.get(item[1], 99), item[0]))

        for banco_destino, status, minimo, descricao, observacao in resultados:
            minimo_texto = "-" if minimo is None else str(minimo)
            obs_texto = observacao if observacao.strip() else "-"
            self.tree.insert("", "end", values=(banco_destino, status, minimo_texto, descricao, obs_texto))


if __name__ == "__main__":
    app = ConsultaPortabilidadeApp()
    app.mainloop()
