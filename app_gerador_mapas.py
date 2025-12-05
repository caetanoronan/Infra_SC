"""
Gerador de Mapas Customizados - Backend Flask
Permite selecionar camadas e exportar em PNG
"""

import os
import json
from pathlib import Path
from datetime import datetime
import geopandas as gpd
import folium
from folium import GeoJsonTooltip
import numpy as np
from shapely.geometry import Point, LineString, Polygon, MultiLineString, MultiPolygon
import threading
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import base64
from io import BytesIO
from PIL import Image
import time

# ==================== CONFIGURAÇÃO ====================

app = Flask(__name__)
CORS(app)

# Caminhos
BASE_DIR = Path(r"C:\Users\caetanoronan\OneDrive - UFSC\Área de Trabalho\Infra_SC")
SHAPEFILE_DIR = BASE_DIR / "bc25_sc_shapefile_2020-10-01"
OUTPUT_DIR = BASE_DIR / "Mapas_prontos"
TEMP_DIR = BASE_DIR / "temp_maps"

# Criar diretórios se não existirem
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Cores das camadas
COLORS = {
    'rodovias-federais': '#e41a1c',
    'rodovias-estaduais': '#377eb8',
    'ferrovias': '#7b3294',
    'pontes': '#8073ac',
    'tuneis': '#e08214',
    'viadutos': '#d01c8b',
    'hidrovias': '#2c7fb8',
    'dutos': '#a6611a',
    'terminais': '#e41a1c',
    'helipontos': '#f46d43',
    'construcoes-aero': '#3288bd',
    'limite-uf': '#333333',
    'municipios': '#999999'
}

# Mapeamento de camadas para shapefiles
LAYER_MAPPING = {
    'rodovias-federais': ('fed_trecho_rodoviario_l.shp', '#e41a1c', 2),
    'rodovias-estaduais': ('est_trecho_rodoviario_l.shp', '#377eb8', 2),
    'ferrovias': ('fer_trecho_ferrovia_l.shp', '#7b3294', 2.2),
    'pontes': ('bnm_ponte_p.shp', '#8073ac', 4),
    'tuneis': ('bnm_tunel_l.shp', '#e08214', 2),
    'viadutos': ('bnm_viaduto_l.shp', '#d01c8b', 2),
    'hidrovias': ('hhi_trecho_hidrovia_l.shp', '#2c7fb8', 2.5),
    'dutos': ('dut_trecho_duto_l.shp', '#a6611a', 2),
    'terminais': ('tte_terminal_ponto_a.shp', '#e41a1c', 2),
    'helipontos': ('aer_pista_ponto_pouso_p.shp', '#f46d43', 5),
    'construcoes-aero': ('edf_edif_constr_aeroportuaria_a.shp', '#3288bd', 4),
    'limite-uf': ('lml_unidade_federacao_a.shp', '#333333', 3),
    'municipios': ('lml_municipio_a.shp', '#999999', 1)
}

# Cache de dados carregados
CACHE_LAYERS = {}
CACHE_TIMESTAMP = {}

# ==================== FUNÇÕES DE UTILIDADE ====================

def simplificar_geometrias(gdf, tolerance=0.0005):
    """Simplifica geometrias para melhor performance"""
    if gdf.empty or gdf.geometry.iloc[0].geom_type in ['Point', 'MultiPoint']:
        return gdf
    
    gdf = gdf.copy()
    gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=True)
    return gdf

def reduzir_precisao(gdf, decimals=5):
    """Reduz precisão das coordenadas"""
    if gdf.empty:
        return gdf
    
    gdf = gdf.copy()
    
    def round_geom(geom):
        if geom.is_empty:
            return geom
        
        geom_type = geom.geom_type
        
        if geom_type == 'Polygon':
            exterior = np.round(np.array(geom.exterior.coords), decimals)
            interiors = []
            for interior in geom.interiors:
                interiors.append(np.round(np.array(interior.coords), decimals))
            return Polygon(exterior, interiors)
        
        elif geom_type == 'MultiPolygon':
            polygons = []
            for poly in geom.geoms:
                exterior = np.round(np.array(poly.exterior.coords), decimals)
                interiors = []
                for interior in poly.interiors:
                    interiors.append(np.round(np.array(interior.coords), decimals))
                polygons.append(Polygon(exterior, interiors))
            return MultiPolygon(polygons)
        
        elif geom_type == 'LineString':
            coords = np.round(np.array(geom.coords), decimals)
            return LineString(coords)
        
        elif geom_type == 'MultiLineString':
            lines = []
            for line in geom.geoms:
                lines.append(np.round(np.array(line.coords), decimals))
            return MultiLineString(lines)
        
        elif geom_type == 'Point':
            coords = np.round(np.array(geom.coords), decimals)
            return Point(coords[0])
        
        else:
            return geom
    
    gdf['geometry'] = gdf['geometry'].apply(round_geom)
    return gdf

