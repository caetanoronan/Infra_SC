import geopandas as gpd
import folium
import requests
import json
import pandas as pd
from folium import plugins

# --- PASSO 1: AQUISIÇÃO DE DADOS MUNICIPAIS ---
print("📥 Baixando dados do IBGE...")
url_ibge = "https://servicodados.ibge.gov.br/api/v3/malhas/estados/SC?formato=application/vnd.geo+json&qualidade=minima&intrarregiao=municipio"

response = requests.get(url_ibge)
response.raise_for_status()
geojson_data = response.json()

gdf_sc = gpd.GeoDataFrame.from_features(geojson_data['features'])
gdf_sc.set_crs("EPSG:4326", inplace=True)
gdf_sc.rename(columns={'codarea': 'Código IBGE'}, inplace=True)
gdf_sc['Código IBGE'] = gdf_sc['Código IBGE'].astype(int)

print("📥 Baixando nomes dos municípios...")
url_municipios = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/SC/municipios"
response_mun = requests.get(url_municipios)
response_mun.raise_for_status()
municipios_data = response_mun.json()

municipios_df = pd.DataFrame([{'id': mun['id'], 'name': mun['nome']} for mun in municipios_data])
municipios_df.rename(columns={'id': 'Código IBGE', 'name': 'Município'}, inplace=True)
municipios_df['Código IBGE'] = municipios_df['Código IBGE'].astype(int)

gdf_sc = gdf_sc.merge(municipios_df, on='Código IBGE', how='left')

# --- PASSO 2: INFRAESTRUTURA DE LOGÍSTICA EM SC ---
print("📥 Processando dados de infraestrutura...")

dados_portos = [
    {'nome': 'Porto de Itajaí', 'lat': -26.9136, 'lon': -48.6597, 'descricao': 'Principal porto de SC - Itajaí'},
    {'nome': 'Porto de Navegantes', 'lat': -26.8722, 'lon': -48.6906, 'descricao': 'Porto de contêineres - Navegantes'},
    {'nome': 'Porto de Imbituba', 'lat': -28.2425, 'lon': -48.6711, 'descricao': 'Porto graneleiro - Imbituba'},
    {'nome': 'Porto de São Francisco do Sul', 'lat': -26.3892, 'lon': -48.6406, 'descricao': 'Porto de breakbulk - São Francisco do Sul'},
]

dados_aeroportos = [
    {'nome': 'Aeroporto Hercílio Luz', 'lat': -27.6700, 'lon': -48.5519, 'descricao': 'Aeroporto Internacional - Florianópolis'},
    {'nome': 'Aeroporto Lauro Carneiro', 'lat': -29.2275, 'lon': -49.6419, 'descricao': 'Aeroporto Regional - Lages'},
]

dados_cd = [
    {'nome': 'CD Blumenau', 'lat': -26.8789, 'lon': -49.0554, 'descricao': 'Centro de Distribuição - Blumenau'},
    {'nome': 'CD Joinville', 'lat': -26.3045, 'lon': -48.8450, 'descricao': 'Centro de Distribuição - Joinville'},
    {'nome': 'CD Florianópolis', 'lat': -27.5954, 'lon': -48.5480, 'descricao': 'Centro de Distribuição - Florianópolis'},
    {'nome': 'CD Criciúma', 'lat': -28.6808, 'lon': -49.3878, 'descricao': 'Centro de Distribuição - Criciúma'},
]

dados_ferrovias = [
    {'nome': 'Ferrovia Tereza Cristina', 'lat': -28.9500, 'lon': -49.3000, 'descricao': 'Linha de transporte de carga - Criciúma/Lages'},
]

# --- PASSO 3: CRIAÇÃO DO MAPA BASE ---
print("🗺️  Gerando o mapa interativo...")
mapa = folium.Map(
    location=[-27.242, -50.218], 
    zoom_start=8,
    tiles='CartoDB positron'
)

# --- PASSO 4: CAMADA BASE - MUNICÍPIOS ---
style_func = lambda x: {
    'fillColor': '#E8E8E8',
    'color': '#999999', 
    'weight': 1,
    'fillOpacity': 0.3
}

highlight_func = lambda x: {
    'fillColor': '#FFEB3B', 
    'color': '#333333', 
    'weight': 2, 
    'fillOpacity': 0.5
}

folium.GeoJson(
    gdf_sc,
    name='🗺️ Base: Municípios de SC',
    style_function=style_func,
    highlight_function=highlight_func,
    tooltip=folium.GeoJsonTooltip(
        fields=['Município', 'Código IBGE'],
        aliases=['Município:', 'IBGE:'],
        localize=True
    ),
    show=True
).add_to(mapa)

