import streamlit as st
import numpy as np
import shapely as sh
import sectionproperties.pre as SPpre
import sectionproperties.analysis as SPana
import matplotlib.pyplot as plt

# ===============================
# Funções auxiliares
# ===============================

# create materials
steel = Material(
    name="Steel",
    elastic_modulus=200e3,
    poissons_ratio=0.3,
    density=7.85e-6,
    yield_strength=500,
    color="grey",
)

def cria_poligono(coordenadas_contorno, coordenadas_aberturas):
    return sh.Polygon(shell=coordenadas_contorno, holes=coordenadas_aberturas)

def cria_geometria(poligono, tamanho_malha, material):
    geom = SPpre.Geometry(geom=poligono, material=material)
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

# ===============================
# Interface Streamlit
# ===============================

st.title("Análise de Seção com sectionproperties")
st.write("Eng. Guilherme Vick")
st.write("Informe as coordenadas da seção.")

# -------------------------------
# Entrada do polígono externo
# -------------------------------
st.subheader("Coordenadas do Polígono Externo")

default_ext = [{"x": 0.0, "y": 0.0},
               {"x": 1.0, "y": 0.0},
               {"x": 1.0, "y": 1.0},
               {"x": 0.0, "y": 1.0}]

dados_ext = st.data_editor(
    default_ext,
    num_rows="dynamic",
    key="ext_table"
)

# -------------------------------
# Entrada das aberturas
# -------------------------------
st.subheader("Aberturas Internas (opcional)")

num_aberturas = st.number_input("Número de aberturas", min_value=0, step=1)

lista_aberturas = []
for i in range(num_aberturas):
    st.markdown(f"### Abertura {i+1}")
    default_aber = [{"x": 0.2, "y": 0.2},
                    {"x": 0.8, "y": 0.2},
                    {"x": 0.8, "y": 0.8},
                    {"x": 0.2, "y": 0.8}]
    tbl = st.data_editor(default_aber, num_rows="dynamic", key=f"aber_{i}")
    coords = [(float(row["x"]), float(row["y"])) for row in tbl]
    lista_aberturas.append(coords)

# -------------------------------
# Entrada do tamanho da malha
# -------------------------------
st.subheader("Parâmetros da malha")
tam_malha = st.number_input("Tamanho da malha", value=50.0)

# -------------------------------
# PROCESSAR
# -------------------------------
if st.button("Calcular e Plotar"):
    try:
        # Converte polígono externo
        coords_ext = [(float(row["x"]), float(row["y"])) for row in dados_ext]

        # Remove buracos vazios
        lista_aberturas = [a for a in lista_aberturas if len(a) > 0]

        # Criar polígono
        poligono = cria_poligono(coords_ext, lista_aberturas)

        # Criar geometria
        geom = cria_geometria(poligono, tam_malha, steel)
        secao = cria_secao(geom)
        calcula_propriedades(secao)

        # Mostrar resultados
        plot_resultados(secao)

        # Plot malha + centroides
        st.subheader("Malha e Centroides")
        fig, ax = plt.subplots(figsize=(6, 6))
        secao.plot_centroids(ax=ax)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Erro: {e}")
