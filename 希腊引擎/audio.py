from audio_lib import *
G = lambda i: T0[i]

def harp(t, k, vol=0.18, base=D): oud(t, hz(k, base), 0.6, vol, 0.85)
def arp(t0, t1, degs, step, vol, base=D):
    t = t0; i = 0
    while t < t1 - 0.05: harp(t, degs[i % len(degs)], vol, base); t += step; i += 1
def ding(t, vol=0.12, m=93):
    n = int(1.6 * SR); x = np.arange(n) / SR; f = mtof(m)
    y = (np.sin(2 * np.pi * f * x) + 0.5 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 3) + 0.25 * np.sin(2 * np.pi * f * 5.4 * x) * np.exp(-x * 6)) * np.exp(-x * 2.2)
    put(y, t, vol, sfx)
def chime_run(t, vol=0.08, up=True, n=8, step=0.06):
    for k in range(n): ding(t + k * step, vol, 86 + (k * 2 if up else 14 - k * 2))
def sticks(t, vol=0.25):
    for k in range(5): clank(t + rng.uniform(0, 0.18), vol * rng.uniform(0.4, 0.8), rng.uniform(600, 1100))
def tap(t, vol=0.3):
    n = int(0.08 * SR); x = np.arange(n) / SR; put(np.sin(2 * np.pi * 420 * x) * np.exp(-x * 60) + lp(rng.standard_normal(n), 0.3) * np.exp(-x * 80) * 0.5, t, vol, sfx)
def step_snd(t, vol=0.12):
    n = int(0.12 * SR); x = np.arange(n) / SR; put(lp(rng.standard_normal(n), 0.08) * np.exp(-x * 40), t, vol, sfx)
def steps(t0, t1, period, vol=0.12):
    t = t0
    while t < t1: step_snd(t, vol); t += period
def rumble(t, dur, vol=0.4):
    n = int(dur * SR); x = np.arange(n) / SR; y = lp(rng.standard_normal(n), 0.01) * 6
    put(y * np.minimum(1, x / 0.3) * np.minimum(1, (dur - x) / 0.5), t, vol, sfx)
def wind_snd(t, dur, vol=0.3, rise=False):
    n = int(dur * SR); x = np.arange(n) / SR; y = lp(rng.standard_normal(n), 0.03) * 3 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * x))
    e = np.minimum(1, x / 0.6) * np.minimum(1, (dur - x) / 0.8)
    if rise: e *= (0.3 + 0.7 * x / dur)
    put(y * e, t, vol, sfx)
def shimmer(t, dur, vol=0.06):
    k = 0
    while k * 0.09 < dur: ding(t + k * 0.09, vol * (0.5 + 0.5 * rng.random()), int(rng.choice([86, 88, 90, 93, 95, 98]))); k += 1

T = TOT
def loom_clack(t0, t1, period=0.42, vol=0.16):
    t = t0; i = 0
    while t < t1:
        n = int(0.09 * SR); x = np.arange(n) / SR
        put((np.sin(2 * np.pi * 260 * x) + 0.5 * np.sin(2 * np.pi * 610 * x)) * np.exp(-x * 45) + lp(rng.standard_normal(n), 0.3) * np.exp(-x * 70) * 0.6, t, vol * (1 if i % 2 == 0 else 0.6), sfx)
        t += period; i += 1
def crowd_murmur(t, dur, vol=0.12, excite=False):
    n = int(dur * SR); x = np.arange(n) / SR
    y = np.zeros(n)
    for k in range(10):
        f = rng.uniform(150, 420); am = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(2, 6) * x + rng.uniform(0, 6))
        y += ss.lfilter(*ss.butter(2, [f / (SR / 2) * 0.9, f * 3 / (SR / 2)], 'band'), rng.standard_normal(n)) * am
    e = np.minimum(1, x / 0.5) * np.minimum(1, (dur - x) / 0.6)
    if excite: e *= 0.6 + 0.4 * np.sin(np.pi * x / dur)
    put(y * e * 0.5, t, vol, sfx)
