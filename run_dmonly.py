'''
Create a dm-only simulation filefolder, for multi-fidelity tests.
making resolution and boxsize as two major hyperparameters,
making outher cosmological parameters as another input dict.
'''
from SimulationRunner import simulationics
import os

def run_dmonly(box, npart, outdir="data"):
    """Create a full simulation with no gas"""

    outdir = os.path.join(os.path.dirname(__file__),"tests/test2")

    Sim = simulationics.SimulationICs(
        outdir=outdir, box = box, npart = npart, redshift = 99, redend = 0, hubble = 0.71)
    Sim.make_simulation(pkaccuracy=0.07)
    assert os.path.exists(outdir)

    Sim2 = simulationics.SimulationICs(outdir=outdir, box=128, npart=128)
    Sim2.load_txt_description()
    assert Sim2.box == Sim.box
    assert Sim2.hubble == Sim.hubble
    #shutil.rmtree(outdir)
