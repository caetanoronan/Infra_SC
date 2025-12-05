"""
Compacta os shapefiles para upload externo
"""
import zipfile
from pathlib import Path

shapefile_dir = Path("bc25_sc_shapefile_2020-10-01")
output_zip = Path("bc25_sc_shapefiles.zip")

print(f"Compactando {shapefile_dir}...")

with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in shapefile_dir.rglob('*'):
        if file.is_file():
            arcname = file.relative_to(shapefile_dir.parent)
            zipf.write(file, arcname)
            print(f"  + {arcname}")

print(f"\n✓ Arquivo criado: {output_zip}")
print(f"  Tamanho: {output_zip.stat().st_size / (1024*1024):.1f} MB")
print("\nPróximo passo:")
print("1. Suba bc25_sc_shapefiles.zip para Google Drive/Dropbox")
print("2. Obtenha link público de download direto")
print("3. Configure URL no app_gerador_mapas_final.py")