def gasp(t, vol=0.25):
    n = int(0.5 * SR); x = np.arange(n) / SR
    y = ss.lfilter(*ss.butter(2, [800 / (SR / 2), 3000 / (SR / 2)], 'band'), rng.standard_normal(n)) * np.minimum(1, x / 0.05) * np.exp(-x * 5)
    put(y * 3, t, vol, sfx)
def cheer(t, dur, vol=0.3):
    crowd_murmur(t, dur, vol, True)
    for k in range(int(dur * 4)): gasp(t + rng.uniform(0, dur - 0.4), vol * 0.25)
def giggle(t, vol=0.08):
    for k in range(5):
        n = int(0.07 * SR); x = np.arange(n) / SR; f = 700 + rng.uniform(-80, 120)
        put(np.sin(2 * np.pi * f * x) * np.sin(np.pi * x / 0.07) * (1 + 0.5 * np.sin(2 * np.pi * 30 * x)), t + k * 0.11, vol, sfx)
def rip(t, vol=0.5):
    n = int(0.6 * SR); x = np.arange(n) / SR
    y = rng.standard_normal(n) * (0.5 + 0.5 * (rng.random(n) > 0.7)) * np.exp(-x * 4)
    put(ss.lfilter(*ss.butter(2, 1800 / (SR / 2), 'high'), y), t, vol, sfx); boom(t, 0.5, sfx)
def creak(t, vol=0.12):
    n = int(0.9 * SR); x = np.arange(n) / SR; f = 180 + 40 * np.sin(2 * np.pi * 0.8 * x)
    y = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (rng.random(n) > 0.6) * np.sin(np.pi * x / 0.9)
    put(lp(y, 0.2), t, vol, sfx)
def drip(t, vol=0.2):
    n = int(0.25 * SR); x = np.arange(n) / SR; f = 900 + 1400 * x / 0.25
    put(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 18), t, vol, sfx)
def shrink(t, dur, vol=0.2):
    n = int(dur * SR); x = np.arange(n) / SR; f = 600 * np.exp(-x * 1.5) + 80
    put(np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6 * np.minimum(1, x / 0.2) * np.minimum(1, (dur - x) / 0.3) + lp(rng.standard_normal(n), 0.05) * 0.5 * np.exp(-x), t, vol, sfx)
def owl_hoot(t, vol=0.12):
    for k, (d, f) in enumerate(((0.35, 380), (0.6, 360))):
        n = int(d * SR); x = np.arange(n) / SR; put(np.sin(2 * np.pi * f * x) * np.sin(np.pi * x / d) ** 2, t + k * 0.5, vol, sfx)


def gulp_snd(t, vol=0.5, heavy=False):
    n = int(0.55 * SR); x = np.arange(n) / SR; f = (180 if not heavy else 120) * np.exp(-x * 3) + 50
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 6) + lp(rng.standard_normal(n), 0.05) * np.exp(-x * 10) * 2
    put(y, t, vol, sfx)
    if heavy: thud(t + 0.35, 0.5); boom(t + 0.3, 0.5, sfx)
def cry(t, dur=1.2, vol=0.08):
    k = 0.0
    while k < dur:
        d_ = 0.38; n = int(d_ * SR); x = np.arange(n) / SR; f = 520 + 160 * np.sin(np.pi * x / d_) + 30 * np.sin(2 * np.pi * 7 * x)
        y = (np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3 + np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.sin(np.pi * x / d_)
        put(lp(y, 0.35), t + k, vol, sfx); k += 0.48
def thunder(t, vol=0.6):
    crash(t, vol * 0.5); rumble(t, 2.4, vol); boom(t, vol, sfx)
def retch(t, vol=0.3):
    n = int(0.45 * SR); x = np.arange(n) / SR
    y = ss.lfilter(*ss.butter(2, [150 / (SR / 2), 900 / (SR / 2)], 'band'), rng.standard_normal(n)) * np.sin(np.pi * x / 0.45) * (1 + 0.6 * np.sin(2 * np.pi * 28 * x))
    put(y * 3, t, vol, sfx)
def gurgle(t, dur, vol=0.2):
    k = 0.0
    while k < dur:
        n = int(0.12 * SR); x = np.arange(n) / SR; f = rng.uniform(90, 220) * (1 + x * 4)
        put(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * x / 0.12), t + k, vol * rng.uniform(0.4, 1), sfx); k += rng.uniform(0.08, 0.25)
