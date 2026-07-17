"""
Generate 'dirty.gds' — a layout with deliberate DRC violations, plus some clean
geometry, so you can watch each rule in foundry.drc light up.

Layers:   metal1 = 1/0    via = 2/0    metal2 = 3/0
Units:    dbu = 1 nm  (so 1 um = 1000 units, 0.20 um = 200 units)

Run:
    klayout -b -r generate_dirty.py         # writes dirty.gds next to this script
    python generate_dirty.py                # needs:  pip install klayout
"""

import os

try:
    import pya as db
except ImportError:
    import klayout.db as db

UM = 1000  # database units per micron


def build():
    ly = db.Layout()
    ly.dbu = 0.001
    top = ly.create_cell("DIRTY_TOP")
    m1 = ly.layer(1, 0)   # metal1
    via = ly.layer(2, 0)  # via
    m2 = ly.layer(3, 0)   # metal2

    B = db.Box  # coords in nm

    # --- VIOLATIONS -------------------------------------------------------

    # M1.W : too-thin wire — 100 nm wide (min is 200 nm)
    top.shapes(m1).insert(B(0, 0, 1000, 100))

    # M1.S : two shapes only 100 nm apart (min spacing 200 nm)
    top.shapes(m1).insert(B(0, 500, 300, 700))
    top.shapes(m1).insert(B(400, 500, 700, 700))

    # M1.A : tiny 100x100 nm square = 0.01 um^2 (min area 0.05 um^2)
    top.shapes(m1).insert(B(0, 1000, 100, 1100))

    # V1.ENC : via enclosed by metal by only 30 nm on the left (min 50 nm)
    top.shapes(m1).insert(B(2000, 0, 2600, 600))
    top.shapes(via).insert(B(2030, 300, 2230, 500))   # 30 nm from left metal edge

    # V1.COV : via with NO metal over it at all (must be covered by metal1)
    top.shapes(via).insert(B(6000, 0, 6200, 200))

    # M1M2.OV : metal1 and metal2 overlap (a short between layers)
    top.shapes(m1).insert(B(0, 2000, 600, 2600))
    top.shapes(m2).insert(B(400, 2000, 1000, 2600))   # overlaps x=400..600

    # --- CLEAN geometry (should NOT be flagged) ---------------------------

    # Wide, isolated wire: 500 nm wide, far from everything.
    top.shapes(m1).insert(B(4000, 0, 5000, 500))

    # Properly enclosed via: metal pad with the via inset 200 nm all around.
    top.shapes(m1).insert(B(2000, 2000, 2600, 2600))
    top.shapes(via).insert(B(2200, 2200, 2400, 2400))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dirty.gds")
    ly.write(out)
    print("wrote", out)


build()
