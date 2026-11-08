# Maqueta Robot Mel 1:6

Maqueta articulada (6 ejes) generada a partir del CAD original (`Robot mel/*.stl`) y la tabla DH
(d1 450, a1 75, a2 640, a3 195, d4 700, d6 75 mm).

- Escala 1:6, sin cables ni soportes de cable (imprimible en FDM).
- Cada articulación gira sobre un encastre: saliente cilíndrico en una pieza + embocadura en la otra
  (holgura radial 0,2 mm, 0,3 mm al fondo, 0,4 mm entre caras).
- 1 tornillo M3 cabeza avellanada (ISO 10642) por eje, solo axial: pasa con holgura (Ø4,0) por la pieza que gira
  y aprieta contra una tuerca autoblocante M3 (DIN 985) alojada en ranura lateral.
- Cabezal RayTools BT220 a 90°: su brida lateral se apoya sobre la planchuela de la brida J6 y la boquilla queda hacia abajo.

`visor_maqueta.html`: visor 3D para mover las articulaciones y auditar (abrir en el navegador).

## Regenerar
```
pip install trimesh manifold3d scipy rtree networkx
python3 generador/build.py out          # requiere el CAD en src/Robot mel/
python3 generador/audit.py out/build.pkl
python3 generador/sweep.py out/build.pkl
python3 generador/export_viewer.py out/build.pkl out/ranges.pkl out/data.json
```
Los STL finales se exportan una vez aprobado el diseño.