def bubbles(t, dur, vol=0.06):
    k = 0.0
    while k < dur: drip(t + k, vol * rng.uniform(0.4, 1)); k += rng.uniform(0.15, 0.4)
def squelch(t, vol=0.25):
    n = int(0.3 * SR); x = np.arange(n) / SR
    put(lp(rng.standard_normal(n), 0.15) * np.exp(-x * 9) * (1 + np.sin(2 * np.pi * 40 * x)), t, vol, sfx)
def click(t, vol=0.12):
    n = int(0.05 * SR); x = np.arange(n) / SR; put(rng.standard_normal(n) * np.exp(-x * 120), t, vol, sfx); put(rng.standard_normal(n) * np.exp(-x * 120), t + 0.07, vol * 0.7, sfx)
def slash(t, vol=0.4):
    whoosh(t - 0.15, 0.3); clank(t, 0.3, 2600); crash(t, 0.3)
def snore(t, vol=0.06):
    n = int(1.0 * SR); x = np.arange(n) / SR
    put(lp(rng.standard_normal(n), 0.04) * np.sin(np.pi * x) ** 2 * (1 + np.sin(2 * np.pi * 30 * x)) * 2, t, vol, sfx)

T = TOT
def lyre_run(t0, t1, degs, step, vol, base=D):
    arp(t0, t1, degs, step, vol, base)
def hiss(t, dur=0.8, vol=0.2):
    n = int(dur * SR); x = np.arange(n) / SR
    put(ss.lfilter(*ss.butter(2, 3000 / (SR / 2), 'high'), rng.standard_normal(n)) * np.sin(np.pi * x / dur) ** 0.5, t, vol, sfx)
def bark3(t, vol=0.3):
    for k in range(3): growl(t + k * 0.18, 0.5, vol)
def heartbeat(t0, t1, bpm, vol=0.6): perc(t0, t1, bpm, 'heart', vol, fills=False)
def whisper_v(t, dur, vol=0.1):
    n = int(dur * SR); x = np.arange(n) / SR
    y = ss.lfilter(*ss.butter(2, [1500 / (SR / 2), 5000 / (SR / 2)], 'band'), rng.standard_normal(n)) * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * x + np.sin(2 * np.pi * 0.7 * x) * 3))
    put(y * np.minimum(1, x / 0.4) * np.minimum(1, (dur - x) / 0.5), t, vol, sfx)

def call(t, ph, vol=0.13, base=D):
    ney(t, ph, 80, vol, base)
def echoes(t, ph, vol=0.12, n=3, gap=0.7, base=D):
    for k in range(n): ney(t + k * gap, ph, 80, vol * (0.55 ** k), base)
def chatter_snd(t0, t1, vol=0.07):
    t = t0
    while t < t1:
        ding(t, vol * rng.uniform(0.4, 1), int(rng.choice([86, 88, 90, 93, 95]))); t += rng.uniform(0.08, 0.18)
