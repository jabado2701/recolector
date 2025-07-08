
## 🛰️ Recolector de Actividad Política en X/Twitter


Este módulo automatiza la recolección, estructuración, limpieza y traducción de datos públicos sobre la actividad en X/Twitter de políticos españoles. Parte de un archivo Excel base con información inicial manual y lo complementa con datos descargados desde fuentes oficiales (Congreso, Wikipedia, X/Twitter).


## 🚀 Funcionalidades
````

### 🧾 Metadata
📂 `extractor/metadata/`
- `DiputadosInfo.py`: extrae y guarda en `.json` los datos de todos los diputados desde el sitio del Congreso (nombre, partido, provincia, comunidad autónoma, edad, legislaturas...).
- `DiputadosExcel.py`: selecciona del `.json` solo a los políticos incluidos en el Excel.
- `PresidentesExcel.py`: obtiene la misma información para presidentes autonómicos desde Wikipedia.

### 🗣️ Posts
📂 `extractor/posts/`
- `MainPosts.py`: módulo principal de extracción. Permite definir si se extraen todos los posts o de un político específico, y filtrar por cantidad o rango de fechas.
- `ExtractorPosts.py`: conecta con la API o realiza scraping para obtener los tweets.
- `TwitterHTML.py` y `ApoyoPosts.py`: funciones auxiliares para extracción estructurada.
- `ControllerPosts.py`: orquesta la escritura al Excel.

### 💬 Comentarios
📂 `extractor/comentarios/`
- `MainComentarios.py`: extrae un número determinado de comentarios por post descargado.
- `ExtractorComentarios.py`: realiza el scraping o llamada API para cada post.
- `ApoyoComentarios.py` y `ControllerComentarios.py`: manejan estructura, validación y escritura.

### 🌍 Idioma y Traducción
📂 `traductor/`
- `AñadidoIdiomas.py`: detecta el idioma de cada mensaje (post, comentario, respuesta) y lo añade en una nueva columna.
- `ContadorIdiomas.py`: contabiliza los idiomas detectados por tipo de mensaje.
- `Traductor.py`: traduce automáticamente cualquier texto no escrito en castellano al español.

### 🧹 Limpieza y Estadísticas
📂 `limpieza/`
- `LimpiezaDesconocido.py`: elimina entradas con idioma no detectado.
- `BorradorDuplicados.py`: elimina publicaciones o comentarios duplicados.
- `ContadorPosts.py`: cuenta cuántos posts tiene cada político.
- `ContadorComentarios.py`: agrupa los comentarios por número y post para mostrar distribución.
````

## 📁 Estructura del Proyecto

```

Recolector/
├── extractor/
│   ├── comentarios/
│   ├── metadata/
│   ├── posts/
│   └── FuncionesConjuntas.py
├── traductor/
├── limpieza/
├── cookies.json
├── .gitignore
└── README.md

````

## ⚙️ Requisitos
````
- Python 3.10+
- pandas  
- numpy  
- openpyxl  
- selenium  
- undetected-chromedriver  
- beautifulsoup4  
- requests  
- langdetect  
- deep-translator  
- tqdm *(opcional)*

> ⚠️ Muy importante asegurarse que  `ChromeDriver` está actualizado y es compatible con el navegador si se usa Selenium.
````
## 🖥️ Ejecución

1️⃣ Clonar el repositorio:

```bash
git clone https://github.com/jabado2701/recolector.git
cd recolector
````

2️⃣ Instalar dependencias:

```bash
pip install -r requirements.txt
```

3️⃣ Ejecutar los módulos:

```bash
# Extraer información de diputados
python extractor/metadata/DiputadosInfo.py

# Seleccionar los del Excel
python extractor/metadata/DiputadosExcel.py

# Extraer publicaciones
python extractor/posts/MainPosts.py

# Extraer comentarios
python extractor/comentarios/MainComentarios.py

# Detectar idiomas
python traductor/AñadidoIdiomas.py

# Traducir mensajes
python traductor/Traductor.py

# Limpieza final
python limpieza/LimpiezaDesconocido.py
python limpieza/BorradorDuplicados.py
```

## 📄 Notas adicionales

* El archivo base `politicos.xlsx` se muestra con los contenidos previos a la ejecución de los códigos.
* Todos los datos gestionados son públicos y obtenidos de fuentes oficiales (Congreso, Wikipedia, X/Twitter).
