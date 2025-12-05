import geopandas as gpd
import folium
from pathlib import Path
import pandas as pd
import json
from shapely.geometry import Polygon, LineString, Point, MultiPolygon, MultiLineString
import numpy as np

# ==================== FUNÇÕES DE OTIMIZAÇÃO ====================

def simplificar_geometrias(gdf, tolerance=0.001):
    """Simplifica geometrias para reduzir vértices"""
    if gdf.empty or gdf.geometry.iloc[0].geom_type in ['Point', 'MultiPoint']:
        return gdf
    gdf = gdf.copy()
    gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=True)
    return gdf

def reduzir_precisao(gdf, decimals=5):
    """Arredonda coordenadas para menos casas decimais"""
    if gdf.empty:
        return gdf
    
    gdf = gdf.copy()
    
    def round_geom(geom):
        if geom.is_empty:
            return geom
            
        geom_type = geom.geom_type
        
        if geom_type == 'Polygon':
            # Arredonda coordenadas do polígono
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

def filtrar_colunas(gdf, colunas_manter):
    """Mantém apenas colunas essenciais"""
    if gdf.empty:
        return gdf
    
    colunas_existentes = [c for c in colunas_manter if c in gdf.columns]
    if colunas_existentes:
        return gdf[colunas_existentes + ['geometry']]
    return gdf[['geometry']]

# ==================== CONFIGURAÇÃO PRINCIPAL ====================

print("🚀 Iniciando otimização do mapa BC25...")

# Caminho base dos shapefiles BC25
BASE_DIR = Path(r"C:\Users\caetanoronan\OneDrive - UFSC\Área de Trabalho\Infra_SC\bc25_sc_shapefile_2020-10-01")

# --- Carregar e otimizar camadas ---
print("📥 Carregando shapefiles BC25...")

# 1. Limite estadual
uf = gpd.read_file(BASE_DIR / "lml_unidade_federacao_a.shp").to_crs("EPSG:4326")
uf = simplificar_geometrias(uf, tolerance=0.001)
uf = reduzir_precisao(uf, decimals=5)
uf = filtrar_colunas(uf, ['nome', 'sigla'])

# 2. Municípios
municipios = gpd.read_file(BASE_DIR / "lml_municipio_a.shp").to_crs("EPSG:4326")

# Calcular área e classificar porte
muni_merc = municipios.to_crs(3857)
municipios["area_km2"] = muni_merc.geometry.area / 1e6
q1, q2 = municipios["area_km2"].quantile([0.33, 0.66])

def _porte(area):
    if area <= q1:
        return "Pequeno"
    if area <= q2:
        return "Medio"
    return "Grande"

municipios["porte_area"] = municipios["area_km2"].apply(_porte)
porte_counts = municipios["porte_area"].value_counts()

# Otimizar municípios
municipios = simplificar_geometrias(municipios, tolerance=0.001)
municipios = reduzir_precisao(municipios, decimals=5)
municipios = filtrar_colunas(municipios, ['nome', 'geocodigo', 'porte_area', 'area_km2'])

# 3. Rodovias
roads = gpd.read_file(BASE_DIR / "rod_via_deslocamento_l.shp").to_crs("EPSG:4326")
roads_main = roads[roads["jurisdicao"].isin(["Federal", "Estadual/Distrital"])]
roads_fed = roads[roads["jurisdicao"] == "Federal"]
roads_est = roads[roads["jurisdicao"] == "Estadual/Distrital"]

# Otimizar rodovias
roads_fed = simplificar_geometrias(roads_fed, tolerance=0.0005)
roads_fed = reduzir_precisao(roads_fed, decimals=5)
roads_fed = filtrar_colunas(roads_fed, ['jurisdicao', 'revestimen', 'operaciona'])

roads_est = simplificar_geometrias(roads_est, tolerance=0.0005)
roads_est = reduzir_precisao(roads_est, decimals=5)
roads_est = filtrar_colunas(roads_est, ['jurisdicao', 'revestimen', 'operaciona'])

# 4. Ferrovias
ferrovias = gpd.read_file(BASE_DIR / "fer_trecho_ferroviario_l.shp").to_crs("EPSG:4326")
ferrovias = simplificar_geometrias(ferrovias, tolerance=0.0005)
ferrovias = reduzir_precisao(ferrovias, decimals=5)
ferrovias = filtrar_colunas(ferrovias, ['nome', 'tipotrecho', 'bitola', 'eletrifica'])

