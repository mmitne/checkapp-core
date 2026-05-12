from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List, Optional
import datetime

app = FastAPI(title="CheckApp Global Engine")

# --- DATABASE DE PREÇOS REAIS (Baseado em análise de mercado) ---
# Preços dinâmicos de acordo com região da cidade 
BASES_REGIONAIS = {
    "SP": {"Hemograma": 27.20, "Vitamina D": 96.00, "Glicemia": 15.00, "USG Abdome": 260.00},
    "RJ": {"Hemograma": 30.00, "Vitamina D": 105.00, "Glicemia": 18.00, "USG Abdome": 280.00},
    "PR": {"Hemograma": 35.00, "Vitamina D": 110.00, "Glicemia": 20.00, "USG Abdome": 285.00}
}

# --- LÓGICA DE LEILÃO E YIELD MANAGEMENT ---
# Possibilidade de praticar preços distintos de acordo com a demanda [cite: 71]
# Preços dinâmicos de acordo com horário do dia (ocupação dos laboratórios) [cite: 73]
def calcular_yield_price(preco_base, hora_atual):
    # Se for à tarde (após as 13h), exames que não exigem jejum ficam mais baratos [cite: 73]
    if 13 <= hora_atual <= 17:
        return preco_base * 0.85 # 15% de desconto automático para ocupar agenda 
    return preco_base

# --- SERVIÇOS DA PLATAFORMA ---

@app.post("/upload-receita")
async def ocr_receita(file: UploadFile = File(...)):
    """
    Simula a leitura automática da receita médica via IA.
    O paciente não tem plano e utiliza a plataforma para buscar o custo factível[cite: 26, 28].
    """
    # Placeholder para a integração real com Gemini Vision
    return {
        "status": "Sucesso",
        "exame_detectado": "Hemograma Completo",
        "mensagem": "Buscando laboratórios custo/efetivos para você "
    }

@app.get("/leilao/{cep}/{exame}")
def iniciar_leilao(cep: str, exame: str):
    """
    Inicia o leilão dinâmico baseado na localização e disponibilidade[cite: 17, 29, 76].
    """
    # Identifica a região pelo primeiro dígito do CEP
    regiao = "SP" if cep.startswith(("0", "1")) else "RJ" if cep.startswith("2") else "PR"
    
    preco_mercado = BASES_REGIONAIS.get(regiao, {}).get(exame, 50.00)
    hora_agora = datetime.datetime.now().hour
    
    # Aplica a inteligência de ocupação 
    preco_sugerido = calcular_yield_price(preco_mercado, hora_agora)
    
    return {
        "modelo": "B2C - Venda Direta [cite: 8]",
        "exame": exame,
        "regiao": regiao,
        "preco_base_regiao": preco_mercado,
        "lance_vencedor_sugerido": round(preco_sugerido, 2),
        "status": "Leilão ativo para laboratórios no seu CEP [cite: 29]"
    }

@app.post("/pagamento/formato-a")
def processar_pagamento():
    """
    Modelo de Pagamento: Cliente insere dados do cartão[cite: 91, 92].
    """
    return {"status": "Pagamento aprovado no app [cite: 93]", "metodo": "Cartão de Crédito"}
