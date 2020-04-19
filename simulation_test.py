"""Integration tests for the Simulation module"""

import os
import re
import configobj
from SimulationRunner import simulationics, clusters
from run_dmonly import run_dmonly, take_params_dict

def test_full_integration():
    """Create a full simulation snapshot and check it corresponds to the saved results"""
    defaultpath = os.path.join(os.path.dirname(__file__), "tests/test1")
    Sim = simulationics.SimulationICs(outdir=defaultpath,box = 256,npart = 96, redshift = 99, redend=0)
    Sim.make_simulation(pkaccuracy=0.07)
    #Check the following files were created
    assert os.path.exists(defaultpath)
    for ff in ("_class_params.ini", "TREECOOL", "mpi_submit", "mpi_submit_genic", "cambpower.py", "camb_linear", "ICS", "output", "camb_linear/ics_matterpow_99.dat", "SimulationICs.json", "mpgadget.param", "_genic_params.ini"):
        assert os.path.exists(os.path.join(defaultpath, ff))
    #Clean the test directory if test was successful
    #shutil.rmtree(defaultpath)

def test_only_DM():
    """Create a full simulation with no gas"""
    outdir = os.path.join(os.path.dirname(__file__),"tests/test2")
    Sim = simulationics.SimulationICs(
        outdir=outdir, box = 256, npart = 96, redshift = 99, redend = 0, hubble = 0.71)
    Sim.make_simulation(pkaccuracy=0.07)
    assert os.path.exists(outdir)

    Sim2 = simulationics.SimulationICs(outdir=outdir, box=128, npart=128)
    Sim2.load_txt_description()
    assert Sim2.box == Sim.box
    assert Sim2.hubble == Sim.hubble
    #shutil.rmtree(outdir)

def test_dmonly_runner():
    '''
    Test the dmonly runner for multi-fidelity
    '''
    Sim = run_dmonly(256, 128, 0.7, 0.3, 0.04, 2.427e-9, 0.97, 
        64, 16, "data", "~/code/MP-Gadget", "path/python", clusters.BIOClass,
        test=True)

    assert os.path.exists("data")
    assert Sim.npart == 128
    assert Sim.cluster.nproc == 64
    assert Sim.cluster.cores == 16
    assert Sim.cluster.nproc % Sim.cluster.cores == 0
    assert Sim.python == "path/python"

    # change a class
    Sim = run_dmonly(256, 128, 0.7, 0.3, 0.04, 2.427e-9, 0.97, 
        64, 16, "data", "~/code/MP-Gadget", "path/python", clusters.StampedeClass,
        test=True)

    assert os.path.exists("data")
    assert Sim.npart == 128
    assert Sim.cluster.nproc == 64
    assert Sim.cluster.cores == 16
    assert Sim.cluster.nproc % Sim.cluster.cores == 0
    assert Sim.python == "path/python"

def test_Latin_taker(json_file):
    '''
    Test if Latin Generator can correctly pick up paramters
    '''
    import json

    with open(json_file, 'r') as f:
        Latin_dict = json.load(f)

    parameter_names = Latin_dict['parameter_names']

    # init a generator
    taker = take_params_dict(Latin_dict)

    this_dict = next(taker)
    next_dict = next(taker)

    # check if consistent with the original file
    for key in this_dict.keys():
        assert key in parameter_names
    
    for param in parameter_names:
        assert param in this_dict.keys()

    assert len(this_dict.keys()) == len(next_dict.keys())
    assert this_dict[parameter_names[0]] != next_dict[parameter_names[0]]
    assert this_dict[parameter_names[-1]] != next_dict[parameter_names[-1]]
