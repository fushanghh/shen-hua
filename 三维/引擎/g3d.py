# 铜辉三维：VTK 离屏 PBR 渲染 + PIL 合成 的代码三维动画引擎（2026-10-30 新建）
import math, numpy as np, vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy

W, H = 1920, 1080

# ---------- 网格工具 ----------
def poly_from(pts, tris):
    pd = vtk.vtkPolyData()
    p = vtk.vtkPoints(); p.SetData(numpy_to_vtk(np.ascontiguousarray(pts, dtype=np.float64), deep=1)); pd.SetPoints(p)
    tris = np.asarray(tris, dtype=np.int64)
    cells = np.hstack([np.full((len(tris), 1), 3, dtype=np.int64), tris]).ravel()
    ca = vtk.vtkCellArray(); ca.SetCells(len(tris), numpy_to_vtkIdTypeArray(cells, deep=1)); pd.SetPolys(ca)
    return pd

def normals(pd, angle=35, split=True):
    n = vtk.vtkPolyDataNormals(); n.SetInputData(pd); n.SetFeatureAngle(angle); n.SetSplitting(split)
    n.ConsistencyOn(); n.AutoOrientNormalsOff(); n.ComputePointNormalsOn(); n.Update(); return n.GetOutput()

def ring_solid(rin, rout, z0, z1, n=256):
    """rin/rout: 角度->半径 函数（或常数）。返回带厚度的环形实体（齿轮、方板开圆孔等）"""
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ri = np.array([rin(t) if callable(rin) else rin for t in th]); ro = np.array([rout(t) if callable(rout) else rout for t in th])
    c, s = np.cos(th), np.sin(th)
    P = []
    for z in (z0, z1):
        P.append(np.c_[ri * c, ri * s, np.full(n, z)]); P.append(np.c_[ro * c, ro * s, np.full(n, z)])
    pts = np.vstack(P)  # 0:in_bot 1:out_bot 2:in_top 3:out_top
    T = []
    for i in range(n):
        j = (i + 1) % n
        ib, ob, it, ot = i, n + i, 2 * n + i, 3 * n + i
        ib2, ob2, it2, ot2 = j, n + j, 2 * n + j, 3 * n + j
        T += [[it, ot, ot2], [it, ot2, it2]]          # 顶
        T += [[ib, ob2, ob], [ib, ib2, ob2]]          # 底
        T += [[ob, ob2, ot2], [ob, ot2, ot]]          # 外壁
        if ri[i] > 1e-6: T += [[ib, it, it2], [ib, it2, ib2]]  # 内壁
    return normals(poly_from(pts, T), 30)

def gear(R, teeth, depth, z0, z1, hole=0.0, n_per=8):
    def ro(t):
        u = (t * teeth / (2 * np.pi)) % 1.0
        # 梯形齿
        if u < 0.15: f = u / 0.15
        elif u < 0.45: f = 1.0
        elif u < 0.6: f = 1 - (u - 0.45) / 0.15
        else: f = 0.0
        return R - depth + depth * f
    return ring_solid(hole if hole > 0 else 1e-7, ro, z0, z1, teeth * n_per)

def torus(R, r, nu=160, nv=24):
    s = vtk.vtkParametricTorus(); s.SetRingRadius(R); s.SetCrossSectionRadius(r)
    f = vtk.vtkParametricFunctionSource(); f.SetParametricFunction(s); f.SetUResolution(nu); f.SetVResolution(nv); f.Update()
    return f.GetOutput()

