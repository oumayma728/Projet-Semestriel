import requests

def ask_gemini(user_question, books_context):
    prompt = f"""Tu es un bibliothécaire virtuel intelligent. Tu gères une bibliothèque et tu réponds aux questions des utilisateurs en français.

Voici les livres disponibles dans la bibliothèque (données réelles) :
{books_context}

Question de l'utilisateur : {user_question}

Réponds de manière naturelle et précise en te basant uniquement sur les données de la bibliothèque ci-dessus.
Si le livre n'existe pas, dis-le clairement.
"""
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3.2:1b",
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"]