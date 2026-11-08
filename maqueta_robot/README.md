# Maqueta Robot Mel 1:6

Maqueta articulada (6 ejes) generada a partir del CAD original (`Robot mel/*.stl`) y la tabla DH
(d1 450, a1 75, a2 640, a3 195, d4 700, d6 75 mm).

- Escala 1:6, sin cables ni soportes de cable (imprimible en FDM).
- Cada articulación: 1 tornillo M3 cabeza avellanada (ISO 10642) + 1 tuerca autoblocante M3 (DIN 985) en ranura lateral.
- Holgura axial entre caras 0,4 mm; agujero 3,4 mm; avellanado 90° Ø6,7.

`visor_maqueta.html`: visor 3D para mover las articulaciones y auditar (abrir en el navegador).

## Regenerar
```
pip install trimesh manifold3d scipy rtree networkx
python3 generador/build.py out          # requiere el CAD en src/Robot mel/
python3 generador/sweep.py out/build.pkl
python3 generador/export_viewer.py out/build.pkl out/ranges.pkl out/data.json
```
Los STL finales se exportan una vez aprobado el diseño.