def sphere(r, res=64):
    s = vtk.vtkSphereSource(); s.SetRadius(r); s.SetThetaResolution(res); s.SetPhiResolution(res // 2 + 1); s.Update(); return s.GetOutput()

def cyl(r, h, res=48, cap=True):
    """沿 z 轴、底在 z=0 的圆柱"""
    c = vtk.vtkCylinderSource(); c.SetRadius(r); c.SetHeight(h); c.SetResolution(res); c.SetCapping(cap); c.Update()
    t = vtk.vtkTransform(); t.Translate(0, 0, h / 2); t.RotateX(90)
    return xform(c.GetOutput(), t)

def cone(r0, r1, h, res=48):
    th = np.linspace(0, 2 * np.pi, res, endpoint=False)
    pts = np.vstack([np.c_[r0 * np.cos(th), r0 * np.sin(th), np.zeros(res)], np.c_[r1 * np.cos(th), r1 * np.sin(th), np.full(res, h)], [[0, 0, 0], [0, 0, h]]])
    T = []
    for i in range(res):
        j = (i + 1) % res
        T += [[i, j, res + j], [i, res + j, res + i], [2 * res, j, i], [2 * res + 1, res + i, res + j]]
    return normals(poly_from(pts, T), 50)

def box(x0, x1, y0, y1, z0, z1):
    b = vtk.vtkCubeSource(); b.SetBounds(x0, x1, y0, y1, z0, z1); b.Update(); return b.GetOutput()

def lathe(profile, res=64):
    """profile: [(r,z),...] 绕 z 轴旋转"""
    pr = np.asarray(profile, float); m = len(pr)
    th = np.linspace(0, 2 * np.pi, res, endpoint=False)
    pts = np.vstack([np.c_[pr[:, 0] * np.cos(t), pr[:, 0] * np.sin(t), pr[:, 1]] for t in th])
    T = []
    for a in range(res):
        b = (a + 1) % res
        for k in range(m - 1):
            p, q, r_, s = a * m + k, b * m + k, b * m + k + 1, a * m + k + 1
            T += [[p, q, r_], [p, r_, s]]
    return normals(poly_from(pts, T), 60)

def tube(points, r, sides=12):
    pts = vtk.vtkPoints()
    for p in points: pts.InsertNextPoint(*p)
    line = vtk.vtkPolyLine(); line.GetPointIds().SetNumberOfIds(len(points))
    for i in range(len(points)): line.GetPointIds().SetId(i, i)
    ca = vtk.vtkCellArray(); ca.InsertNextCell(line)
    pd = vtk.vtkPolyData(); pd.SetPoints(pts); pd.SetLines(ca)
    t = vtk.vtkTubeFilter(); t.SetInputData(pd); t.SetRadius(r); t.SetNumberOfSides(sides); t.CappingOn(); t.Update()
    return t.GetOutput()

def xform(pd, t):
    f = vtk.vtkTransformPolyDataFilter(); f.SetInputData(pd); f.SetTransform(t); f.Update(); return f.GetOutput()

def T(*ops):
    """T(('t',x,y,z),('rx',deg),('ry',deg),('rz',deg),('s',k)) 按书写顺序作用于物体（后写先作用的 VTK 习惯已处理）"""
    t = vtk.vtkTransform(); t.PostMultiply()
    for op in ops:
        k = op[0]
        if k == 't': t.Translate(*op[1:])
        elif k == 'rx': t.RotateX(op[1])
        elif k == 'ry': t.RotateY(op[1])
        elif k == 'rz': t.RotateZ(op[1])
        elif k == 'ra': t.RotateWXYZ(op[1], *op[2:])
        elif k == 's': t.Scale(*(op[1:] if len(op) > 2 else (op[1],) * 3))
    return t

def merge(*pds):
    a = vtk.vtkAppendPolyData()
    for p in pds: a.AddInputData(p)
    a.Update(); return a.GetOutput()

# ---------- 材质 ----------
MAT = {
    'bronze':  dict(col=(0.80, 0.55, 0.30), metal=1.0, rough=0.32),
    'bronze2': dict(col=(0.62, 0.40, 0.20), metal=1.0, rough=0.45),
    'gold':    dict(col=(1.00, 0.78, 0.38), metal=1.0, rough=0.22),
    'patina':  dict(col=(0.30, 0.52, 0.44), metal=0.35, rough=0.75),
    'iron':    dict(col=(0.32, 0.32, 0.34), metal=1.0, rough=0.5),
    'wood':    dict(col=(0.20, 0.09, 0.05), metal=0.0, rough=0.45),
    'lacquer': dict(col=(0.42, 0.04, 0.03), metal=0.0, rough=0.5),
    'wood_l':  dict(col=(0.62, 0.40, 0.22), metal=0.0, rough=0.6),
    'black':   dict(col=(0.05, 0.05, 0.06), metal=0.0, rough=0.4),
    'skin':    dict(col=(0.86, 0.70, 0.55), metal=0.0, rough=0.6),
    'robe_r':  dict(col=(0.55, 0.10, 0.08), metal=0.0, rough=0.7),
    'robe_g':  dict(col=(0.12, 0.30, 0.26), metal=0.0, rough=0.7),
    'water':   dict(col=(0.35, 0.70, 0.95), metal=0.0, rough=0.1, op=0.55),
    'drum':    dict(col=(0.88, 0.80, 0.62), metal=0.0, rough=0.6),
    'stone':   dict(col=(0.035, 0.035, 0.04), metal=0.0, rough=0.7),
}

def actor(pd, mat, emit=None, op=None, xf=None):
    m = vtk.vtkPolyDataMapper(); m.SetInputData(pd); m.ScalarVisibilityOff()
    a = vtk.vtkActor(); a.SetMapper(m); p = a.GetProperty()
    M = MAT[mat] if isinstance(mat, str) else mat
    p.SetInterpolationToPBR(); p.SetColor(*M['col']); p.SetMetallic(M['metal']); p.SetRoughness(M['rough'])
    o = op if op is not None else M.get('op', 1.0)
    if o < 1: p.SetOpacity(o)
    if emit is not None:
        p.SetEmissiveFactor(*emit)
    if xf is not None: a.SetUserTransform(xf)
    return a

class Stage:
    def __init__(self, w=W, h=H):
        self.ren = vtk.vtkRenderer(); self.win = vtk.vtkRenderWindow(); self.win.SetOffScreenRendering(1)
        self.win.SetSize(w, h); self.win.SetAlphaBitPlanes(1); self.win.SetMultiSamples(0); self.win.AddRenderer(self.ren)
        self.ren.SetBackground(0, 0, 0); self.ren.SetBackgroundAlpha(0.0)
        self.ren.UseFXAAOn()
        self.ren.AutomaticLightCreationOff()
        self.ren.UseImageBasedLightingOff()
        self.lights = []
        self.w, self.h = w, h

    def light(self, pos, col, inten, focal=(0, 0, 0), cone=None):
        l = vtk.vtkLight(); l.SetPosition(*pos); l.SetFocalPoint(*focal); l.SetColor(*col); l.SetIntensity(inten)
        l.SetLightTypeToSceneLight()
        if cone: l.SetPositional(True); l.SetConeAngle(cone)
        self.ren.AddLight(l); self.lights.append(l); return l

    def add(self, a): self.ren.AddActor(a); return a

    def cam(self, pos, focal, up=(0, 0, 1), fov=30):
        c = self.ren.GetActiveCamera(); c.SetPosition(*pos); c.SetFocalPoint(*focal); c.SetViewUp(*up); c.SetViewAngle(fov)
        self.ren.ResetCameraClippingRange()

    def grab(self):
        self.win.Render()
        f = vtk.vtkWindowToImageFilter(); f.SetInput(self.win); f.SetInputBufferTypeToRGBA(); f.ReadFrontBufferOff(); f.Update()
        im = f.GetOutput(); arr = vtk_to_numpy(im.GetPointData().GetScalars()).reshape(self.h, self.w, 4)
        return np.flipud(arr).copy()

    def project(self, p):
        """世界坐标 -> 屏幕像素 (x,y)，y 向下"""
        c = vtk.vtkCoordinate(); c.SetCoordinateSystemToWorld(); c.SetValue(*p)
        x, y = c.GetComputedDoubleDisplayValue(self.ren)
        return x, self.h - y
