#!/usr/bin/env python3
"""
generate_article.py
-------------------
Genera un artículo diario sobre mascotas usando la API de Anthropic,
busca una imagen en Unsplash y lo inserta en el index.html del sitio.

Variables de entorno necesarias:
    ANTHROPIC_API_KEY   → API key de Anthropic
    UNSPLASH_ACCESS_KEY → Access key de Unsplash (gratuita)
"""

import os
import re
import json
import random
import datetime
import urllib.request
import urllib.parse
import anthropic

# ─── CONFIGURACIÓN ──────────────────────────────────────────────
API_KEY         = os.environ.get("ANTHROPIC_API_KEY")
UNSPLASH_KEY    = os.environ.get("UNSPLASH_ACCESS_KEY")
HTML_FILE       = "index.html"
MAX_ARTICLES    = 60
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

UNSPLASH_KEYWORDS = {
    "Perros":        "dog pet",
    "Gatos":         "cat pet",
    "Aves":          "pet bird parrot",
    "Reptiles":      "reptile lizard pet",
    "Exóticas":      "exotic pet rabbit hamster",
    "Salud":         "veterinarian pet health",
    "Alimentación":  "pet food dog cat",
}

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
        "gatos de interior vs exterior pros y contras",
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
        "canarios cuidados básicos para principiantes",
        "cómo enseñar a hablar a un loro",
        "señales de enfermedad en aves de compañía",
        "tamaño de jaula adecuado según la especie",
        "periquitos australianos guía completa de cuidados",
    ],
    "Reptiles": [
        "qué come una iguana doméstica",
        "temperatura ideal para un terrario de serpientes",
        "tortuga de tierra cuidados en el hogar",
        "gecko leopardo como mascota guía para principiantes",
        "señales de enfermedad en reptiles",
        "dragons barbudos alimentación y hábitat",
    ],
    "Exóticas": [
        "cómo cuidar un conejo enano",
        "hámster vs cobayo cuál es mejor mascota",
        "erizo africano es buena mascota",
        "hurón doméstico todo lo que necesitás saber",
        "peces betta cuidados en acuario",
        "chinchillas como mascotas ventajas y desafíos",
    ],
    "Salud": [
        "calendario de vacunación para perros y gatos",
        "cómo detectar pulgas y garrapatas",
        "primeros auxilios para mascotas",
        "señales de alerta que requieren veterinario urgente",
        "desparasitación cuándo y con qué frecuencia",
        "enfermedades zoonóticas cuáles pueden contagiarse a humanos",
    ],
    "Alimentación": [
        "alimentos tóxicos para perros que quizás no conocés",
        "dieta BARF pros y contras según la ciencia",
        "cómo leer la etiqueta de un alimento balanceado",
        "cuánta agua debe beber una mascota al día",
        "suplementos vitamínicos para mascotas cuándo son necesarios",
        "alimentos caseros seguros para gatos",
    ],
}


def pick_topic(existing_titles):
    cats = list(CATEGORIES)
    random.shuffle(cats)
    for cat_name, emoji in cats:
        topics = list(TOPIC_POOL.get(cat_name, []))
        random.shuffle(topics)
        for topic in topics:
            if not any(topic.lower() in t.lower() for t in existing_titles[-30:]):
                return cat_name, emoji, topic
    cat_name, emoji = random.choice(CATEGORIES)
    topic = random.choice(TOPIC_POOL[cat_name])
    return cat_name, emoji, topic


def fetch_unsplash_image(cat, topic):
    """Busca una imagen en Unsplash. Devuelve dict con url/thumb/alt/author o None."""
    if not UNSPLASH_KEY:
        print("UNSPLASH_ACCESS_KEY no definida, saltando imagen.")
        return None

    base_kw  = UNSPLASH_KEYWORDS.get(cat, "pet animal")
    topic_kw = " ".join(topic.split()[:3])
    query    = f"{base_kw} {topic_kw}"

    params = urllib.parse.urlencode({
        "query":          query,
        "per_page":       10,
        "orientation":    "landscape",
        "content_filter": "high",
    })
    url = f"https://api.unsplash.com/search/photos?{params}"

    req = urllib.request.Request(url, headers={
        "Authorization":  f"Client-ID {UNSPLASH_KEY}",
        "Accept-Version": "v1",
    })

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        results = data.get("results", [])
        if not results:
            print(f"Unsplash no devolvió resultados para: {query}")
            return None
        photo = random.choice(results[:5])
        return {
            "url":        photo["urls"]["regular"],
            "thumb":      photo["urls"]["small"],
            "alt":        photo.get("alt_description") or query,
            "author":     photo["user"]["name"],
            "author_url": photo["user"]["links"]["html"],
        }
    except Exception as e:
        print(f"Error al buscar imagen en Unsplash: {e}")
        return None


