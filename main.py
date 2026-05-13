import os
import io
import PIL.Image
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
import google.generativeai as genai

app = FastAPI()

# --- IA CONFIG ---
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
        <meta charset="UTF-8">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .gradient-bg { background: linear-gradient(135deg, #1e1b4b 0%, #d946ef 100%); }
        </style>
    </head>
    <body class="bg-slate-50">
        <nav class="gradient-bg p-6 text-white flex justify-between items-center shadow-lg">
            <h1 class="text-2xl font-black">Check<span class="text-pink-300">App</span></h1>
            <div class="space-x-4">
                <button onclick="show('paciente')" class="font-bold">Paciente</button>
                <button onclick="show('lab')" class="font-bold">Laboratório</button>
            </div>
        </nav>

        <main class="max-w-4xl mx-auto p-6 mt-6">
            <div id="paciente" class="bg-white p-8 rounded-3xl shadow-lg border">
                <h2 class="text-xl font-bold mb-6">Busca de Exames</h2>
                <div class="grid md:grid-cols-2 gap-4 mb-6">
                    <input id="cep" type="text" placeholder="CEP" class="p-4 border rounded-xl">
                    <select id="exame" class="p-4 border rounded-xl">
                        <option>Hemograma Completo</option><option>Vitamina D</option>
                        <option>Glicemia</option><option>USG Abdomen</option>
                        <option>Ressonância Magnética</option><option>Tomografia</option>
                    </select>
                </div>
                <input type="file" id="upload" class="hidden" onchange="iaScan()">
                <label for="upload" class="block bg-indigo-600 text-white p-4 rounded-xl text-center font-bold cursor-pointer">
                    UPLOAD RECEITA MÉDICA
                </label>
                <div id="status" class="mt-4 text-center font-bold text-indigo-600 hidden">Lendo com Gemini...</div>
                <div id="res" class="mt-6 p-4 bg-emerald-50 rounded-xl hidden text-emerald-800 font-bold"></div>
            </div>

            <div id="lab" class="hidden bg-slate-900 text-white p-8 rounded-3xl shadow-lg">
                <h2 class="text-xl font-bold mb-6">Cadastro de Laboratório</h2>
                <div class="space-y-4">
                    <input id="lab-nome" type="text" placeholder="Nome do Laboratório" class="w-full p-4 rounded-lg bg-slate-800">
                    <input id="lab-cep" type="text" placeholder="CEP do Lab" class="w-full p-4 rounded-lg bg-slate-800">
                    <select id="lab-esp" class="w-full p-4 rounded-lg bg-slate-800">
                        <option>Exames de Imagem</option><option>Análises Clínicas</option>
                    </select>
                    <div class="flex gap-4">
                        <input id="lab-desc" type="number" placeholder="Desconto %" class="w-1/2 p-4 rounded-lg bg-slate-800">
                        <input id="lab-hora" type="text" placeholder="Horário Ocioso" class="w-1/2 p-4 rounded-lg bg-slate-800">
                    </div>
                    <button onclick="saveLab()" class="w-full bg-pink-600 p-4 rounded-lg font-bold">SALVAR REGRAS</button>
                </div>
            </div>
        </main>

        <script>
            function show(id) {
                document.getElementById('paciente').classList.toggle('hidden', id !== 'paciente');
                document.getElementById('lab').classList.toggle('hidden', id !== 'lab');
            }
            async function iaScan() {
                const file = document.getElementById('upload').files[0];
                document.getElementById('status').classList.remove('hidden');
                const fd = new FormData(); fd.append('file', file);
                const r = await fetch('/ia-scan', {method:'POST', body: fd});
                const d = await r.json();
                document.getElementById('status').classList.add('hidden');
                document.getElementById('res').classList.remove('hidden');
                document.getElementById('res').innerText = "Exame Identificado: " + d.exame;
            }
            function saveLab() { alert("Regras de Ociosidade salvas na base CheckApp!"); }
        </script>
    </body>
    </html>
    """

@app.post("/ia-scan")
async def scan(file: UploadFile = File(...)):
    if not model: return {"exame": "ERRO: CHAVE API"}
    try:
        img = PIL.Image.open(io.BytesIO(await file.read()))
        res = model.generate_content(["Identifique o exame principal. Responda apenas o nome.", img])
        return {"exame": res.text.strip()}
    except: return {"exame": "IMAGEM ILEGÍVEL"}
