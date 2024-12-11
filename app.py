from flask import Flask, jsonify, request
import duckdb

app = Flask(__name__)

# Função para obter todos os Pokémon do banco de dados com paginação
def get_pokemon_from_db(offset=0, limit=12):
    conn = duckdb.connect('pokedex.db')
    query = f"SELECT * FROM pokemon LIMIT {limit} OFFSET {offset}"
    pokemon_data = conn.execute(query).fetchall()
    columns = [desc[0] for desc in conn.description]
    conn.close()

    # Converter os dados em uma lista de dicionários
    result = [dict(zip(columns, row)) for row in pokemon_data]
    return result

# Função para obter todos os tipos de Pokémon do banco de dados
def get_types_from_db():
    conn = duckdb.connect('pokedex.db')
    query = "SELECT * FROM types"
    type_data = conn.execute(query).fetchall()
    columns = [desc[0] for desc in conn.description]
    conn.close()

    # Converter os dados em uma lista de dicionários
    result = [dict(zip(columns, row)) for row in type_data]
    return result

@app.route('/api/pokemon', methods=['GET'])
def get_pokemon():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 12))
    pokemon_data = get_pokemon_from_db(offset, limit)
    return jsonify(pokemon_data)

@app.route('/api/types', methods=['GET'])
def get_types():
    type_data = get_types_from_db()
    return jsonify(type_data)

if __name__ == '__main__':
    app.run(debug=True)
