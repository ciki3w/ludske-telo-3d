"""Zostaví webový balík modelu ľudského tela z BodyParts3D (CC BY-SA 2.1 JP).
Použitie: python build_model.py <bp3d_dir> <out_dir> [--dry]
"""
import sys, os, re, json, collections, struct
import numpy as np

BP = sys.argv[1]; OUT = sys.argv[2]; DRY = '--dry' in sys.argv

EXV = r'arter|vein|venous|nerve|branch|plexus|vascular'
# (id, include regex, exclude regex, budget trojuholníkov, farba)
DEFS = [
 ('koza',        r'^skin$', None, 110000, '#e7b494'),
 # kostra
 ('zuby',        r'^tooth$', None, 16000, '#f6f3e8'),
 ('sanka',       r'^mandible$', None, 14000, '#ece2c6'),
 ('lebka',       r'^skull$', None, 55000, '#ece2c6'),
 ('chrbtica',    r'^vertebral column$|^sacrum$|^coccyx$', None, 45000, '#ece2c6'),
 ('hrudnik',     r'^rib cage$|^sternum$', None, 40000, '#ece2c6'),
 ('klucna',      r'^clavicle$', None, 4000, '#ece2c6'),
 ('lopatka',     r'^scapula$', None, 10000, '#ece2c6'),
 ('ramenna',     r'^humerus$|^(left|right) humerus$', None, 8000, '#ece2c6'),
 ('predlaktie',  r'^(radius|ulna)$|^(left|right) (radius|ulna)$', None, 8000, '#ece2c6'),
 ('ruka_kosti',  r'^carpal bone$|^metacarpal bone$|phalanx of .*(finger|thumb)|^skeleton of (left|right) hand proper$', None, 16000, '#ece2c6'),
 ('panva',       r'^hip bone$|^pelvis$|^bony pelvis$', None, 14000, '#ece2c6'),
 ('stehenna',    r'^femur$|^(left|right) femur$', None, 8000, '#ece2c6'),
 ('jablcko',     r'^patella$', None, 2000, '#ece2c6'),
 ('predkolenie', r'^(tibia|fibula)$|^(left|right) (tibia|fibula)$', None, 8000, '#ece2c6'),
 ('noha_kosti',  r'^(calcaneus|talus|navicular bone|cuboid bone|.*cuneiform bone|metatarsal bone|tarsal bone)$|phalanx of .*toe', None, 18000, '#ece2c6'),
 # svaly
 ('prsny',       r'pectoralis major', EXV, 8000, '#b8413a'),
 ('deltovy',     r'deltoid', EXV, 8000, '#b8413a'),
 ('biceps',      r'biceps brachii', EXV, 6000, '#b8413a'),
 ('triceps',     r'triceps brachii', EXV, 8000, '#b8413a'),
 ('predlaktie_svaly', r'^muscle of forearm$', EXV, 20000, '#b8413a'),
 ('brusne',      r'external oblique|internal oblique|transversus abdominis|rectus abdominis', EXV, 16000, '#b8413a'),
 ('trapezovy',   r'trapezius', EXV, 8000, '#b8413a'),
 ('pilovity',    r'serratus anterior', EXV, 10000, '#b8413a'),
 ('sedaci',      r'gluteus (maximus|medius|minimus)', EXV, 8000, '#b8413a'),
 ('stvorhlavy',  r'rectus femoris|vastus (lateralis|medialis|intermedius)|quadriceps femoris', EXV, 14000, '#b8413a'),
 ('krajciarsky', r'sartorius', EXV, 4000, '#b8413a'),
 ('zadne_stehno',r'biceps femoris|semitendinosus|semimembranosus', EXV, 10000, '#b8413a'),
 ('lytkovy',     r'gastrocnemius|soleus|calcaneal tendon', EXV, 10000, '#b8413a'),
 ('predny_pistalovy', r'tibialis anterior', EXV, 4000, '#b8413a'),
 ('kyvac',       r'sternocleidomastoid', EXV, 4000, '#b8413a'),
 ('medzirebrove',r'^external intercostal muscle$', EXV, 16000, '#b8413a'),
 # tráviaca
 ('jazyk',       r'^tongue$|muscle of tongue', EXV, 5000, '#e07f86'),
 ('hltan',       r'^pharynx$|muscle of pharynx', EXV, 8000, '#d97a7a'),
 ('pazerak',     r'^esophagus$', EXV, 4000, '#d98479'),
 ('zaludok',     r'^stomach$', EXV, 6000, '#e0957f'),
 ('zlcnik',      r'^gallbladder$', EXV, 2000, '#5c8a3a'),
 ('pecen',       r'^liver$', EXV, 24000, '#7b2b22'),
 ('pankreas',    r'^pancreas$', EXV, 6000, '#e9c27a'),
 ('tenke',       r'^small intestine$|^duodenum$|^jejunum$|^ileum$', EXV, 30000, '#e8a291'),
 ('hrube',       r'^large intestine$|^cecum$|^appendix$|colon$|^rectum$|anal canal', EXV, 16000, '#c98a78'),
 # dýchacia
 ('hrtan',       r'^larynx$|thyroid cartilage|cricoid cartilage|arytenoid|epiglottis|cartilage of larynx|intrinsic muscle of larynx|ligament of larynx', None, 10000, '#e2cbb8'),
 ('priedusnica', r'^trachea$|^tracheobronchial tree$', None, 24000, '#f0d0c8'),
 ('plucne_cievy',r'^pulmonary vascular system$', None, 20000, '#7a6cc9'),
 ('pluca',       'GEN_LUNG', None, 14000, '#f2a2ad'),
 ('branica',     r'^diaphragm$', None, 10000, '#b8574d'),
 # obehová
 ('srdce',       r'^heart$', None, 30000, '#a8222e'),
 ('aorta',       r'^aorta$', None, 8000, '#e0303a'),
 ('dute_zily',   r'^(superior|inferior) vena cava$', None, 4000, '#3053c0'),
 ('slezina',     r'^spleen$', None, 3000, '#7a3456'),
 # hormonálna (pred mozgom/hrtanom kvôli prioritám)
 ('hypofyza',    r'^pituitary gland$', None, 2000, '#ec8f58'),
 ('tymus',       r'^thymus$|lobe of thymus', None, 3000, '#cfa0a5'),
 ('nadoblicky',  r'adrenal gland|suprarenal gland', EXV, 3000, '#e0aa38'),
 # nervová
 ('mozocek',     r'^cerebellum$', None, 20000, '#d9918a'),
 ('kmen',        r'^brainstem$', None, 12000, '#e3b2a2'),
 ('mozog_celovy',    r'^(left|right) frontal lobe$', None, 40000, '#e89a9a'),
 ('mozog_temenny',   r'^(left|right) parietal lobe$', None, 40000, '#e6c58c'),
 ('mozog_spankovy',  r'^(left|right) temporal lobe$|^(left|right) insula$', None, 30000, '#93c1e6'),
 ('mozog_zahlavovy', r'^(left|right) occipital lobe$', None, 12000, '#a6d495'),
 ('komory',          r'lateral ventricle|third ventricle|fourth ventricle|cerebral aqueduct', None, 12000, '#7fd3e8'),
 ('limbicky',        r'^(left|right) limbic lobe$|cingulate gyrus|hippocampus|^diencephalon$|hypothalamus|pineal body|habenula|tuber cinereum', r'white matter|capsule', 14000, '#c79ad6'),
 ('miecha',      r'^spinal cord$', None, 4000, '#f5d77a'),
 # zmysly
 ('oko',         r'^(left|right) eyeball$|extra-ocular muscle', None, 16000, '#f4f2ec'),
 ('ucho',        r'^external ear$|auditory ossicle|cochlea|labyrinth|tympanic membrane', None, 8000, '#e3a689'),
 ('nervy',       r'^nerve$|cranial nerve|optic nerve|spinal nerve', None, 12000, '#f1c94a'),
 # vylučovacia
 ('oblicky',     r'^kidney$|^(left|right) kidney$', EXV, 6000, '#8c2f2c'),
 ('mocovody',    r'^ureter$|^urethra$', None, 3000, '#d8b84e'),
 ('mechur',      r'^urinary bladder$', None, 3000, '#d6b247'),
 # cievy nakoniec (zvyšok)
 ('tepny',       r'^systemic arterial tree$', None, 60000, '#d8323c'),
 ('zily',        r'^vein$', r'pulmonary', 60000, '#3557c4'),
]

