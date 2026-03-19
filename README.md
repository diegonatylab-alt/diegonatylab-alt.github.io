# PetaGuía 🐾

Blog de mascotas con publicación automática diaria usando la API de Anthropic.

## Estructura del proyecto

```
├── index.html              # El sitio completo (un solo archivo)
├── generate_article.py     # Script que genera artículos con IA
├── .github/
│   └── workflows/
│       └── daily_article.yml  # GitHub Actions: se ejecuta todos los días
└── README.md
```

## Setup inicial (hacer una sola vez)

### 1. Crear el repositorio en GitHub

El nombre debe ser exactamente: `diegonatylab-alt.github.io`

- Entrá a github.com → New repository
- Nombre: `diegonatylab-alt.github.io`
- Visibilidad: **Public**
- NO tildes ninguna opción adicional → Create repository

### 2. Subir los archivos

En la página del repositorio vacío, hacé clic en **"uploading an existing file"** y subí:
- `index.html`
- `generate_article.py`
- La carpeta `.github/workflows/daily_article.yml` (creá las carpetas manualmente)

O si tenés Git instalado:
```bash
git clone https://github.com/diegonatylab-alt/diegonatylab-alt.github.io
cd diegonatylab-alt.github.io
# Copiá los archivos acá
git add .
git commit -m "🚀 Sitio inicial"
git push
```

### 3. Activar GitHub Pages

- Dentro del repositorio → Settings → Pages
- Source: **Deploy from a branch**
- Branch: **main** → **/ (root)**
- Save

En 1-2 minutos el sitio estará en: **https://diegonatylab-alt.github.io**

### 4. Agregar la API key de Anthropic como secreto

- Dentro del repositorio → Settings → **Secrets and variables** → Actions
- Clic en **New repository secret**
- Name: `ANTHROPIC_API_KEY`
- Value: tu API key (empieza con `sk-ant-...`)
- Add secret

### 5. Verificar el workflow

- Ir a la pestaña **Actions** del repositorio
- Deberías ver "Publicar artículo diario"
- Podés ejecutarlo manualmente con el botón **"Run workflow"** para probarlo

---

## Cómo funciona

Cada día a las 8:00 AM UTC, GitHub Actions:
1. Clona el repositorio
2. Ejecuta `generate_article.py`
3. El script llama a la API de Claude Haiku para generar un artículo
4. Inserta el artículo en el array `articles` del `index.html`
5. Hace commit y push automáticamente
6. GitHub Pages publica el cambio en minutos

## Costos estimados

| Componente | Costo |
|------------|-------|
| GitHub Pages + Actions | Gratis |
| API Anthropic (Haiku) | ~$0.0075 por artículo = ~$2.70/año |
| Dominio .com (opcional) | ~$12/año |
| **Total** | **~$15/año** |

## Conectar un dominio personalizado

1. Comprá un dominio en Namecheap o Porkbun
2. En el panel DNS del registrador, creá estos registros:
   ```
   A    @    185.199.108.153
   A    @    185.199.109.153
   A    @    185.199.110.153
   A    @    185.199.111.153
   CNAME www  diegonatylab-alt.github.io
   ```
3. En GitHub → Settings → Pages → Custom domain → ingresá tu dominio
4. Tildá **Enforce HTTPS**

## Monetización con Google AdSense

1. Creá una cuenta en [Google AdSense](https://adsense.google.com)
2. Agregá tu sitio y esperá la aprobación (puede tardar días o semanas)
3. Una vez aprobado, en `index.html` buscá el comentario `<!-- Google AdSense placeholder -->` y reemplazalo con tu código real
4. Los placeholders con clase `ad-banner`, `ad-widget` e `in-article-ad` ya están posicionados estratégicamente

## Personalizar el nombre del sitio

En `index.html`, buscá todas las ocurrencias de `PetaGuía` y reemplazalas con el nombre que elijas.
