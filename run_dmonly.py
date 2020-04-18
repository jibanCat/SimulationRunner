'''
Create a dm-only simulation filefolder, for multi-fidelity tests.
making resolution and boxsize as two major hyperparameters,
making outher cosmological parameters as another input dict.
'''
from typing import Generator, Type
import os
import argparse
import json
from SimulationRunner import simulationics, clusters

def run_dmonly(box: int, npart: int,
        hubble: float, omega0: float, omegab: float,
        scalar_amp: float, ns: float,
        outdir: str = "data",
        gadget_dir: str = "~/bigdata/codes/MP-Gadget/",
        cluster_class: Type[clusters.BIOClass] = clusters.BIOClass) -> None:
    """Create a full simulation with no gas"""

    Sim = simulationics.SimulationICs(
        outdir=outdir, box = box, npart = npart, redshift = 99, redend = 0,
        hubble = hubble, omega0 = omega0, 
        omegab = omegab, scalar_amp = scalar_amp,
        ns     = ns, gadget_dir = gadget_dir,
        cluster_class = cluster_class)
    Sim.make_simulation(pkaccuracy=0.07)
    assert os.path.exists(outdir)

    #shutil.rmtree(outdir)

def take_params_dict(Latin_dict: dict) -> Generator:
    '''
    take the next param dict with a single
    sample for each param
    '''
    parameter_names = Latin_dict['parameter_names']
    length          = len(Latin_dict[parameter_names[0]])
    
    assert length == len(Latin_dict[parameter_names[-1]])

    for i in range(length):
        param_dict = {}

        for key in parameter_names:
            param_dict[key] = Latin_dict[key][i]
        
        yield param_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    # load the json file with the cosmological parameters in this format
    # { 'hubble' : [0.5, 0.6, 0.7], 'omega0' : [0.2, 0.15, 0.17], ... }
    # should write another function to generate samples
    parser.add_argument("--json_file", type=str, default="paramLatin.json")
    
    parser.add_argument("--gadget_dir", type=str,
        default="~/bigdata/codes/MP-Gadget/")
    parser.add_argument("cluster_class", type=str,
        default="clusters.BIOClass")

    # keep a separated flags for boxsize and resolution
    parser.add_argument("--box", type=int, default=256)
    parser.add_argument("--res", type=int, default=128)

    args = parser.parse_args()

    # make the cluster class to be a str so can put in argparser
    cc = eval(args.cluster_class)

    with open(args.json_file, 'r') as f:
        Latin_dict = json.load(f)

    # handle the param file generation one-by-one
    for i,param_dict in enumerate(take_params_dict(Latin_dict)):
        # outdir auto generated, since we will have many folders
        outdir = "test-{}-{}-dmonly_{}".format(
            args.res, args.box, str(i).zfill(4))

        run_dmonly(args.box, args.res, 
            outdir=outdir, gadget_dir=args.gadget_dir,
            cluster_class=cc,
            **param_dict)
