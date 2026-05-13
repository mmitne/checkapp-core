import os
import io
import PIL.Image
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import google.generativeai as genai

app = FastAPI()

# Configuração da IA
api_key = os.environ.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-100 p-6">
        <div class="max-w-2xl mx-auto bg-white p-8 rounded-2xl shadow-lg">
            <h1 class="text-2xl font-bold mb-4">CheckApp | Teste de Upload</h1>
            <input type="file" id="upload" class="mb-4">
            <button onclick="enviar()" class="bg-indigo-600 text-white px-6 py-2 rounded-lg">ENVIAR</button>
            <p id="msg" class="mt-4 font-bold text-indigo-700"></p>
        </div>
        <script>
            async function enviar() {
                const file = document.getElementById('upload').files[0];
                if(!file) { alert("Selecione um arquivo!"); return; }
                document.getElementById('msg').innerText = "Enviando...";
                
                const fd = new FormData(); fd.append('file', file);
                try {
                    const r = await fetch('/ia-scan', {method:'POST', body: fd});
                    const d = await r.json();
                    document.getElementById('msg').innerText = "Resultado: " + d.exame;
                } catch(e) {
                    document.getElementById('msg').innerText = "Erro ao enviar: " + e;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/ia-scan")
async def scan(file: UploadFile = File(...)):
    if not model: return {"exame": "ERRO: CHAVE API"}
    try:
        # AQUI O LOG QUE AJUDA A DEPURAR
        print(f"Recebendo arquivo: {file.filename}") 
        contents = await file.read()
        img = PIL.Image.open(io.BytesIO(contents))
        res = model.generate_content(["Identifique o exame principal. Responda apenas o nome.", img])
        return {"exame": res.text.strip()}
    except Exception as e:
        print(f"Erro no processamento: {str(e)}")
        return {"exame": f"Erro técnico: {str(e)}"}
