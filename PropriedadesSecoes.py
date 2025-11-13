import streamlit as st
import numpy as np
import shapely as sh
import sectionproperties.pre as SPpre
import sectionproperties.pre.library as SPlib
import sectionproperties.analysis as SPana
import matplotlib.pyplot as plt

# Funções fornecidas

def cria_poligono(coordenadas_contorno, coordenadas_aberturas):
    return sh.Polygon(shell=coordenadas_contorno, holes=coordenadas_aberturas)

def cria_geometria(poligono, tamanho_malha):
    geom = SPpre.Geometry(geom=poligono)
    geom.create_mesh(tamanho_malha)
    return geom

def cria_secao(geometria):
    return SPana.Section(geometria)

def calcula_propriedades(secao):
    secao.calculate_geometric_properties()
    secao.calculate_warping_properties()

def plot_resultados(secao):
    st.subheader("Resultados das Propriedades da Seção")
    st.write(f"**Área:** {secao.get_area():.3f}")
    st.write(f"**Perímetro:** {secao.get_perimeter():.3f}")
    st.write(f"**Momento de Inércia Ixx:** {secao.get_ic()[0]:.3f}")
    st.write(f"**Momento de Inércia Iyy:** {secao.get_ic()[1]:.3f}")
    st.write(f"**Momento de Inércia Ixy:** {secao.get_ic()[2]:.3f}")
    st.write(f"**Momento de Torção J:** {secao.get_j():.3f}")

# Interface Streamlit

from streamlit_drawable_canvas import st_canvas

st.title("Análise de Seção com sectionproperties")
st.write("Desenhe o polígono externo e as aberturas diretamente na tela.")

st.subheader("Desenho do Polígono Externo")
canvas_ext = st_canvas(
    fill_color="rgba(255, 0, 0, 0.2)",
    stroke_color="#000000",
    stroke_width=2,
    background_color="#FFFFFF",
    height=400,
    width=400,
    drawing_mode="polygon",
    key="canvas_ext"
)

st.subheader("Desenho das Aberturas")
num_aberturas = st.number_input("Número de aberturas", min_value=0, step=1)
canvas_aberturas = []
for i in range(num_aberturas):
    st.markdown(f"### Abertura {i+1}")
    canvas = st_canvas(
        fill_color="rgba(0, 0, 255, 0.2)",
        stroke_color="#0000FF",
        stroke_width=2,
        background_color="#FFFFFF",
        height=300,
        width=400,
        drawing_mode="polygon",
        key=f"canvas_aber_{i}"
    )
    canvas_aberturas.append(canvas)

st.subheader("Tamanho da malha")
tam_malha = st.number_input("Tamanho da malha", value=50.0)

if st.button("Calcular e Plotar"):
    try:
        # Extrair polígono externo
        coords_ext = []
        if canvas_ext.json_data and "objects" in canvas_ext.json_data:
            for obj in canvas_ext.json_data["objects"]:
                if "path" in obj:
                    for p in obj["path"]:
                        if isinstance(p, list) and len(p) == 3:
                            coords_ext.append((p[1], p[2]))

        # Extrair aberturas
        lista_aberturas = []
        for canvas in canvas_aberturas:
            coords = []
            if canvas.json_data and "objects" in canvas.json_data:
                for obj in canvas.json_data["objects"]:
                    if "path" in obj:
                        for p in obj["path"]:
                            if isinstance(p, list) and len(p) == 3:
                                coords.append((p[1], p[2]))
            if coords:
                lista_aberturas.append(coords)

        poligono = cria_poligono(coords_ext, lista_aberturas)
        geom = cria_geometria(poligono, tam_malha)
        secao = cria_secao(geom)
        calcula_propriedades(secao)

        plot_resultados(secao)

        st.subheader("Malha e Centroides")
        fig = plt.figure(figsize=(6, 6))
        ax = fig.gca()
        secao.plot_centroids(ax=ax)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Erro: {e}")