# 5. Pontos (menos otimização necessária)
aerodromos = gpd.read_file(BASE_DIR / "aer_pista_ponto_pouso_p.shp").to_crs("EPSG:4326")
helipontos = aerodromos[aerodromos["tipopista"].str.contains("Heliponto", case=False, na=False)]
helipontos = reduzir_precisao(helipontos, decimals=5)

construcoes_aero = gpd.read_file(BASE_DIR / "edf_edif_constr_aeroportuaria_p.shp").to_crs("EPSG:4326")
construcoes_aero = reduzir_precisao(construcoes_aero, decimals=5)

terminais = gpd.read_file(BASE_DIR / "hdv_atracadouro_terminal_p.shp").to_crs("EPSG:4326")
terminais = reduzir_precisao(terminais, decimals=5)

# 6. Outras camadas (aplicar otimização moderada)
terminais_area = gpd.read_file(BASE_DIR / "hdv_atracadouro_terminal_a.shp").to_crs("EPSG:4326")
terminais_area = simplificar_geometrias(terminais_area, tolerance=0.002)
terminais_area = reduzir_precisao(terminais_area, decimals=5)

terminais_linha = gpd.read_file(BASE_DIR / "hdv_atracadouro_terminal_l.shp").to_crs("EPSG:4326")
terminais_linha = simplificar_geometrias(terminais_linha, tolerance=0.001)
terminais_linha = reduzir_precisao(terminais_linha, decimals=5)

dutos = gpd.read_file(BASE_DIR / "dut_trecho_duto_l.shp").to_crs("EPSG:4326")
dutos = simplificar_geometrias(dutos, tolerance=0.001)
dutos = reduzir_precisao(dutos, decimals=5)

hidrovias = gpd.read_file(BASE_DIR / "hdv_trecho_hidroviario_l.shp").to_crs("EPSG:4326")
hidrovias = simplificar_geometrias(hidrovias, tolerance=0.001)
hidrovias = reduzir_precisao(hidrovias, decimals=5)

pontes = gpd.read_file(BASE_DIR / "tra_ponte_l.shp").to_crs("EPSG:4326")
pontes = simplificar_geometrias(pontes, tolerance=0.001)
pontes = reduzir_precisao(pontes, decimals=5)

tuneis = gpd.read_file(BASE_DIR / "tra_tunel_l.shp").to_crs("EPSG:4326")
tuneis = simplificar_geometrias(tuneis, tolerance=0.001)
tuneis = reduzir_precisao(tuneis, decimals=5)

viadutos = gpd.read_file(BASE_DIR / "tra_passagem_elevada_viaduto_l.shp").to_crs("EPSG:4326")
viadutos = simplificar_geometrias(viadutos, tolerance=0.001)
viadutos = reduzir_precisao(viadutos, decimals=5)

# ==================== RESUMO DA OTIMIZAÇÃO ====================
print("\n📊 RESUMO DAS CAMADAS OTIMIZADAS:")
print(f"   ✓ Limite estadual: {len(uf)} geometria(s)")
print(f"   ✓ Municípios: {len(municipios)} (Porte: {porte_counts.get('Pequeno',0)}/{porte_counts.get('Medio',0)}/{porte_counts.get('Grande',0)})")
print(f"   ✓ Rodovias Federais: {len(roads_fed)}")
print(f"   ✓ Rodovias Estaduais: {len(roads_est)}")
print(f"   ✓ Ferrovias: {len(ferrovias)}")
print(f"   ✓ Helipontos: {len(helipontos)}")
print(f"   ✓ Terminais: {len(terminais)}")
print("   ⚡ Todas as geometrias foram simplificadas e otimizadas!")

# ==================== CRIAR MAPA OTIMIZADO ====================

print("\n🗺️ Criando mapa otimizado...")

# Mapa base com configurações para melhor performance
mapa = folium.Map(
    location=[-27.5, -49.5],
    zoom_start=7,
    tiles="CartoDB positron",
    min_zoom=5,
    max_zoom=12,
    prefer_canvas=True,  # Melhor performance para muitas features
    control_scale=True,
)