# --- načítanie mapovania koncept -> elementy
el = collections.defaultdict(set)
for fn in ['partof_element_parts.txt', 'isa_element_parts.txt']:
    for line in open(os.path.join(BP, fn), encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) >= 3 and p[2].startswith('FJ'): el[p[1]].add(p[2])
path = {}
for sub in ['partof_BP3D_4.0_obj_99', 'isa_BP3D_4.0_obj_99']:
    d = os.path.join(BP, 'ex', sub)
    for f in os.listdir(d): path.setdefault(f[:-4], os.path.join(d, f))

claimed = {}
plan = []
for oid, inc, exc, budget, color in DEFS:
    ri = re.compile(inc, re.I); re_ = re.compile(exc, re.I) if exc else None
    if inc == 'GEN_LUNG': plan.append((oid, ['(generované)'], [], budget, color)); continue
    names = [n for n in el if ri.search(n) and not (re_ and re_.search(n))]
    files = set()
    for n in names: files |= el[n]
    files = sorted(f for f in files if f in path and f not in claimed)
    for f in files: claimed[f] = oid
    plan.append((oid, names, files, budget, color))

def load_obj(p):
    V = []; F = []
    with open(p, encoding='utf-8', errors='ignore') as fh:
        for line in fh:
            if line.startswith('v '):
                a = line.split(); V.append((float(a[1]), float(a[2]), float(a[3])))
            elif line.startswith('f '):
                a = line.split()[1:]
                idx = [int(t.split('/')[0]) - 1 for t in a]
                for k in range(1, len(idx) - 1): F.append((idx[0], idx[k], idx[k+1]))
    return np.array(V, np.float64), np.array(F, np.int64)

