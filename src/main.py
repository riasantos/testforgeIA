import os
import json
import re
import docx
import requests
import logging
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Border, Side, Alignment, Font
from openpyxl.utils import get_column_letter

# Configuração de Logging para ver o que acontece no terminal
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# ======================
# CONFIGURAÇÃO GERAL
# ======================
GITHUB_TOKEN = os.getenv("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")
COPILOT_API_URL = "https://api.githubcopilot.com/chat/completions"

DOCUMENTS_DIR = "Documentações"
EXCEL_OUTPUT = "cenarios_de_testes.xlsx"

MANUAL_MIN_PER_TEST = 15
AI_MIN_PER_TEST = 2

# ======================
# MOTOR DE IA (COPILOT)
# ======================
def call_copilot(prompt: str) -> str:
    if not GITHUB_TOKEN:
        raise RuntimeError("ERRO: GITHUB_TOKEN não configurado nas variáveis de ambiente.")

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "Editor-Version": "vscode/1.80.0",
    }

    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "Você é um Engenheiro de QA Sênior focado em precisão técnica e JSON estruturado."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
    }

    try:
        response = requests.post(COPILOT_API_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Erro na API Copilot: {e}")
        raise

# =============================================
# ENGENHARIA DE PROMPT
# =============================================
QA_PROMPT_TEMPLATE = """
Aja como um Lead QA Engineer. Analise os requisitos abaixo e gere um Plano de Testes em formato JSON.

### REGRAS DE OUTPUT:
1. Retorne EXCLUSIVAMENTE o objeto JSON.
2. Não utilize blocos de código markdown (```json ... ```).
3. Use a técnica de 'Análise de Valor Limite' e 'Transição de Estados'.
4. IDs: TC-FUNC-NNN, TC-NEG-NNN, TC-SEC-NNN.

### ESTRUTURA DO JSON:
{{
  "analise_requisitos": {{ "riscos": [], "entidades": [] }},
  "cenarios_funcionais": [
    {{
      "id": "TC-FUNC-001",
      "titulo": "Título Curto",
      "prioridade": "Alta",
      "descricao": "O que o teste faz",
      "passos": ["1...", "2..."],
      "resultado_esperado": "Resultado verificável"
    }}
  ],
  "cenarios_negativos": [],
  "cenarios_borda": [],
  "metricas_qualidade": {{ "total_casos": 0 }}
}}

### REQUISITOS PARA ANÁLISE:
{requisitos_texto}
"""

# ======================
# PROCESSAMENTO DE ARQUIVOS
# ======================
def extrair_requisitos_docx(caminho):
    logging.info(f"📄 Extraindo texto de: {caminho}")
    doc = docx.Document(caminho)
    conteudo = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    return "\n".join(conteudo)

def limpar_e_validar_json(texto):
    texto_limpo = re.sub(r'```json\s*|```', '', texto).strip()
    try:
        return json.loads(texto_limpo)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', texto_limpo, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise

def salvar_excel_por_documentos(doc_json_list):
    logging.info("📝 Gerando arquivo Excel final...")
    wb = Workbook()
    wb.remove(wb.active) # Remove aba padrão

    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                         top=Side(style='thin'), bottom=Side(style='thin'))

    for doc_name, data in doc_json_list:
        ws = wb.create_sheet(title=doc_name[:30])
        headers = ["ID", "Título", "Prioridade", "Descrição", "Passos", "Resultado Esperado"]
        
        # Estilização do cabeçalho
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")

        # Unificar cenários
        todos_cenarios = data.get("cenarios_funcionais", []) + \
                         data.get("cenarios_negativos", []) + \
                         data.get("cenarios_borda", [])

        for row_num, cenario in enumerate(todos_cenarios, 2):
            ws.cell(row=row_num, column=1, value=cenario.get("id"))
            ws.cell(row=row_num, column=2, value=cenario.get("titulo"))
            ws.cell(row=row_num, column=3, value=cenario.get("prioridade"))
            ws.cell(row=row_num, column=4, value=cenario.get("descricao"))
            ws.cell(row=row_num, column=5, value="\n".join(cenario.get("passos", [])))
            ws.cell(row=row_num, column=6, value=cenario.get("resultado_esperado"))
            
            # Aplicar bordas e alinhamento
            for col in range(1, 7):
                ws.cell(row=row_num, column=col).border = thin_border
                ws.cell(row=row_num, column=col).alignment = Alignment(wrap_text=True, vertical="top")

        # Ajuste de largura das colunas
        ws.column_dimensions['D'].width = 40
        ws.column_dimensions['E'].width = 50
        ws.column_dimensions['F'].width = 40

    wb.save(EXCEL_OUTPUT)
    logging.info(f"✨ Sucesso! Planilha gerada: {EXCEL_OUTPUT}")

# ======================
# EXECUÇÃO PRINCIPAL
# ======================
def iniciar_testforge():
    # Garante que a pasta de documentações existe
    Path(DOCUMENTS_DIR).mkdir(exist_ok=True)
    
    docx_files = list(Path(DOCUMENTS_DIR).glob("*.docx"))
    
    if not docx_files:
        logging.warning(f"⚠️ Nenhum arquivo .docx encontrado na pasta '{DOCUMENTS_DIR}'.")
        return

    doc_json_list = []
    for docpath in docx_files:
        try:
            texto = extrair_requisitos_docx(docpath)
            prompt = QA_PROMPT_TEMPLATE.format(requisitos_texto=texto)
            
            resposta = call_copilot(prompt)
            dados_qa = limpar_e_validar_json(resposta)
            
            doc_json_list.append((docpath.stem, dados_qa))
        except Exception as e:
            logging.error(f"❌ Erro ao processar {docpath.name}: {e}")

    if doc_json_list:
        salvar_excel_por_documentos(doc_json_list)

if __name__ == "__main__":
    print("🚀 TestForge iniciado...")

    iniciar_testforge()