# --- Interface do usuário (igual ao original) ---
ui_html = """
<div id="map-ui-container" style="font-family: Arial, sans-serif;">
    <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 1000; background: rgba(255,255,255,0.92); padding: 8px 14px; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.15); font-size: 16px; font-weight: 600; color: #1f2933; text-align: center;">
        Mapa de Infraestrutura Logística - Santa Catarina<br>
        <span style="font-size: 11px; font-weight: 500; color: #374151;">Autor: Ronan Armando Caetano · Graduado em Ciências Biológicas · Técnico em Geoprocessamento · Técnico em Saneamento</span>
    </div>
    <div style="position: fixed; top: 70px; left: 12px; z-index: 1000;">
        <div style="position: relative; width: 60px; height: 60px; border: 2px solid #333; border-radius: 50%; background: rgba(255,255,255,0.92); box-shadow: 0 2px 6px rgba(0,0,0,0.15); display: flex; align-items: center; justify-content: center; font-weight: 700; color: #333;">
            N
            <div style="position: absolute; top: 6px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 7px solid transparent; border-right: 7px solid transparent; border-bottom: 14px solid #d62728;"></div>
        </div>
    </div>
    <div style="position: fixed; bottom: 12px; left: 12px; z-index: 1000; max-width: 340px; font-size: 13px;">
        <div id="info-toggle" style="cursor: pointer; background: #ffffff; color: #1f2933; padding: 8px 10px; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.15); display: inline-flex; align-items: center; gap: 6px; font-weight: 600;">
            <span>ℹ️</span><span>Informacoes das camadas</span>
        </div>
        <div id="info-panel" style="display: none; margin-top: 8px; background: rgba(255,255,255,0.96); color: #1f2933; padding: 10px 12px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); line-height: 1.5; font-size: 12px;">
            <div style="font-weight: 700; margin-bottom: 6px; color: #0f172a;">📋 Legenda/Descrição:</div>
            <div style="margin-bottom: 2px;">• Rodovias federais/estaduais separadas em camadas.</div>
            <div style="margin-bottom: 2px;">• Ferrovias, hidrovias e dutos como linhas dedicadas.</div>
            <div style="margin-bottom: 2px;">• Helipontos e construções aeroportuárias (terminais, hangares) como pontos.</div>
            <div style="margin-bottom: 2px;">• Limites municipais (porte por área) em camada dedicada; limite estadual sempre visível.</div>
            <div style="margin-bottom: 6px;">• Pontes, túneis e viadutos como camadas independentes.</div>
            <div style="font-weight: 700; color: #1e40af;">👆 Use o controle de camadas (canto superior direito) para alternar a visibilidade.</div>
        </div>
    </div>
</div>
<script>
(function(){
    const infoToggle = document.getElementById('info-toggle');
    const infoPanel = document.getElementById('info-panel');
    if (infoToggle && infoPanel) {
        infoToggle.addEventListener('click', function(){
            infoPanel.style.display = infoPanel.style.display === 'none' ? 'block' : 'none';
        });
    }
})();
</script>
"""
mapa.get_root().html.add_child(folium.Element(ui_html))

# --- Adicionar camadas otimizadas ---

# 1. Limite estadual (sempre visível)
folium.GeoJson(
    uf,
    name="🧭 Limite Estadual SC",
    style_function=lambda x: {"color": "#000000", "weight": 2.5, "fillOpacity": 0},
    smooth_factor=1.0,  # Reduz processamento
).add_to(mapa)

# 2. Municípios
folium.GeoJson(
    municipios,
    name="🗺️ Limites Municipais (Porte)",
    style_function=lambda x: {
        "color": {"Pequeno": "#e5f5f9", "Medio": "#99d8c9", "Grande": "#2ca25f"}
                .get(x["properties"].get("porte_area"), "#666666"),
        "fillColor": {"Pequeno": "#e5f5f9", "Medio": "#99d8c9", "Grande": "#2ca25f"}
                    .get(x["properties"].get("porte_area"), "#f0f0f0"),
        "weight": 1.0,
        "fillOpacity": 0.15,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["nome", "porte_area", "area_km2"],
        aliases=["Município", "Porte", "Área (km²)"],
        sticky=True,
    ),
    smooth_factor=1.0,
    show=False,
).add_to(mapa)

