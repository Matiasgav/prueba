import sys, os, pickle, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *
from mesh2step import mesh_to_solid, write_step
from build_hw import frame
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Vec
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace

D = pickle.load(open(sys.argv[1], 'rb')); OUT = sys.argv[2]
os.makedirs(OUT + '/STL', exist_ok=True); os.makedirs(OUT + '/STEP', exist_ok=True)
NAMES = {'base': '01_base_pedestal', 'j1': '02_torreta_J1', 'j2': '03_brazo_J2', 'j3': '04_codo_J3',
         'j4': '05_antebrazo_J4', 'j5': '06_muneca_J5', 'j6': '07_brida_cabezal_J6'}
COL = {'base': (0.23, 0.26, 0.29), 'j6': (0.73, 0.75, 0.78)}
YEL = (0.94, 0.72, 0.0)

solids = {}
for n, m in D['final'].items():
    m.export(f"{OUT}/STL/{NAMES[n]}.stl")
    t = time.time(); s, ok = mesh_to_solid(m); solids[n] = s
    write_step([(NAMES[n], s, COL.get(n, YEL))], f"{OUT}/STEP/{NAMES[n]}.step")
    print(n, 'STEP valido', ok, '%.0fs' % (time.time() - t), flush=True)

def ax(O, d): return gp_Ax2(gp_Pnt(*map(float, O)), gp_Dir(*map(float, d)))

hw = []
for j in D['joints']:
    sd = np.array(j['sd']); O = np.array(j['O']); L = j['L']
    p0 = O + j['s_head'] * sd
    head = BRepPrimAPI_MakeCone(ax(p0, sd), 3.0, 1.5, 1.65).Shape()
    shank = BRepPrimAPI_MakeCylinder(ax(p0 + 1.65 * sd, sd), 1.5, L - 1.65).Shape()
    hw.append((f"Tornillo_{j['n']}_M3x{L}_ISO10642", BRepAlgoAPI_Fuse(head, shank).Shape(), (0.8, 0.81, 0.83)))
    Mn = frame(sd); c = O + (j['nut_s'] + 0.15) * sd; rc = 5.5 / np.sqrt(3); a0 = np.radians(j['slot_ang'])
    poly = BRepBuilderAPI_MakePolygon()
    for k in range(6):
        p = c + rc * (np.cos(a0 + k * np.pi / 3) * Mn[:3, 0] + np.sin(a0 + k * np.pi / 3) * Mn[:3, 1])
        poly.Add(gp_Pnt(*map(float, p)))
    poly.Close()
    face = BRepBuilderAPI_MakeFace(poly.Wire(), True).Face()
    nut = BRepPrimAPI_MakePrism(face, gp_Vec(*map(float, 4.0 * sd))).Shape()
    nut = BRepAlgoAPI_Cut(nut, BRepPrimAPI_MakeCylinder(ax(c - 0.5 * sd, sd), 1.5, 5.0).Shape()).Shape()
    hw.append((f"Tuerca_{j['n']}_M3_DIN985", nut, (0.17, 0.42, 0.69)))

write_step([(NAMES[n], solids[n], COL.get(n, YEL)) for n in solids] + hw,
           f"{OUT}/STEP/00_ensamble_maqueta_robot.step")
print('ensamble ok')
