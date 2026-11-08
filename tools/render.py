"""Render offscreen colorido (pyrender/EGL) para conjuntos de peças da oficina.

    from tools.render import render_conjunto
    render_conjunto([(mesh_trimesh, (r,g,b,a)), ...], "saida.png", vistas=["iso","topo",...],
                    corte=None|("x",0.0))
"""
import os

os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
import numpy as np  # noqa: E402
import pyrender  # noqa: E402
import trimesh  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

CORES = {
    "creme": (0.93, 0.89, 0.80, 1.0),
    "petroleo": (0.10, 0.42, 0.42, 1.0),
    "grafite": (0.25, 0.26, 0.28, 1.0),
    "ambar": (1.0, 0.68, 0.10, 1.0),
    "aco": (0.70, 0.72, 0.75, 1.0),
    "fantasma": (0.55, 0.65, 0.85, 0.35),
    "ptfe": (0.97, 0.97, 0.97, 1.0),
    "silicone": (0.85, 0.30, 0.30, 1.0),
}

_DIRS = {
    "iso": (1.0, -1.2, 0.9),
    "iso_tras": (-1.0, 1.4, 0.7),
    "topo": (0.0, -0.001, 1.0),
    "baixo": (0.0, 0.001, -1.0),
    "frente": (0.0, 1.0, 0.05),     # +Y = frente do robô
    "lado": (1.0, 0.0, 0.05),
    "tras": (0.0, -1.0, 0.05),
}


def _look_at(eye, alvo, up=(0, 0, 1)):
    f = np.array(alvo, float) - np.array(eye, float)
    f /= np.linalg.norm(f)
    up = np.array(up, float)
    if abs(np.dot(f, up)) > 0.99:
        up = np.array([0, 1, 0], float)
    s = np.cross(f, up); s /= np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = s, u, -f, eye
    return m


def cortar(mesh, eixo="x", pos=0.0, manter_positivo=True):
    n = {"x": [1, 0, 0], "y": [0, 1, 0], "z": [0, 0, 1]}[eixo]
    n = np.array(n, float) * (1 if manter_positivo else -1)
    o = np.zeros(3); o["xyz".index(eixo)] = pos
    try:
        return trimesh.intersections.slice_mesh_plane(mesh, n, o, cap=True)
    except Exception:
        return trimesh.intersections.slice_mesh_plane(mesh, n, o, cap=False)


def render_conjunto(itens, saida, vistas=("iso", "topo", "baixo", "lado"), titulo="",
                    corte=None, tam=(700, 560), legendas=None):
    imgs = []
    todos = trimesh.util.concatenate([m for m, _ in itens])
    centro = todos.bounds.mean(axis=0)
    raio = np.linalg.norm(todos.bounds[1] - todos.bounds[0]) / 2
    r = pyrender.OffscreenRenderer(*tam)
    for v in vistas:
        cena = pyrender.Scene(bg_color=(0.96, 0.96, 0.97, 1.0), ambient_light=(0.35, 0.35, 0.35))
        for m, cor in itens:
            mm = m
            if corte is not None:
                mm = cortar(m, *corte)
                if mm is None or len(mm.faces) == 0:
                    continue
            mat = pyrender.MetallicRoughnessMaterial(baseColorFactor=cor, metallicFactor=0.05,
                                                     roughnessFactor=0.7,
                                                     alphaMode="BLEND" if cor[3] < 1 else "OPAQUE")
            cena.add(pyrender.Mesh.from_trimesh(mm, material=mat, smooth=False))
        d = np.array(_DIRS[v], float); d /= np.linalg.norm(d)
        ortho = v in ("topo", "baixo", "frente", "lado", "tras")
        if ortho:
            cam = pyrender.OrthographicCamera(xmag=raio * 1.1, ymag=raio * 1.1 * tam[1] / tam[0], znear=1.0, zfar=raio * 20)
        else:
            cam = pyrender.PerspectiveCamera(yfov=np.radians(35), znear=1.0, zfar=raio * 20)
        dist = raio * (3.0 if not ortho else 4.0)
        pose = _look_at(centro + d * dist, centro)
        cena.add(cam, pose=pose)
        cena.add(pyrender.DirectionalLight(intensity=3.5), pose=pose)
        cena.add(pyrender.DirectionalLight(intensity=1.5), pose=_look_at(centro + np.array([0.3, 0.5, 1]) * dist, centro))
        cor_img, _ = r.render(cena, flags=pyrender.RenderFlags.RGBA)
        im = Image.fromarray(cor_img).convert("RGB")
        ImageDraw.Draw(im).text((10, 8), v + (f"  (corte {corte[0]}={corte[1]:g})" if corte else ""), fill=(30, 30, 30))
        imgs.append(im)
    r.delete()
    cols = min(len(imgs), 3)
    linhas = (len(imgs) + cols - 1) // cols
    folha = Image.new("RGB", (tam[0] * cols, tam[1] * linhas + 40), (255, 255, 255))
    for i, im in enumerate(imgs):
        folha.paste(im, ((i % cols) * tam[0], 40 + (i // cols) * tam[1]))
    dr = ImageDraw.Draw(folha)
    dr.text((12, 12), titulo, fill=(10, 60, 60))
    if legendas:
        dr.text((tam[0] * cols - 520, 12), legendas, fill=(60, 60, 60))
    folha.save(saida)
    return saida
