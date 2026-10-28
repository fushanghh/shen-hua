import sys, numpy as np
from PIL import Image
import film as F
ts = [float(F.T0[i]) + F.S[i][0] * float(f) for i in range(len(F.S)) for f in sys.argv[2].split(',')] if len(sys.argv) > 2 else [float(F.T0[i]) + F.S[i][0] * 0.7 for i in range(len(F.S))]
rng = sys.argv[1].split(':'); a, b = int(rng[0]), int(rng[1])
ts = ts[a:b]
ims = [Image.fromarray(F.render(t)).resize((480, 360)) for t in ts]
cols = 4; rows = (len(ims) + cols - 1) // cols
sh = Image.new('RGB', (480 * cols, 360 * rows))
for i, im in enumerate(ims): sh.paste(im, ((i % cols) * 480, (i // cols) * 360))
sh.save(sys.argv[3] if len(sys.argv) > 3 else '/home/sandbox/st/sheet.jpg', quality=82)
print(F.TOTAL)
