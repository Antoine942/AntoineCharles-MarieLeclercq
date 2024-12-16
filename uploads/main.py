import os
from flask import Flask, render_template, request
import openai
from werkzeug.utils import secure_filename
from langdetect import detect

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Fonction d'analyse des fichiers
def analyze_file_content(file_content):
    try:
        # Détection du type de contenu (code ou texte)
        if file_content.strip().startswith(("def ", "class ", "import ")):
            prompt = f"Analyze the following code and provide structured feedback:\n\n{file_content}"
        else:
            prompt = f"Analyze the following text and provide structured feedback:\n\n{file_content}"

        # Appel à OpenAI (modèle gpt-3.5-turbo)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.5,
        )
        analysis = response["choices"][0]["message"]["content"]
        return analysis
    except Exception as e:
        return f"Erreur lors de l'analyse : {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    feedback = None
    if request.method == "POST":
        if "file" not in request.files:
            feedback = "Aucun fichier sélectionné."
        else:
            file = request.files["file"]
            if file.filename == "":
                feedback = "Aucun fichier sélectionné."
            elif file:
                try:
                    # Sauvegarder le fichier
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    file.save(filepath)

                    # Lire le contenu du fichier
                    with open(filepath, "r", encoding="utf-8") as f:
                        file_content = f.read()

                    # Analyser le contenu
                    feedback = analyze_file_content(file_content)

                except Exception as e:
                    feedback = f"Erreur lors du traitement du fichier : {e}"

    return render_template("index.html", feedback=feedback)

if __name__ == "__main__":
    app.run(debug=True)
