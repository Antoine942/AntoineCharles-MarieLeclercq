from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import openai
from PyPDF2 import PdfReader
from docx import Document

# Charger les variables d'environnement
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialiser l'application Flask
app = Flask(__name__)

# Liste des extensions de fichiers de code
CODE_EXTENSIONS = {".py", ".js", ".java", ".cpp", ".c", ".html", ".css", ".php", ".rb", ".go"}

# Fonction pour extraire le texte d'un fichier
def extract_text(file):
    filename = file.filename
    try:
        # Fichier texte simple
        if filename.endswith(".txt"):
            return file.read().decode('utf-8'), "text"
        # Fichier PDF
        elif filename.endswith(".pdf"):
            try:
                pdf_reader = PdfReader(file)
                text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
                return text, "text"
            except Exception as e:
                return None, f"Erreur lors de la lecture du PDF : {e}"
        # Fichier Word
        elif filename.endswith(".docx"):
            try:
                doc = Document(file)
                text = " ".join([para.text for para in doc.paragraphs])
                return text, "text"
            except Exception as e:
                return None, f"Erreur lors de la lecture du fichier Word : {e}"
        # Fichier de code
        elif any(filename.endswith(ext) for ext in CODE_EXTENSIONS):
            try:
                return file.read().decode('utf-8'), "code"
            except Exception as e:
                return None, f"Erreur lors de la lecture du fichier de code : {e}"
        else:
            return None, "Type de fichier non supporté."
    except Exception as e:
        return None, f"Erreur générale lors du traitement du fichier : {e}"

# Fonction pour analyser un texte ou un code avec OpenAI
def analyze_content(content, content_type):
    try:
        if content_type == "text":
            prompt = "Tu es un assistant qui fournit des retours détaillés et constructifs sur des projets étudiants écrits en texte."
        elif content_type == "code":
            prompt = "Tu es un assistant expert en programmation qui fournit des retours constructifs sur le code. Identifie les erreurs potentielles, les bonnes pratiques et suggère des améliorations."
        else:
            return "Type de contenu non supporté."

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}]
        )
        feedback = response.choices[0].message['content']
        return feedback
    except Exception as e:
        return f"Une erreur est survenue lors de l'analyse : {e}"

# Route principale pour afficher et traiter le formulaire
@app.route("/", methods=["GET", "POST"])
def index():
    feedback = None
    if request.method == "POST":
        # Vérifier si un fichier a été envoyé
        if 'file' in request.files:
            file = request.files['file']
            content, error_or_type = extract_text(file)

            if content:
                # Analyser le texte ou le code
                feedback = analyze_content(content, error_or_type)
            else:
                feedback = error_or_type  # Retourner le message d'erreur spécifique
        else:
            feedback = "Aucun fichier n'a été déposé."
    # Rendre la page HTML
    return render_template("index.html", feedback=feedback)

# Lancer l'application en local
if __name__ == "__main__":
    app.run(debug=True)