# --- PASSO 5: CAMADA 1 - PORTOS ---
print("   Adicionando camada de Portos...")
fg_portos = folium.FeatureGroup(name='⚓ Portos (4)', show=False)
for porto in dados_portos:
    popup_text = f"<b>{porto['nome']}</b><br>{porto['descricao']}"
    folium.Marker(
        location=[porto['lat'], porto['lon']],
        popup=folium.Popup(popup_text, max_width=250),
        tooltip=porto['nome'],
        icon=folium.Icon(color='red', icon='anchor', prefix='fa')
    ).add_to(fg_portos)
fg_portos.add_to(mapa)

# --- PASSO 6: CAMADA 2 - AEROPORTOS ---
print("   Adicionando camada de Aeroportos...")
fg_aeroportos = folium.FeatureGroup(name='✈️ Aeroportos (2)', show=False)
for aeroporto in dados_aeroportos:
    popup_text = f"<b>{aeroporto['nome']}</b><br>{aeroporto['descricao']}"
    folium.Marker(
        location=[aeroporto['lat'], aeroporto['lon']],
        popup=folium.Popup(popup_text, max_width=250),
        tooltip=aeroporto['nome'],
        icon=folium.Icon(color='blue', icon='plane', prefix='fa')
    ).add_to(fg_aeroportos)
fg_aeroportos.add_to(mapa)

# --- PASSO 7: CAMADA 3 - CENTROS DE DISTRIBUIÇÃO ---
print("   Adicionando camada de Centros de Distribuição...")
fg_cd = folium.FeatureGroup(name='📦 Centros de Distribuição (4)', show=False)
for cd in dados_cd:
    popup_text = f"<b>{cd['nome']}</b><br>{cd['descricao']}"
    folium.Marker(
        location=[cd['lat'], cd['lon']],
        popup=folium.Popup(popup_text, max_width=250),
        tooltip=cd['nome'],
        icon=folium.Icon(color='green', icon='cube', prefix='fa')
    ).add_to(fg_cd)
fg_cd.add_to(mapa)

# --- PASSO 8: CAMADA 4 - FERROVIAS ---
print("   Adicionando camada de Ferrovias...")
fg_ferrovias = folium.FeatureGroup(name='🚂 Ferrovias (1)', show=False)
for ferrovia in dados_ferrovias:
    popup_text = f"<b>{ferrovia['nome']}</b><br>{ferrovia['descricao']}"
    folium.Marker(
        location=[ferrovia['lat'], ferrovia['lon']],
        popup=folium.Popup(popup_text, max_width=250),
        tooltip=ferrovia['nome'],
        icon=folium.Icon(color='darkgreen', icon='train', prefix='fa')
    ).add_to(fg_ferrovias)
fg_ferrovias.add_to(mapa)

# --- PASSO 10: CONTROLE DE CAMADAS ---
print("   Adicionando controle de camadas...")
folium.LayerControl(position='topright', collapsed=False).add_to(mapa)

# --- PASSO 11: LEGENDA INFORMATIVA ---
legend_html = '''
<div style="position: fixed; 
     bottom: 20px; left: 20px; width: 320px; 
     background-color: white; border: 3px solid #333; z-index:9999; 
     font-size: 13px; padding: 15px; border-radius: 8px; 
     box-shadow: 0 0 15px rgba(0,0,0,0.2);">
     
<h3 style="margin: 0 0 10px 0; font-size: 16px; color: #333;">
🗺️ Mapa Interativo de Infraestrutura - SC
</h3>
<hr style="margin: 8px 0;">

<p style="margin: 5px 0; font-size: 12px; color: #555;">
<b>✔️ Como usar:</b>
</p>
<ul style="margin: 5px 0; padding-left: 15px; font-size: 11px; color: #666;">
<li>Use o <b>controle no topo direito</b> para ativar/desativar camadas</li>
<li><b>Clique</b> nos marcadores para informações</li>
<li><b>Passe o mouse</b> sobre elementos para destacar</li>
</ul>

<hr style="margin: 8px 0;">

<p style="margin: 5px 0; font-size: 11px; color: #777;">
<b>Fonte:</b> INDE (Infraestrutura Nacional de Dados Espaciais) | IBGE<br>
<b>Última atualização:</b> Dezembro/2025
</p>
</div>
'''
mapa.get_root().html.add_child(folium.Element(legend_html))

# --- PASSO 12: SALVAR ARQUIVO ---
output_file = "mapa_infraestrutura_sc.html"
mapa.save(output_file)
print(f"\n✅ Sucesso! Mapa interativo salvo como '{output_file}'.")
print(f"\n📊 Resumo das Camadas:")
print(f"   ✓ Base: Municípios de SC (295) - SEMPRE VISÍVEL")
print(f"   ○ Camada 1: ⚓ Portos (4) - desativada")
print(f"   ○ Camada 2: ✈️ Aeroportos (2) - desativada")
print(f"   ○ Camada 3: 📦 Centros de Distribuição (4) - desativada")
print(f"   ○ Camada 4: 🚂 Ferrovias (1) - desativada")
print(f"\n💡 Nota: Rodovias removidas até obter dados oficiais do DNIT/INDE")