def tri_count(p):
    n = 0
    with open(p, encoding='utf-8', errors='ignore') as fh:
        for line in fh:
            if line.startswith('f '): n += 1
    return n

if DRY:
    tot = 0
    for oid, names, files, budget, color in plan:
        t = sum(tri_count(path[f]) for f in files)
        tot += min(t, budget)
        print(f"{oid:18s} files={len(files):4d} tris={t:8d} -> {min(t,budget):7d}  | {', '.join(sorted(names)[:5])}{' …' if len(names)>5 else ''}")
    print('TOTAL after budget', tot)
    sys.exit()

import fast_simplification
os.makedirs(OUT, exist_ok=True)
meshes = []
allmin = np.array([1e9]*3); allmax = -allmin
def lung_surface(side):
    from scipy import ndimage
    from skimage.measure import marching_cubes
    fs = set()
    for n in el:
        if re.search(rf'^{side} bronchial tree$', n): fs |= el[n]
    from scipy.spatial import Delaunay
    sg = 1 if side == 'left' else -1
    pts = np.vstack([load_obj(path[f])[0] for f in fs if f in path])
    pts = pts[sg*pts[:, 0] > 28]                       # bez hlavných priedušiek pri strednej čiare
    vox = 3.0; lo = pts.min(0) - 40; dims = np.ceil((pts.max(0) + 40 - lo) / vox).astype(int) + 1
    grid = np.stack(np.meshgrid(*[lo[k] + np.arange(dims[k])*vox for k in range(3)], indexing='ij'), -1).reshape(-1, 3)
    g = (Delaunay(pts).find_simplex(grid) >= 0).reshape(dims)
    g = ndimage.binary_dilation(g, iterations=4)       # pľúcne tkanivo presahuje koncové priedušky
    # vyrežeme srdce (konvexný obal + rezerva) a stredné priestorie
    hf = set(); [hf.update(el[n]) for n in el if n == 'heart']
    hp = np.vstack([load_obj(path[f])[0] for f in hf if f in path])
    hm = (Delaunay(hp).find_simplex(grid) >= 0).reshape(dims)
    hm = ndimage.binary_dilation(hm, iterations=3)
    g &= ~hm
    g &= (sg*grid[:, 0] > 12).reshape(dims)
    f = ndimage.gaussian_filter(g.astype(np.float32), 1.5)
    V, F, _, _ = marching_cubes(f, 0.5, spacing=(vox, vox, vox))
    return V + lo, F[:, ::-1].astype(np.int64)

for oid, names, files, budget, color in plan:
    Vs = []; Fs = []; off = 0
    if names == ['(generované)']:
        for side in ('left', 'right'):
            V, F = lung_surface(side); Vs.append(V); Fs.append(F + off); off += len(V)
    for f in files if names != ['(generované)'] else []:
        V, F = load_obj(path[f])
        if len(F) == 0: continue
        Vs.append(V); Fs.append(F + off); off += len(V)
    if not Vs: print('EMPTY', oid); continue
    V = np.vstack(Vs); F = np.vstack(Fs)
    # mm -> m, osi: X = x, Y = z, Z = -y
    V = np.stack([V[:,0], V[:,2], -V[:,1]], 1) / 1000.0
    if len(F) > budget:
        V, F = fast_simplification.simplify(V.astype(np.float32), F.astype(np.int32), target_reduction=1 - budget/len(F))
    meshes.append((oid, color, V.astype(np.float64), F.astype(np.int64)))
    allmin = np.minimum(allmin, V.min(0)); allmax = np.maximum(allmax, V.max(0))
    print(f"{oid:18s} tris={len(F):7d} verts={len(V):7d}")

# posun: chodidlá na y=0, stred x/z na 0 podľa kože
skin = [m for m in meshes if m[0] == 'koza'][0][2]
shift = np.array([-(skin[:,0].min()+skin[:,0].max())/2, -skin[:,1].min(), -(skin[:,2].min()+skin[:,2].max())/2])
blob = bytearray(); manifest = []
for oid, color, V, F in meshes:
    V = V + shift
    lo = V.min(0); hi = V.max(0); sc = np.maximum(hi - lo, 1e-6)
    q = np.round((V - lo) / sc * 65535).astype(np.uint16)
    ent = { 'id':oid, 'color':color, 'min':lo.round(6).tolist(), 'size':sc.round(6).tolist(), 'nv':len(V), 'nf':len(F) }
    while len(blob) % 4: blob.append(0)
    ent['pos'] = len(blob); blob += q.tobytes()
    while len(blob) % 4: blob.append(0)
    big = len(V) > 65535
    ent['idx'] = len(blob); ent['i32'] = big
    blob += F.astype(np.uint32 if big else np.uint16).tobytes()
    manifest.append(ent)
open(os.path.join(OUT, 'telo.bin'), 'wb').write(blob)
json.dump({'meshes':manifest, 'license':'BodyParts3D, (c) The Database Center for Life Science licensed under CC Attribution-Share Alike 2.1 Japan'},
          open(os.path.join(OUT, 'telo.json'), 'w'), separators=(',', ':'))
print('bin MB', len(blob)/1e6, 'shift', shift)
