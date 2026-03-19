#!/usr/bin/env python3
"""
generate_article.py
-------------------
Genera un artículo diario sobre mascotas usando la API de Anthropic
y lo inserta en el array `articles` del index.html del sitio.

Uso:
    python generate_article.py

Variables de entorno necesarias:
    ANTHROPIC_API_KEY   → tu clave de API de Anthropic

Ejecutado automáticamente todos los días por GitHub Actions.
"""

import os
import re
import json
import random
import datetime
import anthropic

# ─── CONFIGURACIÓN ──────────────────────────────────────────────
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
HTML_FILE = "index.html"          # ruta relativa al repo
MAX_ARTICLES = 60                  # máximo de artículos a mantener en el array
# ────────────────────────────────────────────────────────────────

CATEGORIES = [
    ("Perros",       "🐶"),
    ("Gatos",        "🐱"),
    ("Aves",         "🦜"),
    ("Reptiles",     "🦎"),
    ("Exóticas",     "🐇"),
    ("Salud",        "💊"),
    ("Alimentación", "🍖"),
]

TOPIC_POOL = {
    "Perros": [
        "razas ideales para departamento",
        "cómo entrenar un cachorro en casa",
        "señales de dolor en perros",
        "qué vacunas necesita un perro cada año",
        "cómo bañar a un perro correctamente",
        "juegos para estimular mentalmente a tu perro",
        "por qué los perros comen pasto",
        "cuánto ejercicio necesita cada raza",
        "qué significa el lenguaje corporal del perro",
        "cómo cortar las uñas a un perro en casa",
    ],
    "Gatos": [
        "por qué los gatos ronronean",
        "cómo limpiar los ojos de un gato",
        "razas de gatos hipoalergénicas",
        "gatos de interior vs exterior: pros y contras",
        "cómo enriquecer el ambiente de un gato de interior",
        "señales de estrés en gatos",
        "cuántas veces al día debe comer un gato adulto",
        "por qué mi gato me trae presas",
        "cómo presentar a un gato nuevo en casa",
        "enfermedades más comunes en gatos mayores",
    ],
    "Aves": [
        "cómo saber si un loro está sano",
        "qué frutas puede comer una cotorra",
        "canarios: cuidados básicos para principiantes",
        "cómo enseñar a hablar a un loro",
        "señales de enfermedad en aves de compañía",
        "tamaño de jaula adecuado según la especie",
        "cuándo es normal que un ave mude de plumas",
        "periquitos australianos: guía completa de cuidados",
    ],
    "Reptiles": [
        "qué come una iguana doméstica",
        "temperatura ideal para un terrario de serpientes",
        "tortuga de tierra: cuidados en el hogar",
        "gecko leopardo como mascota: guía para principiantes",
        "señales de enfermedad en reptiles",
        "dragons barbudos: alimentación y hábitat",
    ],
    "Exóticas": [
        "cómo cuidar un conejo enano",
        "hámster vs cobayo: cuál es mejor mascota",
        "erizo africano: ¿es buena mascota?",
        "hurón doméstico: todo lo que necesitás saber",
        "peces betta: cuidados en acuario",
        "chinchillas como mascotas: ventajas y desafíos",
    ],
    "Salud": [
        "calendario de vacunación para perros y gatos",
        "cómo detectar pulgas y garrapatas",
        "primeros auxilios para mascotas",
        "señales de alerta que requieren veterinario urgente",
        "desparasitación: cuándo y con qué frecuencia",
        "enfermedades zoonóticas: cuáles pueden contagiarse a humanos",
    ],
    "Alimentación": [
        "alimentos tóxicos para perros que quizás no conocés",
        "dieta BARF: pros y contras según la ciencia",
        "cómo leer la etiqueta de un alimento balanceado",
        "cuánta agua debe beber una mascota al día",
        "suplementos vitamínicos para mascotas: cuándo son necesarios",
        "alimentos caseros seguros para gatos",
    ],
}


