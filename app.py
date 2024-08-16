import streamlit as st
import requests
import json
from datetime import datetime

# Configuración de las APIs (las claves se obtienen de los secretos de Streamlit)
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]
SERPER_API_KEY = st.secrets["SERPER_API_KEY"]

def get_research_grant_info(campo_estudio, tipo_ayuda, fecha_limite, solo_guatemaltecos):
    # Construir el prompt para la API de Together
    prompt = f"Proporciona información sobre ayudas para investigación o publicación en el campo de {campo_estudio} para tipo de ayuda {tipo_ayuda} con fecha límite cercana a {fecha_limite}."
    if solo_guatemaltecos:
        prompt += " Incluye solo ayudas disponibles para guatemaltecos."
    prompt += " Incluye nombres de ayudas, requisitos básicos y enlaces si están disponibles."

    # Llamada a la API de Together
    response = requests.post(
        "https://api.together.xyz/inference",
        headers={
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "togethercomputer/llama-2-70b-chat",
            "prompt": prompt,
            "max_tokens": 512,
            "temperature": 0.7
        }
    )

    ai_response = response.json().get("choices", [{}])[0].get("text", "")

    # Llamada a la API de Serper para obtener resultados de búsqueda relacionados
    search_query = f"ayudas investigación o publicación {campo_estudio} {tipo_ayuda}"
    if solo_guatemaltecos:
        search_query += " para guatemaltecos"
    serper_response = requests.post(
        "https://google.serper.dev/search",
        headers={
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "q": search_query
        }
    )

    search_results = serper_response.json().get("organic", [])[:3]  # Tomamos los primeros 3 resultados

    return ai_response, search_results

# Interfaz de Streamlit
st.title("Buscador de Ayudas para Investigación o Publicación")

campo_estudio = st.text_input("Campo de estudio")
tipo_ayuda = st.selectbox("Tipo de ayuda", ["Investigación", "Publicación"])
fecha_limite = st.date_input("Fecha límite de aplicación")
solo_guatemaltecos = st.checkbox("Mostrar solo ayudas disponibles para guatemaltecos")

if st.button("Buscar ayudas"):
    if campo_estudio and tipo_ayuda and fecha_limite:
        fecha_limite_str = fecha_limite.strftime("%d/%m/%Y")
        ai_info, search_results = get_research_grant_info(campo_estudio, tipo_ayuda, fecha_limite_str, solo_guatemaltecos)

        st.subheader("Información de ayudas")
        st.write(ai_info)

        st.subheader("Resultados de búsqueda relacionados")
        if search_results:
            for result in search_results:
                st.write(f"- [{result.get('title')}]({result.get('link')})")
                st.write(result.get('snippet', ''))
        else:
            st.write("No se encontraron resultados de búsqueda.")
    else:
        st.warning("Por favor, completa todos los campos.")