CALL1 = [(4, 0.5), (7, 1)]; CALL2 = [(7, 0.4), (4, 0.4), (0, 1)]
T = TOT
LULL = [(4, 1), (2, 1), (0, 2), (2, 0.5), (4, 0.5), (5, 1), (4, 2), (None, 1)]
LULL2 = [(7, 1), (5, 1), (4, 1), (2, 1), (0, 3), (None, 1)]
def pipe(t0, notes, bpm, vol, base=D + 12): ney(t0, notes, bpm, vol, base, 0.05, 0.35)
def blinkclose(t, vol=0.05): ding(t, vol, int(rng.choice([69, 72, 74])))
def alarm_horn(t, vol=0.25): horn(t, 1.2, D + 7, vol); horn(t + 0.05, 1.2, D + 8, vol * 0.7)
# 0 钩子
drone(0, G(1), D - 24, 0.3); pad(0, G(1), [0, 1, 4], 0.2); heartbeat(0.3, G(1) - 0.5, 70, 0.7)
shimmer(G(0) + 0.5, 2.0, 0.07); whoosh(G(0) + 2.2, 0.3); clank(G(0) + 2.4, 0.15, 2600); boom(G(0) + 3.4, 0.6)
# 1 标题
frame(G(1) + 0.2, 1.0); boom(G(1) + 0.2, 0.7); crash(G(1) + 0.2, 0.2); pad(G(1), G(2) + 0.5, [0, 1, 4, 7], 0.22); chime_run(G(1) + 0.6, 0.07, True, 10)
# 2-5 守卫 / 百眼 / 睡觉
B = 96
perc(G(2), G(4), B, 'baladi', 0.6); oud_ost(G(2), G(4), B, 0.14); pad(G(2), G(4), [0, 2, 4], 0.14)
seq(G(2), G(4), B, [PE, PA], lambda t, ph, b, v, ba: ney(t, ph, b, v, ba + 12), 0.08); crowd_murmur(G(2), 5, 0.05); steps(G(2), G(3), 0.6, 0.1)
for k in range(24): sparkle(G(3) + 0.3 + k * 0.13, 0.04)
shimmer(G(3) + 3.2, 1.5, 0.06)
drone(G(4), G(6), D - 24, 0.22); pad(G(4), G(6), [0, 1, 4], 0.16); snore(G(4) + 0.6, 0.06); snore(G(4) + 2.6, 0.06); owl_hoot(G(5) + 0.8, 0.1); wind_snd(G(4), 10, 0.06)
for k in range(8): blinkclose(G(5) + 0.4 + k * 0.5, 0.04)
# 6 河边少女
B = 108
perc(G(6), G(7), B, 'maqsum', 0.5); oud_ost(G(6), G(7), B, 0.14, (0, 4, 2, 4, 0, 4, 3, 4)); pad(G(6), G(7), [0, 2, 4], 0.12)
ney(G(6) + 0.3, PE, B, 0.08, D + 12); water(G(6), 5.6, 0.08); crowd_murmur(G(6), 5.6, 0.06); giggle(G(6) + 2.8, 0.07)
# 7-8 变牛
drone(G(7), G(9), D - 24, 0.26); perc(G(7), G(8), 120, 'saidi', 0.8); thunder(G(7) + 0.2, 0.5); thunder(G(7) + 1.8, 0.4); wind_snd(G(7), 5, 0.15)
shimmer(G(8) + 0.4, 1.4, 0.08); whoosh(G(8) + 1.0, 0.25); boom(G(8) + 1.6, 0.6); chime_run(G(8) + 1.6, 0.08, False, 12); thud(G(8) + 2.4, 0.2)
# 9-11 赫拉驾到
B = 92
pad(G(9), G(12), [0, 2, 4, 7], 0.18); perc(G(9) + 2.4, G(12), B, 'maqsum', 0.4); oud_ost(G(9) + 2.4, G(12), B, 0.12)
chime_run(G(9) + 0.2, 0.08, False, 14); shimmer(G(9), 3, 0.06); frame(G(9) + 2.6, 0.5)
ney(G(10) + 0.3, [(4, 0.5), (5, 0.5), (4, 1), (2, 1), (4, 2)], 90, 0.09, D + 12)
gulp_snd(G(11) + 1.2, 0.3); for_ = [tap(G(11) + 2.0 + k * 0.5, 0.15) for k in range(3)]
# 12-13 交给阿耳戈斯
drone(G(12), G(14), D - 24, 0.22); perc(G(12), G(14), 96, 'saidi', 0.6); thud(G(12) + 0.6, 0.3)
boom(G(13) + 1.6, 0.7); shimmer(G(13) + 1.6, 1.6, 0.08); for_ = [sparkle(G(13) + 1.6 + k * 0.05, 0.05) for k in range(12)]
# 14-15 日夜看守
B = 88
perc(G(14), G(16), B, 'baladi', 0.45); oud_ost(G(14), G(16), B, 0.12, (0, 4, 3, 4)); pad(G(14), G(16), [0, 1, 4], 0.14)
for k in range(10): blinkclose(G(14) + k * 0.6, 0.035)
water(G(15), 4.4, 0.1); owl_hoot(G(14) + 3.0, 0.06)
# 16-17 宙斯 / 赫尔墨斯
pad(G(16), G(17), [0, 1, 3], 0.18); ney(G(16) + 0.3, [(4, 1), (3, 0.5), (1, 0.5), (0, 2)], 56, 0.1)
B = 128
perc(G(17), G(18), B, 'malfuf', 0.6); oud_ost(G(17), G(18), B, 0.13); whoosh(G(17) + 1.2, 0.35); chime_run(G(17) + 1.3, 0.07, True, 10); wind_snd(G(17) + 1.0, 4, 0.12)
# 18 报警
steps(G(18) + 0.4, G(18) + 1.4, 0.3, 0.08); boom(G(18) + 1.7, 0.7); alarm_horn(G(18) + 1.8, 0.2); heartbeat(G(18) + 1.8, G(19), 130, 0.7); growl(G(18) + 2.0, 1.0, 0.1)
# 19 变身
pad(G(19), G(20), [0, 2, 4], 0.16); sparkle(G(19) + 0.5, 0.08); shimmer(G(19) + 1.2, 1.4, 0.08); whoosh(G(19) + 1.6, 0.3); boom(G(19) + 2.0, 0.4)
for k in range(8): yip(G(19) + 2.2 + k * 0.25, 0.04)
# 20-24 排笛催眠
pad(G(20), G(25), [0, 2, 4], 0.14); drone(G(20), G(25), D - 24, 0.15)
oud_ost(G(20), G(21), 84, 0.1, (0, 4, 2, 4)); steps(G(20), G(21), 0.45, 0.07)
seq(G(20), G(25), 72, [LULL, LULL2], pipe, 0.11)
for k in range(10): yip(G(20) + 0.5 + k * 0.5, 0.025)
for k in range(30): blinkclose(G(23) + 0.3 + k * 0.11, 0.03)
heartbeat(G(24), G(25), 66, 0.5)
# 25-28 无聊故事 / 天黑
drone(G(25), G(29), D - 24, 0.2); pad(G(25), G(29), [0, 1, 4], 0.14); for_ = [whisper_v(G(25) + k * 1.6, 1.4, 0.06) for k in range(int((G(28) - G(25)) / 1.6))]
snore(G(26) + 1.0, 0.06); snore(G(27) + 1.0, 0.07); snore(G(27) + 3.4, 0.08); wind_snd(G(27), 5, 0.06); owl_hoot(G(27) + 3.0, 0.08)
for k in range(20): blinkclose(G(28) + 0.2 + k * 0.25, 0.035)
heartbeat(G(28), G(30), 60, 0.6)
# 29-30 最后一只 / 寂静
ding(G(29) + 3.4, 0.12, 69); pad(G(29), G(30), [0, 1], 0.1)
ding(G(30) + 2.2, 0.1, 93); clank(G(30) + 2.3, 0.08, 3200)
# 31-33 斩首 / 坠崖 / 熄灭
heartbeat(G(31), G(31) + 1.6, 120, 0.7); clank(G(31) + 1.0, 0.18, 2600); whoosh(G(31) + 1.6, 0.5); slash(G(31) + 1.85, 0.5); boom(G(31) + 1.9, 1.0); crash(G(31) + 1.9, 0.4)
drone(G(31) + 1.9, G(34), D - 36, 0.32); pad(G(31) + 2, G(34), [0, 1, 3], 0.2)
rumble(G(32) + 0.3, 3.5, 0.3); for_ = [thud(G(32) + 0.6 + k * 0.6, 0.25) for k in range(5)]
for k in range(30): ding(G(33) + 0.5 + k * 0.12, 0.03, 81 - (k % 5))
# 34-37 赫拉悲痛 / 摘眼
drone(G(34), G(38), D - 24, 0.26); pad(G(34), G(38), [0, 1, 3], 0.2); wind_snd(G(34), 11, 0.14); thunder(G(34) + 0.1, 0.6); thunder(G(34) + 3.0, 0.5)
cry(G(34) + 1.4, 1.6, 0.06); cry(G(35) + 1.0, 1.4, 0.05); ney(G(35) + 0.3, [(4, 1), (3, 0.5), (1, 0.5), (0, 2)], 52, 0.1)
steps(G(36), G(37), 0.55, 0.1); shimmer(G(36) + 1.0, 3, 0.05)
for k in range(40): sparkle(G(37) + 0.2 + k * 0.12, 0.035)
# 38-39 孔雀
B = 90
pad(G(38), G(40), [0, 2, 4, 7], 0.18); oud_ost(G(38), G(40), B, 0.12, (0, 4, 2, 4)); water(G(38), 9.4, 0.06)
for k in range(16): sparkle(G(38) + 0.8 + k * 0.2, 0.04)
shimmer(G(39) + 0.6, 2.4, 0.08); boom(G(39) + 2.4, 0.5); chime_run(G(39) + 2.4, 0.09, True, 14); crash(G(39) + 2.4, 0.15)
# 40-43 今天 / 凝视人间
B = 96
perc(G(40), G(42), B, 'maqsum', 0.45); oud_ost(G(40), G(42), B, 0.13); pad(G(40), G(44), [0, 2, 4], 0.14)
seq(G(40), G(42), B, [PE, PA], lambda t, ph, b, v, ba: ney(t, ph, b, v, ba + 12), 0.08); crowd_murmur(G(40), 5.4, 0.06)
for k in range(6): click(G(40) + 1.2 + k * 0.7, 0.1)
shimmer(G(41) + 1.6, 1.8, 0.07); chime_run(G(41) + 1.8, 0.08, True, 12)
drone(G(42), G(44), D - 24, 0.2); shimmer(G(42) + 1.6, 2.4, 0.06); ney(G(43) + 0.3, PE, 54, 0.1)
# 44-45 回到开场
drone(G(44), T, D - 24, 0.28); pad(G(44), G(45) + 1, [0, 1, 4], 0.2); heartbeat(G(44) + 0.3, G(44) + 2.0, 70, 0.7)
shimmer(G(44) + 0.5, 2.0, 0.07); whoosh(G(44) + 2.2, 0.3); boom(G(44) + 3.4, 0.6)
frame(G(45) + 0.1, 0.8); chime_run(G(45) + 0.3, 0.06, True, 8)
for i in range(1, len(T0) - 1):
    if F.GRP[i][1] == 0 and i not in (1, 8, 31, 44): whoosh(T0[i], 0.07)

mix = np.tanh((mus * 0.75 + sfx * 0.55) * 1.0)
fade = np.ones(N); nf = int(2.0 * SR); fade[-nf:] = np.linspace(1, 0, nf); mix *= fade
st = np.stack([mix, mix], 1); st[:, 1] = np.roll(st[:, 1], int(0.008 * SR))
os.makedirs('out', exist_ok=True)
sf.write('out/mix_raw.wav', st, SR)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'out/mix_raw.wav', '-af', 'loudnorm=I=-15:TP=-1.5:LRA=9', '-ar', '44100', 'out/mix.wav'], check=True)
print('ok', TOT)
