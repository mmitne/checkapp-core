import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import google.generativeai as genai
import PIL.Image
import io

app = FastAPI()

# COLE SUA API KEY AQUI (Para teste rápido) ou use Variáveis de Ambiente
GOOGLE_API_KEY = "AIzaSyBivenejBRrYM8iSkxqM5BVZCAFnnQ7b-E"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/", response_class=HTMLResponse)
async def home():
    # Mantendo o visual incrível que criamos, mas adicionando a lógica de upload real
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CheckApp | IA Real-Life</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { font-family: 'Inter', sans-serif; background-color: #f1f5f9; }
            .gradient-bg { background: linear-gradient(135deg, #1e1b4b 0%, #4338ca 100%); }
        </style>
    </head>
    <body>
        <nav class="bg-white border-b p-4 shadow-sm">
            <div class="max-w-4xl mx-auto flex justify-between items-center">
                <span class="font-bold text-xl text-indigo-900">CheckApp <span class="text-xs font-light text-slate-400">AI POWERED</span></span>
            </div>
        </nav>

        <main class="max-w-2xl mx-auto p-6 mt-10">
            <div class="bg-white rounded-3xl shadow-2xl p-8 border border-slate-100">
                <h2 class="text-2xl font-bold text-slate-800 mb-6">Demonstração de OCR em Tempo Real</h2>
                
                <div class="space-y-6">
                    <div class="border-2 border-dashed border-indigo-200 rounded-2xl p-10 text-center bg-indigo-50/30">
                        <input type="file" id="foto-receita" class="hidden" accept="image/*" onchange="processarIA()">
                        <label for="foto-receita" class="cursor-pointer">
                            <span class="text-5xl block mb-4">📸</span>
                            <span class="font-bold text-indigo-600">Tire uma foto da receita</span>
                            <p class="text-xs text-slate-400 mt-2">Nossa IA identificará os exames e iniciará o leilão [cite: 50]</p>
                        </label>
                    </div>

                    <div id="loading" class="hidden text-center py-6">
                        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mx-auto"></div>
                        <p class="text-indigo-600 font-medium mt-4">Gemini analisando caligrafia médica...</p>
                    </div>

                    <div id="resultado-ia" class="hidden p-6 bg-emerald-50 rounded-2xl border border-emerald-100">
                        <h3 class="font-bold text-emerald-800 mb-2">Exame Identificado:</h3>
                        <div id="exame-nome" class="text-2xl font-black text-emerald-600 mb-4 uppercase">---</div>
                        <div class="text-sm text-emerald-700 bg-white/50 p-3 rounded-lg">
                            <strong>Próximo passo:</strong> O leilão reverso foi disparado para laboratórios em seu CEP.
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <script>
            async def processarIA() {
                const fileInput = document.getElementById('foto-receita');
                const loading = document.getElementById('loading');
                const res = document.getElementById('resultado-ia');
                const exameTxt = document.getElementById('exame-nome');

                if (!fileInput.files[0]) return;

                loading.classList.remove('hidden');
                res.classList.add('hidden');

                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                try {
                    const response = await fetch('/ia-scan', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    
                    loading.classList.add('hidden');
                    res.classList.remove('hidden');
                    exameTxt.innerText = data.exame;
                } catch (error) {
                    alert("Erro na conexão com a IA. Verifique sua API Key.");
                    loading.classList.add('hidden');
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/ia-scan")
async def scan_receita(file: UploadFile = File(...)):
    # Lógica Real de Conexão com Gemini [cite: 51]
    contents = await file.read()
    img = PIL.Image.open(io.BytesIO(contents))
    
    prompt = "Identifique apenas o nome do exame laboratorial principal solicitado nesta receita médica. Responda apenas com o nome do exame em MAIÚSCULAS."
    
    response = model.generate_content([prompt, img])
    return {"exame": response.text.strip()}