def pick_topic(existing_titles: list[str]) -> tuple[str, str, str]:
    """Elige una categoría y tema evitando repetir títulos recientes."""
    random.shuffle(CATEGORIES)
    for cat_name, emoji in CATEGORIES:
        topics = TOPIC_POOL.get(cat_name, [])
        random.shuffle(topics)
        for topic in topics:
            if not any(topic.lower() in t.lower() for t in existing_titles[-30:]):
                return cat_name, emoji, topic
    # Fallback: elige cualquiera
    cat_name, emoji = random.choice(CATEGORIES)
    topic = random.choice(TOPIC_POOL[cat_name])
    return cat_name, emoji, topic


def generate_article(cat: str, topic: str) -> dict:
    """Llama a la API de Anthropic y devuelve los campos del artículo."""
    client = anthropic.Anthropic(api_key=API_KEY)

    prompt = f"""Eres un experto en mascotas y veterinaria. 
Escribí un artículo de blog en español sobre "{topic}" en la categoría "{cat}".

FORMATO DE RESPUESTA — devolvé ÚNICAMENTE un objeto JSON válido con esta estructura:
{{
  "title": "Título atractivo y con keyword (máx 70 caracteres)",
  "excerpt": "Resumen de 2 frases para el listado del blog (máx 160 caracteres)",
  "readTime": "N",
  "content": "HTML completo del artículo con etiquetas <h2>, <p> y <ul>/<li>. Mínimo 600 palabras. Sin <html>, <body> ni <style>."
}}

Requisitos del artículo:
- Lenguaje claro, accesible y cálido para dueños hispanohablantes
- Al menos 3 subtítulos H2
- Incluir datos concretos y consejos prácticos
- Terminar con un párrafo de conclusión o llamado a la acción
- No usar markdown, solo HTML dentro del campo "content"
"""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Limpiar posibles bloques de código markdown
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    data = json.loads(raw)
    return data


def load_existing_articles(html: str) -> list[dict]:
    """Extrae el array articles del HTML."""
    match = re.search(r"const articles = (\[.*?\]);", html, re.DOTALL)
    if not match:
        raise ValueError("No se encontró 'const articles = [...]' en el HTML")
    return json.loads(match.group(1))


def save_articles(html: str, articles: list[dict]) -> str:
    """Reemplaza el array articles en el HTML."""
    new_json = json.dumps(articles, ensure_ascii=False, indent=6)
    return re.sub(
        r"const articles = \[.*?\];",
        f"const articles = {new_json};",
        html,
        flags=re.DOTALL,
    )


def main():
    if not API_KEY:
        raise EnvironmentError("ANTHROPIC_API_KEY no está definida")

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    articles = load_existing_articles(html)
    existing_titles = [a["title"] for a in articles]

    # Elegir tema
    cat, emoji, topic = pick_topic(existing_titles)
    print(f"✏️  Generando artículo sobre '{topic}' [{cat}]...")

    # Generar con IA
    new_data = generate_article(cat, topic)

    # Construir objeto artículo
    today = datetime.date.today()
    months_es = ["enero","febrero","marzo","abril","mayo","junio",
                 "julio","agosto","septiembre","octubre","noviembre","diciembre"]
    date_str = f"{today.day} de {months_es[today.month-1]}, {today.year}"

    new_article = {
        "id": (articles[0]["id"] + 1) if articles else 1,
        "title":    new_data["title"],
        "excerpt":  new_data["excerpt"],
        "category": cat,
        "emoji":    emoji,
        "date":     date_str,
        "readTime": str(new_data.get("readTime", "5")),
        "featured": False,
        "content":  new_data["content"],
    }

    # Insertar al inicio, el primero pasa a ser el featured
    articles.insert(0, new_article)
    articles[0]["featured"] = True
    if len(articles) > 1:
        articles[1]["featured"] = False

    # Limitar cantidad de artículos
    if len(articles) > MAX_ARTICLES:
        articles = articles[:MAX_ARTICLES]

    # Guardar
    html_updated = save_articles(html, articles)
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_updated)

    print(f"✅  Artículo publicado: {new_article['title']}")


if __name__ == "__main__":
    main()
