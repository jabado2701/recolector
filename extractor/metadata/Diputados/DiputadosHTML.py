import requests

url = "https://www.congreso.es/es/busqueda-de-diputados?p_p_id=diputadomodule&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_diputadomodule_mostrarFicha=true&codParlamentario=222&idLegislatura=XV&mostrarAgenda=false"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    html_content = response.text
    with open("Resultados/diputado.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("HTML guardado como 'diputado.html'")
else:
    print(f"Error al obtener la página: {response.status_code}")