# 3. Rodovias Federais
folium.GeoJson(
    roads_fed,
    name="🟥 Rodovias Federais",
    style_function=lambda x: {"color": "#d73027", "weight": 2.0, "opacity": 0.9},
    tooltip=folium.GeoJsonTooltip(
        fields=["jurisdicao", "revestimen", "operaciona"],
        aliases=["Jurisdição", "Revestimento", "Status"],
    ),
    smooth_factor=1.0,
    show=False,
).add_to(mapa)

# 4. Rodovias Estaduais
folium.GeoJson(
    roads_est,
    name="🟦 Rodovias Estaduais",
    style_function=lambda x: {"color": "#4575b4", "weight": 1.8, "opacity": 0.85},
    tooltip=folium.GeoJsonTooltip(
        fields=["jurisdicao", "revestimen", "operaciona"],
        aliases=["Jurisdição", "Revestimento", "Status"],
    ),
    smooth_factor=1.0,
    show=False,
).add_to(mapa)

# 5. Ferrovias
folium.GeoJson(
    ferrovias,
    name="🚂 Ferrovias",
    style_function=lambda x: {"color": "#7b3294", "weight": 2.2, "opacity": 0.9},
    tooltip=folium.GeoJsonTooltip(
        fields=["nome", "tipotrecho", "bitola"],
        aliases=["Nome", "Tipo", "Bitola"],
    ),
    smooth_factor=1.0,
    show=False,
).add_to(mapa)

# 6. Pontos (helipontos, construções, terminais) - modo simplificado
def adicionar_pontos_simplificado(gdf, nome, cor, icon):
    """Adiciona pontos de forma otimizada"""
    if len(gdf) == 0:
        return
    
    fg = folium.FeatureGroup(name=icon + " " + nome, show=False)
    
    for _, row in gdf.iterrows():
        nome_feat = row.get('nome', nome)
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=4,
            color=cor,
            fill=True,
            fill_opacity=0.7,
            tooltip=nome_feat,
            popup=folium.Popup(f"<b>{nome_feat}</b>", max_width=200),
        ).add_to(fg)
    
    fg.add_to(mapa)

# Adicionar pontos otimizados
adicionar_pontos_simplificado(helipontos, "Helipontos", "#f46d43", "🚁")
adicionar_pontos_simplificado(construcoes_aero, "Construções Aeroportuárias", "#3288bd", "🏢")
adicionar_pontos_simplificado(terminais, "Terminais Portuários", "#e41a1c", "⚓")

# 7. Outras camadas (modo simplificado)
camadas_simples = [
    (dutos, "⛽ Dutos", "#a6611a", 2.0),
    (hidrovias, "🛳️ Hidrovias", "#2c7fb8", 2.5),
    (pontes, "🌉 Pontes", "#8073ac", 1.8),
    (tuneis, "🚇 Túneis", "#e08214", 2.0),
    (viadutos, "🛤️ Viadutos", "#d01c8b", 2.0),
]

for gdf, nome, cor, peso in camadas_simples:
    if len(gdf) > 0:
        folium.GeoJson(
            gdf,
            name=nome,
            style_function=lambda x, c=cor, w=peso: {"color": c, "weight": w, "opacity": 0.85},
            smooth_factor=1.0,
            show=False,
        ).add_to(mapa)

# Controle de camadas
folium.LayerControl(position="topright", collapsed=False).add_to(mapa)

# ==================== SALVAR MAPA ====================

output = "mapa_infraestrutura_bc25_sc.html"
mapa.save(output)

# Verificar tamanho do arquivo
tamanho_mb = Path(output).stat().st_size / (1024 * 1024)
print(f"\n✅ Mapa otimizado gerado: {output}")
print(f"📏 Tamanho do arquivo: {tamanho_mb:.1f} MB")

if tamanho_mb > 95:
    print("⚠️  Aviso: Arquivo ainda grande para GitHub Pages (>95MB)")
    print("💡 Dica: Tente aumentar a tolerância (tolerance=0.002) nas geometrias")
else:
    print("🎉 Perfeito! Arquivo dentro do limite do GitHub Pages (<100MB)")

print("\n📌 Próximos passos:")
print("1. Abra o arquivo HTML no navegador para testar")
print("2. Se necessário, ajuste as tolerâncias na linha 71-73")
print("3. Faça upload para o GitHub Pages")