def carregar_camada(layer_id):
    """Carrega uma camada do shapefile com cache"""
    
    # Verificar cache (atualizar a cada 1 hora)
    if layer_id in CACHE_LAYERS:
        if time.time() - CACHE_TIMESTAMP.get(layer_id, 0) < 3600:
            return CACHE_LAYERS[layer_id]
    
    if layer_id not in LAYER_MAPPING:
        return None
    
    shapefile, _, _ = LAYER_MAPPING[layer_id]
    shapefile_path = SHAPEFILE_DIR / shapefile
    
    if not shapefile_path.exists():
        print(f"⚠️ Arquivo não encontrado: {shapefile_path}")
        return None
    
    try:
        print(f"📥 Carregando {layer_id}...")
        gdf = gpd.read_file(shapefile_path).to_crs("EPSG:4326")
        
        # Simplificar geometrias
        if gdf.geometry.iloc[0].geom_type not in ['Point', 'MultiPoint']:
            gdf = simplificar_geometrias(gdf, tolerance=0.0005)
        
        # Reduzir precisão
        gdf = reduzir_precisao(gdf, decimals=5)
        
        # Manter apenas colunas essenciais
        essential_cols = ['nome', 'tipotrecho', 'bitola', 'categoria', 'tipo']
        existing_cols = [col for col in essential_cols if col in gdf.columns]
        if existing_cols:
            gdf = gdf[existing_cols + ['geometry']]
        else:
            gdf = gdf[['geometry']]
        
        # Cache
        CACHE_LAYERS[layer_id] = gdf
        CACHE_TIMESTAMP[layer_id] = time.time()
        
        print(f"✅ {layer_id} carregado: {len(gdf)} features")
        return gdf
    
    except Exception as e:
        print(f"❌ Erro ao carregar {layer_id}: {e}")
        return None

def criar_mapa_customizado(selected_layers, nome_arquivo="mapa_customizado"):
    """Cria um mapa com as camadas selecionadas"""
    
    print(f"\n🗺️ Criando mapa com {len(selected_layers)} camadas...")
    
    # Criar mapa base
    mapa = folium.Map(
        location=[-27.5, -49.5],
        zoom_start=7,
        tiles="CartoDB positron",
        min_zoom=5,
        max_zoom=12,
        prefer_canvas=True,
        control_scale=True
    )
    
    # Adicionar camadas
    camadas_adicionadas = 0
    
    for layer_id in selected_layers:
        if layer_id not in LAYER_MAPPING:
            continue
        
        gdf = carregar_camada(layer_id)
        if gdf is None or gdf.empty:
            print(f"⚠️ {layer_id} vazio ou indisponível")
            continue
        
        color, weight = LAYER_MAPPING[layer_id][1], LAYER_MAPPING[layer_id][2]
        
        try:
            # Adicionar GeoJSON ao mapa
            folium.GeoJson(
                gdf,
                name=layer_id.replace('-', ' ').title(),
                style_function=lambda x, c=color, w=weight: {
                    'color': c,
                    'weight': w,
                    'opacity': 0.8
                },
                popup=folium.GeoJsonPopup(fields=list(gdf.columns)[:-1]) if len(gdf.columns) > 1 else None,
                show=True
            ).add_to(mapa)
            
            camadas_adicionadas += 1
            print(f"✓ {layer_id} adicionado")
        
        except Exception as e:
            print(f"❌ Erro ao adicionar {layer_id}: {e}")
    
    # Adicionar controle de camadas
    folium.LayerControl(position="topright", collapsed=False).add_to(mapa)
    
    # Salvar HTML temporário
    html_path = TEMP_DIR / f"{nome_arquivo}.html"
    mapa.save(str(html_path))
    
    print(f"✅ Mapa HTML gerado: {html_path}")
    print(f"📊 Total de camadas adicionadas: {camadas_adicionadas}")
    
    return html_path

# ==================== ROTAS FLASK ====================

@app.route('/', methods=['GET'])
def index():
    """Página principal"""
    return render_template('gerador_mapas_app.html')

