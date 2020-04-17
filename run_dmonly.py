'''
Create a dm-only simulation filefolder, for multi-fidelity tests.
making resolution and boxsize as two major hyperparameters,
making outher cosmological parameters as another input dict.
'''
import os
import argparse
import json
from SimulationRunner import simulationics

def run_dmonly(box, npart, 
        hubble, omega0, omegab, scalar_amp, ns,
        outdir="data"):
    """Create a full simulation with no gas"""

    outdir = os.path.join(os.path.dirname(__file__),"tests/test2")

    Sim = simulationics.SimulationICs(
        outdir=outdir, box = box, npart = npart, redshift = 99, redend = 0,
        hubble = hubble, omega0 = omega0, 
        omegab = omegab, scalar_amp = scalar_amp,
        ns     = ns)
    Sim.make_simulation(pkaccuracy=0.07)
    assert os.path.exists(outdir)

    #shutil.rmtree(outdir)

def take_params_dict(Latin_dict):
    '''
    take the next param dict with a single
    sample for each param
    '''
    all_keys = Latin_dict.keys()
    length   = len(Latin_dict[all_keys[0]])
    
    assert length == Latin_dict[all_keys[-1]]

    for i in range(length):
        param_dict = {}

        for key in all_keys:
            param_dict[key] = Latin_dict[key][i]
        
        yield param_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    # load the json file with the cosmological parameters in this format
    # { 'hubble' : [0.5, 0.6, 0.7], 'omega0' : [0.2, 0.15, 0.17], ... }
    # should write another function to generate samples
    parser.add_argument("--json_file", type=str, default="paramLatin.json")
    
    # keep a separated flags for boxsize and resolution
    parser.add_argument("--box", type=int, default=256)
    parser.add_argument("--res", type=int, default=128)

    args = parser.parse_args()

    with open(args.json_file, 'r') as f:
        Latin_dict = json.load(f)

    # handle the param file generation one-by-one
    for i,param_dict in enumerate(take_params_dict(Latin_dict)):
        # outdir auto generated, since we will have many folders
        outdir = "{}-{}-dmonly_{}".format(
            args.res, args.box, str(i).zfill(4))

        run_dmonly(args.box, args.res, **param_dict)
