import requests
import duckdb
import os

# Função para obter a lista de todos os Pokémon
def get_all_pokemon():
    url = "https://pokeapi.co/api/v2/pokemon?limit=10000"  # PokeAPI permite obter todos os Pokémon com limite grande
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [pokemon['name'] for pokemon in data['results']]
    else:
        return []

# Função para obter dados de um Pokémon da PokeAPI
def get_pokemon_data(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
        return {
            "id": data['id'],
            "name": data['name'],
            "type": ', '.join([type_info['type']['name'] for type_info in data['types']]),
            "sprite": data['sprites']['front_default'],
            "hp": stats.get('hp', 0),
            "attack": stats.get('attack', 0),
            "defense": stats.get('defense', 0),
            "special_attack": stats.get('special-attack', 0),
            "special_defense": stats.get('special-defense', 0),
            "speed": stats.get('speed', 0)
        }
    else:
        return None

# Função para obter imagens dos tipos dos Pokémon locais
def get_local_type_images(directory):
    type_images = []
    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            type_name = os.path.splitext(filename)[0]
            image_path = os.path.abspath(os.path.join(directory, filename))
            type_images.append({
                "name": type_name,
                "image": image_path
            })
    return type_images

# Função para atualizar o banco de dados DuckDB com Pokémon
def update_pokemon_db(pokemon_list):
    conn = duckdb.connect('pokedex.db')
    for i, pokemon in enumerate(pokemon_list):
        data = get_pokemon_data(pokemon)
        if data:
            print(f"Baixando dados do {i+1}/{len(pokemon_list)}: {data['name']}")
            # Inserir ou atualizar os dados no banco de dados
            conn.execute(f"""
                INSERT INTO pokemon (id, name, type, sprite, hp, attack, defense, special_attack, special_defense, speed)
                VALUES ({data['id']}, '{data['name']}', '{data['type']}', '{data['sprite']}', {data['hp']}, {data['attack']}, {data['defense']}, {data['special_attack']}, {data['special_defense']}, {data['speed']})
                ON CONFLICT(id) DO UPDATE SET
                name=EXCLUDED.name, type=EXCLUDED.type, sprite=EXCLUDED.sprite, hp=EXCLUDED.hp, attack=EXCLUDED.attack, defense=EXCLUDED.defense, special_attack=EXCLUDED.special_attack, special_defense=EXCLUDED.special_defense, speed=EXCLUDED.speed;
            """)
    conn.close()

# Função para atualizar o banco de dados DuckDB com Tipos
def update_types_db(type_list):
    conn = duckdb.connect('pokedex.db')
    for t in type_list:
        # Inserir ou atualizar os dados no banco de dados
        conn.execute(f"""
            INSERT INTO types (name, image)
            VALUES ('{t['name']}', '{t['image']}')
            ON CONFLICT(name) DO UPDATE SET
            image=EXCLUDED.image;
        """)
    conn.close()

# Inicializar o banco de dados e criar as tabelas
def init_db():
    conn = duckdb.connect('pokedex.db')
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pokemon (
            id INTEGER PRIMARY KEY,
            name VARCHAR,
            type VARCHAR,
            sprite VARCHAR,
            hp INTEGER,
            attack INTEGER,
            defense INTEGER,
            special_attack INTEGER,
            special_defense INTEGER,
            speed INTEGER
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS types (
            name VARCHAR PRIMARY KEY,
            image VARCHAR
        );
    """)
    conn.close()

if __name__ == '__main__':
    # Inicializar o banco de dados
    init_db()

    # Obter a lista de todos os Pokémon
    #all_pokemon = get_all_pokemon()

    # Atualizar o banco de dados com todos os Pokémon
    #update_pokemon_db(all_pokemon)

    # Obter a lista de todas as tipagens e imagens locais
    all_types = get_local_type_images("src/images/type")

    # Atualizar o banco de dados com todas as tipagens e imagens
    update_types_db(all_types)
