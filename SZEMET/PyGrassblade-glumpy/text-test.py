# -----------------------------------------------------------------------------
# Copyright (c) 2009-2016 Nicolas P. Rougier. All rights reserved.
# Distributed under the (new) BSD License.
# -----------------------------------------------------------------------------
from glumpy import app
from glumpy.log import log
from glumpy.graphics.text import FontManager
from glumpy.graphics.collections import GlyphCollection
from glumpy.transforms import Position, OrthographicProjection, Viewport

window = app.Window(width=1200, height=800, color=(1,1,1,1))

@window.event
def on_draw(dt):
    window.clear()
    labels.draw()


projection = OrthographicProjection(Position())

font = FontManager.get("OpenSans-Regular.ttf", size=10, mode='agg')
labels = GlyphCollection('agg', transform=projection)

for x in range(0, 1000, 50):
	text = "{}".format(x)
	labels.append(text, font, origin = (x,20,0), anchor_x="left")

window.attach(labels["transform"])
window.attach(labels["viewport"])
app.run()