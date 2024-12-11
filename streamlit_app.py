import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configurar a página para modo wide
st.set_page_config(layout="wide")

# Função para obter dados dos Pokémon do servidor Flask
def get_pokemon(offset=0, limit=12):
    response = requests.get(f"http://127.0.0.1:5000/api/pokemon?offset={offset}&limit={limit}")
    if response.status_code == 200:
        return response.json()
    else:
        return []

# Função para obter todos os Pokémon para a caixa de seleção
def get_all_pokemon():
    response = requests.get("http://127.0.0.1:5000/api/pokemon?offset=0&limit=1000")
    if response.status_code == 200:
        return response.json()
    else:
        return []

# Função para obter imagens dos tipos dos Pokémon do servidor Flask
def get_type_images():
    response = requests.get("http://127.0.0.1:5000/api/types")
    if response.status_code == 200:
        return {t['name']: t['image'] for t in response.json()}
    else:
        return {}

# Estado inicial da aplicação
if 'view' not in st.session_state:
    st.session_state.view = 'list'
if 'pokemon_data' not in st.session_state:
    st.session_state.pokemon_data = []
if 'all_pokemon_data' not in st.session_state:
    st.session_state.all_pokemon_data = get_all_pokemon()
if 'type_images' not in st.session_state:
    st.session_state.type_images = get_type_images()
if 'offset' not in st.session_state:
    st.session_state.offset = 0
if 'selected_pokemon' not in st.session_state:
    st.session_state.selected_pokemon = None

# Função para alternar entre as visões
def set_view(view):
    st.session_state.view = view

# Função para selecionar um Pokémon
def select_pokemon_by_id(pokemon_id):
    for pokemon in st.session_state.all_pokemon_data:
        if pokemon['id'] == pokemon_id:
            st.session_state.selected_pokemon = pokemon
            set_view('detail')
            break

# Função para carregar os Pokémon da página atual
def load_pokemon_page(offset):
    new_pokemon = get_pokemon(offset)
    st.session_state.pokemon_data = new_pokemon

# Função para exibir as imagens das tipagens
def display_type_images(types):
    width = 100 if st.session_state.view == 'list' else 200
    for t in types.split(", "):
        type_name = t.lower()
        if type_name in st.session_state.type_images:
            st.image(st.session_state.type_images[type_name], width=width)

# Centralizar título
st.markdown("<h1 style='text-align: center;'>Pokédex</h1>", unsafe_allow_html=True)

# Centralizar botões de navegação
col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
with col2:
    if st.button("Anterior", use_container_width=True):
        if st.session_state.offset >= 12:
            st.session_state.offset -= 12
            load_pokemon_page(st.session_state.offset)
with col3:
    if st.button("Alternar Visão", key="toggle_view", use_container_width=True):
        if st.session_state.view == 'list':
            set_view('detail')
        else:
            set_view('list')
with col4:
    if st.button("Próximo", use_container_width=True):
        st.session_state.offset += 12
        load_pokemon_page(st.session_state.offset)

# Carregar a página inicial de Pokémon
if not st.session_state.pokemon_data:
    load_pokemon_page(st.session_state.offset)

# Visão de Lista
if st.session_state.view == 'list':
    pokemon_list = st.session_state.pokemon_data

    # Exibir Pokémon em linhas de 6, 2 linhas por página
    for i in range(0, len(pokemon_list), 6):
        cols = st.columns(6)
        for j in range(6):
            if i + j < len(pokemon_list):
                pokemon = pokemon_list[i + j]
                with cols[j]:
                    st.markdown(
                        f"""
                        <div style='border: 2px solid #ddd; padding: 10px; border-radius: 10px; text-align: center;'>
                            <img src='{pokemon['sprite']}' width='100'/>
                            <h4>{pokemon['name']}</h4>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    display_type_images(pokemon['type'])
                    if st.button("Detalhes", key=f"button_{pokemon['id']}", on_click=lambda p=pokemon: select_pokemon_by_id(p['id'])):
                        pass

# Visão Detalhada
elif st.session_state.view == 'detail' and st.session_state.selected_pokemon:
    col1, col2 = st.columns([1, 2])

    with col1:
        # Adicionar caixa de seleção para selecionar Pokémon
        pokemon_names = [pokemon['name'] for pokemon in st.session_state.all_pokemon_data]
        selected_name = st.selectbox("Selecionar Pokémon", pokemon_names, index=pokemon_names.index(st.session_state.selected_pokemon['name']))
        select_pokemon_by_id(next(pokemon['id'] for pokemon in st.session_state.all_pokemon_data if pokemon['name'] == selected_name))

        st.image(st.session_state.selected_pokemon['sprite'], use_container_width=True)
        display_type_images(st.session_state.selected_pokemon['type'])

    with col2:
        stats = {
            "HP": st.session_state.selected_pokemon['hp'],
            "Ataque": st.session_state.selected_pokemon['attack'],
            "Defesa": st.session_state.selected_pokemon['defense'],
            "Ataque Especial": st.session_state.selected_pokemon['special_attack'],
            "Defesa Especial": st.session_state.selected_pokemon['special_defense'],
            "Velocidade": st.session_state.selected_pokemon['speed']
        }

        # Exibir os gráficos dos status
        df = pd.DataFrame(list(stats.items()), columns=["Status", "Valor"])
        fig = px.bar(df, y="Status", x="Valor", orientation='h', 
                     title="Status Base do Pokémon",
                     color="Status", 
                     color_discrete_sequence=px.colors.qualitative.Bold)

        # Remover a legenda e adicionar os valores ao lado
        fig.update_layout(showlegend=False)
        fig.update_traces(texttemplate='%{x}', textposition='outside')

        st.plotly_chart(fig, use_container_width=True)

# Nota de créditos no rodapé
st.markdown("""
<div style='text-align: center;'>
    <p>Imagens retiradas de <a href="https://github.com/PokeAPI/pokeapi/tree/master/data/v2" target="_blank">GitHub - PokeAPI</a></p>
</div>
""", unsafe_allow_html=True)
