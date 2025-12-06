# -*- coding: utf-8 -*-
"""
Gerador de Mapas Customizados - Backend Flask
Permite selecionar camadas e exportar em PNG
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import geopandas as gpd
import folium
import numpy as np
from shapely.geometry import Point, LineString, Polygon, MultiLineString, MultiPolygon
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from io import BytesIO
from PIL import Image
import time
import zipfile
import urllib.request

# Configurar encoding UTF-8
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ==================== CONFIGURAÇÃO ====================

app = Flask(__name__)
CORS(app)

# Caminhos
# Usa o diretório do arquivo para funcionar local e em servidores
BASE_DIR = Path(__file__).resolve().parent
SHAPEFILE_DIR = BASE_DIR / "bc25_sc_shapefile_2020-10-01"
OUTPUT_DIR = BASE_DIR / "Mapas_prontos"
TEMP_DIR = BASE_DIR / "temp_maps"

# URL para download dos shapefiles (configurar após upload)
SHAPEFILE_URL = os.environ.get("SHAPEFILE_URL", "")

# Criar diretórios se não existirem
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# ==================== DOWNLOAD SHAPEFILES ====================

def baixar_shapefiles():
    """Baixa e extrai shapefiles se não existirem"""
    if SHAPEFILE_DIR.exists() and any(SHAPEFILE_DIR.iterdir()):
        print("[OK] Shapefiles já existem localmente")
        return True
    
    if not SHAPEFILE_URL:
        print("[WARN] SHAPEFILE_URL não configurada")
        return False
    
    print(f"[DOWNLOAD] Baixando shapefiles de {SHAPEFILE_URL}...")
    zip_path = BASE_DIR / "shapefiles_temp.zip"
    
    try:
        # Download
        urllib.request.urlretrieve(SHAPEFILE_URL, zip_path)
        print(f"[OK] Download concluído: {zip_path.stat().st_size / (1024*1024):.1f} MB")
        
        # Extrair
        print("[EXTRACT] Extraindo arquivos...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(BASE_DIR)
        
        # Remover zip temporário
        zip_path.unlink()
        
        print(f"[OK] Shapefiles extraídos em {SHAPEFILE_DIR}")
        return True
    
    except Exception as e:
        print(f"[ERROR] Falha ao baixar shapefiles: {e}")
        if zip_path.exists():
            zip_path.unlink()
        return False

# Baixar shapefiles no startup
baixar_shapefiles()

# Cache de mapas HTML em memória (evita problemas com sistema de arquivos)
MAPS_CACHE = {}

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

# Mapeamento de camadas para shapefiles (cores e pesos do mapa original)
LAYER_MAPPING = {
    'rodovias-federais': ('rod_via_deslocamento_l.shp', '#d73027', 2.2, 0.9, 'Federal'),
    'rodovias-estaduais': ('rod_via_deslocamento_l.shp', '#4575b4', 2.0, 0.85, 'Estadual/Distrital'),
    'ferrovias': ('fer_trecho_ferroviario_l.shp', '#7b3294', 2.3, 0.9, None),
    'pontes': ('tra_ponte_l.shp', '#8073ac', 2, 0.9, None),
    'tuneis': ('tra_tunel_l.shp', '#e08214', 2.2, 0.9, None),
    'viadutos': ('tra_passagem_elevada_viaduto_l.shp', '#f781bf', 2.2, 0.9, None),
    'hidrovias': ('hdv_trecho_hidroviario_l.shp', '#2c7fb8', 3.2, 0.85, None),
    'dutos': ('dut_trecho_duto_l.shp', '#a6611a', 2.6, 0.9, None),
    'terminais': ('hdv_atracadouro_terminal_p.shp', 'red', 5, 0.85, None),
    'helipontos': ('aer_pista_ponto_pouso_p.shp', '#f46d43', 5, 0.85, None),
    'construcoes-aero': ('edf_edif_constr_aeroportuaria_p.shp', '#3288bd', 5, 0.75, None),
    'limite-uf': ('lml_unidade_federacao_a.shp', '#000000', 2.5, 1.0, None),
    'municipios': ('lml_municipio_a.shp', '#2ca25f', 1.1, 0.18, None)
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
    
    shapefile, _, _, _, filtro = LAYER_MAPPING[layer_id]
    shapefile_path = SHAPEFILE_DIR / shapefile
    
    if not shapefile_path.exists():
        print("[WARN] File not found: {}".format(shapefile_path))
        return None
    
    try:
        print("[LOAD] Loading {}...".format(layer_id))
        gdf = gpd.read_file(str(shapefile_path)).to_crs("EPSG:4326")
        
        # Aplicar filtro de jurisdicao se necessario (rodovias)
        if filtro and 'jurisdicao' in gdf.columns:
            gdf = gdf[gdf['jurisdicao'] == filtro]
        
        # Simplificar geometrias
        if gdf.geometry.iloc[0].geom_type not in ['Point', 'MultiPoint']:
            gdf = simplificar_geometrias(gdf, tolerance=0.0005)
        
        # Reduzir precisão
        gdf = reduzir_precisao(gdf, decimals=5)
        
        # Manter apenas colunas essenciais
        essential_cols = ['nome', 'tipotrecho', 'bitola', 'categoria', 'tipo', 'jurisdicao', 'revestimen', 'operaciona']
        existing_cols = [col for col in essential_cols if col in gdf.columns]
        if existing_cols:
            gdf = gdf[existing_cols + ['geometry']]
        else:
            gdf = gdf[['geometry']]
        
        # Cache
        CACHE_LAYERS[layer_id] = gdf
        CACHE_TIMESTAMP[layer_id] = time.time()
        
        print("[OK] {} loaded: {} features".format(layer_id, len(gdf)))
        return gdf
    
    except Exception as e:
        print("[ERROR] Failed to load {}: {}".format(layer_id, str(e)))
        return None

def criar_mapa_customizado(selected_layers, nome_arquivo="mapa_customizado"):
    """Cria um mapa com as camadas selecionadas"""
    
    print("\n[MAP] Creating map with {} layers...".format(len(selected_layers)))
    
    # Criar mapa base (igual ao mapa original)
    mapa = folium.Map(
        location=[-27.5, -49.5],
        zoom_start=7,
        tiles="CartoDB positron",
        min_zoom=5,
        max_zoom=12,
        prefer_canvas=True,
        control_scale=True
    )
    
    # Adicionar titulo, rosa dos ventos e info cartografica
    ui_html = """
    <div style="font-family: Arial, sans-serif;">
        <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 1000; background: rgba(255,255,255,0.92); padding: 8px 14px; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.15); font-size: 14px; font-weight: 600; color: #1f2933; text-align: center;">
            Mapa de Infraestrutura Logistica - Santa Catarina
        </div>
        <div style="position: fixed; top: 70px; left: 12px; z-index: 1000;">
            <div style="position: relative; width: 50px; height: 50px; border: 2px solid #333; border-radius: 50%; background: rgba(255,255,255,0.92); box-shadow: 0 2px 6px rgba(0,0,0,0.15); display: flex; align-items: center; justify-content: center; font-weight: 700; color: #333; font-size: 12px;">
                N
                <div style="position: absolute; top: 4px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 5px solid transparent; border-right: 5px solid transparent; border-bottom: 10px solid #d62728;"></div>
            </div>
        </div>
        <div style="position: fixed; bottom: 12px; right: 12px; z-index: 1000; background: rgba(255,255,255,0.95); padding: 8px 10px; border-radius: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.15); font-size: 10px; line-height: 1.3; max-width: 280px;">
            <strong>Datum:</strong> WGS84<br>
            <strong>Fonte:</strong> IBGE BC25 2020<br>
            <strong>Autor:</strong> Ronan A. Caetano
        </div>
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(ui_html))
    
    # Adicionar camadas
    camadas_adicionadas = 0
    
    for layer_id in selected_layers:
        if layer_id not in LAYER_MAPPING:
            continue
        
        gdf = carregar_camada(layer_id)
        if gdf is None or gdf.empty:
            print("[WARN] {} empty or unavailable".format(layer_id))
            continue
        
        shapefile, color, weight, opacity, filtro = LAYER_MAPPING[layer_id]
        geom_type = gdf.geometry.iloc[0].geom_type if len(gdf) > 0 else None
        
        try:
            # Para pontos (helipontos, terminais, construcoes), usar CircleMarker
            if geom_type in ['Point', 'MultiPoint']:
                fg = folium.FeatureGroup(name=layer_id.replace('-', ' ').title(), show=True)
                for _, row in gdf.iterrows():
                    tooltip = row.get('nome', layer_id) if 'nome' in gdf.columns else layer_id
                    folium.CircleMarker(
                        location=[row.geometry.y, row.geometry.x],
                        radius=weight,
                        color=color,
                        fill=True,
                        fill_opacity=opacity,
                        tooltip=tooltip
                    ).add_to(fg)
                fg.add_to(mapa)
            else:
                # Para linhas e poligonos, usar GeoJson
                # Municipios com fillOpacity especial
                if layer_id == 'municipios':
                    folium.GeoJson(
                        gdf,
                        name=layer_id.replace('-', ' ').title(),
                        style_function=lambda x, c=color, w=weight, o=opacity: {
                            'color': c,
                            'fillColor': c,
                            'weight': w,
                            'fillOpacity': o,
                            'opacity': 1.0
                        },
                        show=True
                    ).add_to(mapa)
                # Dutos com linha tracejada
                elif layer_id == 'dutos':
                    folium.GeoJson(
                        gdf,
                        name=layer_id.replace('-', ' ').title(),
                        style_function=lambda x, c=color, w=weight, o=opacity: {
                            'color': c,
                            'weight': w,
                            'opacity': o,
                            'dashArray': '6,4'
                        },
                        show=True
                    ).add_to(mapa)
                # Limite UF sempre visivel
                elif layer_id == 'limite-uf':
                    folium.GeoJson(
                        gdf,
                        name=layer_id.replace('-', ' ').title(),
                        style_function=lambda x, c=color, w=weight: {
                            'color': c,
                            'weight': w,
                            'fillOpacity': 0
                        },
                        show=True
                    ).add_to(mapa)
                else:
                    # Demais camadas (rodovias, ferrovias, pontes, etc)
                    folium.GeoJson(
                        gdf,
                        name=layer_id.replace('-', ' ').title(),
                        style_function=lambda x, c=color, w=weight, o=opacity: {
                            'color': c,
                            'weight': w,
                            'opacity': o
                        },
                        # Exibir camadas selecionadas por padrão
                        show=True
                    ).add_to(mapa)
            
            camadas_adicionadas += 1
            print("[OK] {} added".format(layer_id))
        
        except Exception as e:
            print("[ERROR] Failed to add {}: {}".format(layer_id, str(e)))
    
    # Adicionar controle de camadas
    folium.LayerControl(position="topright", collapsed=False).add_to(mapa)
    
    # Salvar HTML em string (para cache em memória)
    html_str = mapa._repr_html_()
    
    # Também salvar em arquivo (backup)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    html_path = TEMP_DIR / "{}.html".format(nome_arquivo)
    mapa.save(str(html_path))
    
    print("[OK] Map HTML generated: {}".format(html_path))
    print("[STAT] Total layers added: {}".format(camadas_adicionadas))
    
    return nome_arquivo, html_str

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
            {'id': 'tuneis', 'name': 'Tuneis', 'color': COLORS['tuneis']},
            {'id': 'viadutos', 'name': 'Viadutos', 'color': COLORS['viadutos']}
        ],
        'maritima': [
            {'id': 'hidrovias', 'name': 'Hidrovias', 'color': COLORS['hidrovias']},
            {'id': 'dutos', 'name': 'Dutos', 'color': COLORS['dutos']},
            {'id': 'terminais', 'name': 'Terminais Portuarios', 'color': COLORS['terminais']}
        ],
        'aviacao': [
            {'id': 'helipontos', 'name': 'Helipontos', 'color': COLORS['helipontos']},
            {'id': 'construcoes-aero', 'name': 'Construcoes Aeroportuarias', 'color': COLORS['construcoes-aero']}
        ],
        'limites': [
            {'id': 'limite-uf', 'name': 'Limite Estadual', 'color': COLORS['limite-uf']},
            {'id': 'municipios', 'name': 'Municipios', 'color': COLORS['municipios']}
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
            return jsonify({'error': 'No layers selected'}), 400
        
        # Sanitizar nome
        nome_arquivo = "".join(c for c in nome_arquivo if c.isalnum() or c in (' ', '-', '_')).strip()
        if not nome_arquivo:
            nome_arquivo = 'mapa_customizado'
        
        print("\n[GEN] Generating: {}".format(nome_arquivo))
        print("[LAYERS] {}".format(selected_layers))
        
        # Criar mapa
        nome_arquivo, html_content = criar_mapa_customizado(selected_layers, nome_arquivo)
        
        # Armazenar HTML em cache
        MAPS_CACHE[nome_arquivo] = html_content
        
        print("[GEN] Map cached with key: {}".format(nome_arquivo))
        
        # Retornar URL do mapa
        return jsonify({
            'success': True,
            'message': 'Map generated successfully!',
            'url': '/visualizar/{}'.format(nome_arquivo),
            'layers_count': len(selected_layers)
        })
    
    except Exception as e:
        print("[ERROR] {}".format(str(e)))
        return jsonify({'error': str(e)}), 500

@app.route('/visualizar/<nome_arquivo>', methods=['GET'])
def visualizar_mapa(nome_arquivo):
    """Visualiza o mapa gerado"""
    
    # Primeiro tenta buscar do cache em memória
    if nome_arquivo in MAPS_CACHE:
        print(f"[VIEW] Serving map from cache: {nome_arquivo}")
        return MAPS_CACHE[nome_arquivo]
    
    # Fallback: tenta buscar do arquivo
    html_path = TEMP_DIR / "{}.html".format(nome_arquivo)
    
    print(f"[VIEW] Cache miss, looking for file: {html_path}")
    
    if html_path.exists():
        print(f"[VIEW] Serving map from file: {html_path}")
        with open(str(html_path), 'r', encoding='utf-8') as f:
            content = f.read()
            # Adiciona ao cache para próximas requisições
            MAPS_CACHE[nome_arquivo] = content
            return content
    
    print(f"[VIEW] Map not found: {nome_arquivo}")
    return "Map not found. Please generate a map first.", 404

@app.route('/api/exportar-png', methods=['POST'])
def exportar_png():
    """Exporta mapa como PNG usando Playwright"""
    
    try:
        data = request.json
        nome_arquivo = data.get('nome', 'mapa_customizado')
        
        # Sanitizar nome
        nome_arquivo = "".join(c for c in nome_arquivo if c.isalnum() or c in (' ', '-', '_')).strip()
        if not nome_arquivo:
            nome_arquivo = 'mapa_customizado'
        
        print("\n[EXPORT] Exporting PNG: {}".format(nome_arquivo))
        
        # Procurar arquivo HTML no temp_maps
        html_filename = "{}.html".format(nome_arquivo)
        temp_path = TEMP_DIR / html_filename
        
        if not temp_path.exists():
            return jsonify({'error': 'Mapa nao encontrado. Gere o mapa primeiro!'}), 404
        
        # Criar timestamp para PNG
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        png_filename = "{}_{}.png".format(nome_arquivo, timestamp)
        png_path = OUTPUT_DIR / png_filename
        
        print("[INFO] Converting HTML to PNG...")
        
        # Usar Playwright para converter HTML em PNG
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            # Abrir arquivo HTML
            page.goto('file:///{}'.format(str(temp_path).replace('\\', '/')))
            
            # Aguardar mapa carregar completamente (espera tiles Leaflet)
            page.wait_for_timeout(3000)
            
            # Tirar screenshot
            page.screenshot(path=str(png_path), full_page=True)
            
            browser.close()
        
        print("[OK] PNG exported: {}".format(png_path))
        
        return jsonify({
            'success': True,
            'message': 'PNG exportado: {}'.format(png_filename),
            'filepath': str(png_path)
        })
    
    except Exception as e:
        print("[ERROR] {}".format(str(e)))
        import traceback
        traceback.print_exc()
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
    print("[INIT] Gerador de Mapas Customizados")
    print("=" * 60)
    print("[PATH] Shapefile dir: {}".format(SHAPEFILE_DIR))
    print("[PATH] Output dir: {}".format(OUTPUT_DIR))
    print("[PATH] Temp dir: {}".format(TEMP_DIR))
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    print("\n[WEB] Access: http://{}:{}".format(host, port))
    print("=" * 60 + "\n")
    
    # Em produção use debug=False
    app.run(debug=debug, port=port, host=host)