@app.route('/api/layers', methods=['GET'])
def get_layers():
    """Retorna informações das camadas"""
    layers = {
        'transportes': [
            {'id': 'rodovias-federais', 'name': 'Rodovias Federais', 'color': COLORS['rodovias-federais']},
            {'id': 'rodovias-estaduais', 'name': 'Rodovias Estaduais', 'color': COLORS['rodovias-estaduais']},
            {'id': 'ferrovias', 'name': 'Ferrovias', 'color': COLORS['ferrovias']}
        ],
        'obras_arte': [
            {'id': 'pontes', 'name': 'Pontes', 'color': COLORS['pontes']},
            {'id': 'tuneis', 'name': 'Túneis', 'color': COLORS['tuneis']},
            {'id': 'viadutos', 'name': 'Viadutos', 'color': COLORS['viadutos']}
        ],
        'maritima': [
            {'id': 'hidrovias', 'name': 'Hidrovias', 'color': COLORS['hidrovias']},
            {'id': 'dutos', 'name': 'Dutos', 'color': COLORS['dutos']},
            {'id': 'terminais', 'name': 'Terminais Portuários', 'color': COLORS['terminais']}
        ],
        'aviacao': [
            {'id': 'helipontos', 'name': 'Helipontos', 'color': COLORS['helipontos']},
            {'id': 'construcoes-aero', 'name': 'Construções Aeroportuárias', 'color': COLORS['construcoes-aero']}
        ],
        'limites': [
            {'id': 'limite-uf', 'name': 'Limite Estadual', 'color': COLORS['limite-uf']},
            {'id': 'municipios', 'name': 'Municípios', 'color': COLORS['municipios']}
        ]
    }
    return jsonify(layers)

@app.route('/api/gerar-mapa', methods=['POST'])
def gerar_mapa():
    """Gera mapa com camadas selecionadas"""
    
    try:
        data = request.json
        selected_layers = data.get('layers', [])
        nome_arquivo = data.get('nome', 'mapa_customizado')
        
        if not selected_layers:
            return jsonify({'error': 'Nenhuma camada selecionada'}), 400
        
        # Sanitizar nome
        nome_arquivo = "".join(c for c in nome_arquivo if c.isalnum() or c in (' ', '-', '_')).strip()
        if not nome_arquivo:
            nome_arquivo = 'mapa_customizado'
        
        print(f"\n📝 Gerando: {nome_arquivo}")
        print(f"📋 Camadas: {selected_layers}")
        
        # Criar mapa
        html_path = criar_mapa_customizado(selected_layers, nome_arquivo)
        
        # Retornar URL do mapa
        return jsonify({
            'success': True,
            'message': f'Mapa gerado com sucesso!',
            'url': f'/visualizar/{nome_arquivo}',
            'layers_count': len(selected_layers)
        })
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/visualizar/<nome_arquivo>', methods=['GET'])
def visualizar_mapa(nome_arquivo):
    """Visualiza o mapa gerado"""
    html_path = TEMP_DIR / f"{nome_arquivo}.html"
    
    if not html_path.exists():
        return "Mapa não encontrado", 404
    
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/exportar-png', methods=['POST'])
def exportar_png():
    """Exporta mapa em PNG"""
    
    try:
        data = request.json
        nome_arquivo = data.get('nome', 'mapa_customizado')
        
        # Sanitizar nome
        nome_arquivo = "".join(c for c in nome_arquivo if c.isalnum() or c in (' ', '-', '_')).strip()
        if not nome_arquivo:
            nome_arquivo = 'mapa_customizado'
        
        print(f"\n📸 Exportando PNG: {nome_arquivo}")
        
        # Criar timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        png_filename = f"{nome_arquivo}_{timestamp}.png"
        png_path = OUTPUT_DIR / png_filename
        
        # Para agora, vamos criar um placeholder
        # Em produção, usar selenium/puppeteer para screenshot
        img = Image.new('RGB', (1200, 800), color=(255, 255, 255))
        img.save(png_path)
        
        print(f"✅ PNG salvo: {png_path}")
        
        return jsonify({
            'success': True,
            'message': f'PNG exportado: {png_filename}',
            'filepath': str(png_path)
        })
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Status da aplicação"""
    return jsonify({
        'status': 'online',
        'output_dir': str(OUTPUT_DIR),
        'total_mapas': len(list(OUTPUT_DIR.glob('*.png')))
    })

# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Iniciando Gerador de Mapas Customizados")
    print("=" * 60)
    print(f"📁 Diretório de shapefiles: {SHAPEFILE_DIR}")
    print(f"📁 Diretório de saída: {OUTPUT_DIR}")
    print(f"📁 Diretório temporário: {TEMP_DIR}")
    print("\n🌐 Acesse: http://localhost:5000")
    print("=" * 60 + "\n")
    
    app.run(debug=True, port=5000, host='localhost')