def build_image_html(image):
    """HTML de la imagen con crédito a Unsplash (requerido por su licencia)."""
    if not image:
        return ""
    return (
        f'<figure style="margin:0 0 28px 0;">'
        f'<img src="{image["url"]}" alt="{image["alt"]}" '
        f'style="width:100%;border-radius:10px;max-height:420px;object-fit:cover;" loading="lazy"/>'
        f'<figcaption style="font-size:0.75rem;color:#888;margin-top:6px;">'
        f'Foto de <a href="{image["author_url"]}?utm_source=petaguia&utm_medium=referral" '
        f'target="_blank" rel="noopener">{image["author"]}</a> en '
        f'<a href="https://unsplash.com/?utm_source=petaguia&utm_medium=referral" '
        f'target="_blank" rel="noopener">Unsplash</a>'
        f'</figcaption></figure>'
    )


def generate_article(cat, topic):
    client = anthropic.Anthropic(api_key=API_KEY)

    prompt = (
        f'Eres un experto en mascotas. Escribí un artículo en español sobre "{topic}" '
        f'para la categoría "{cat}".\n\n'
        'RESPONDE ÚNICAMENTE con JSON puro. Sin texto antes ni después. Sin bloques de código. '
        'Sin comillas triples. Solo el objeto JSON.\n\n'
        'Estructura exacta (respeta las comillas dobles en todas las claves y valores):\n'
        '{"title":"Título atractivo máx 70 caracteres",'
        '"excerpt":"Resumen 2 frases máx 160 caracteres",'
        '"readTime":"5",'
        '"content":"HTML del artículo aquí con h2 p ul li. Mínimo 500 palabras. '
        'Sin html body style. Las comillas dentro del HTML deben ser \\u0022 o evitadas."}'
    )

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    print(f"RAW API response (primeros 200 chars): {raw[:200]}")

    raw = re.sub(r"^```json\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"^```\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"```\s*$", "", raw, flags=re.MULTILINE)
    raw = raw.strip()

    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No se encontró JSON en la respuesta: {raw[:300]}")
    raw = raw[start:end]

    data = json.loads(raw)
    return data


def _find_array_bounds(html):
    """Encuentra los límites del array articles usando conteo de corchetes."""
    match = re.search(r"const articles\s*=\s*\[", html)
    if not match:
        raise ValueError("No se encontró 'const articles = [' en el HTML")

    bracket_start = match.end() - 1
    depth = 0
    in_string = False
    escape = False

    for i in range(bracket_start, len(html)):
        ch = html[i]
        if escape:
            escape = False
            continue
        if ch == '\\' and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if not in_string:
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    return match.start(), bracket_start, i + 1

    raise ValueError("No se encontró el cierre del array articles")


def load_existing_articles(html):
    """Extrae el array articles del HTML de forma robusta."""
    _, bracket_start, bracket_end = _find_array_bounds(html)
    raw = html[bracket_start:bracket_end]
    raw = re.sub(r',\s*([\]}])', r'\1', raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR al parsear articles. Primeros 500 chars:\n{raw[:500]}")
        raise e


def save_articles(html, articles):
    """Reemplaza el array articles en el HTML."""
    decl_start, _, bracket_end = _find_array_bounds(html)
    semi_pos = html.index(';', bracket_end - 1) + 1
    new_json = json.dumps(articles, ensure_ascii=False, indent=6)
    return html[:decl_start] + "const articles = " + new_json + ";" + html[semi_pos:]


def main():
    if not API_KEY:
        raise EnvironmentError("ANTHROPIC_API_KEY no está definida")

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    articles = load_existing_articles(html)
    print(f"Artículos existentes: {len(articles)}")

    existing_titles = [a.get("title", "") for a in articles]
    cat, emoji, topic = pick_topic(existing_titles)
    print(f"Generando artículo sobre '{topic}' [{cat}]...")

    # Buscar imagen en Unsplash
    image = fetch_unsplash_image(cat, topic)
    if image:
        print(f"Imagen obtenida de Unsplash: {image['author']}")
    else:
        print("Sin imagen, se usará solo el emoji.")

    # Generar contenido con IA
    new_data = generate_article(cat, topic)

    # Insertar imagen al inicio del contenido
    image_html = build_image_html(image)
    content_with_image = image_html + new_data["content"]

    today = datetime.date.today()
    months_es = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    date_str = f"{today.day} de {months_es[today.month - 1]}, {today.year}"

    max_id = max((a.get("id", 0) for a in articles), default=0)

    new_article = {
        "id":       max_id + 1,
        "title":    new_data["title"],
        "excerpt":  new_data["excerpt"],
        "category": cat,
        "emoji":    emoji,
        "date":     date_str,
        "readTime": str(new_data.get("readTime", "5")),
        "featured": False,
        "image":    image["thumb"] if image else "",
        "content":  content_with_image,
    }

    articles.insert(0, new_article)
    for i, a in enumerate(articles):
        a["featured"] = (i == 0)

    if len(articles) > MAX_ARTICLES:
        articles = articles[:MAX_ARTICLES]

    html_updated = save_articles(html, articles)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_updated)

    print(f"Artículo publicado: {new_article['title']}")


if __name__ == "__main__":
    main()
