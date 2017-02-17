"""Integration tests for the neutrinosimulation module"""

import filecmp
import os
import bigfile
import numpy as np
import configobj
from . import neutrinosimulation as nus

def test_neutrino_part():
    """Create a full simulation with particle neutrinos."""
    test_dir = os.path.join(os.getcwd(),"test_nu/")
    Sim = nus.NeutrinoPartICs(outdir=test_dir,box = 256,npart = 256, m_nu = 0.45, redshift = 99, separate_gas=False, code_args={'redend':0, 'do_build':False})
    Sim.make_simulation()
    assert os.path.exists(test_dir)
    #Check these we are writing reasonable values.
    config = configobj.ConfigObj(os.path.join(test_dir,"_genic_params.ini"))
    assert config['Omega'] == "0.288"
    assert config['OmegaLambda'] == "0.712"
    assert config['NNeutrino'] == "256"
    assert config['NBaryon'] == "0"
    assert config['NU_in_DM'] == "0"
    assert config['NU_Vtherm_On'] == "1"
    assert config['NU_PartMass_in_ev'] == "0.45"
    #Check that the output has neutrino particles
    f = bigfile.BigFile(os.path.join(test_dir,"ICS/256_256_99"),'r')
    assert f["Header"].attrs["TotNumPart"][2] == 256**3
    #Clean the test directory if test was successful
    #Check the mass is correct
    mcdm = f["Header"].attrs["MassTable"][1]
    mnu = f["Header"].attrs["MassTable"][2]
    #The mass ratio should be given by the ratio of omega_nu by omega_cdm
    assert np.abs(mnu/(mcdm+mnu) / ( (Sim.m_nu/93.146/Sim.hubble**2)/(Sim.omega0)) - 1) < 1e-5
    assert np.abs(f["Header"].attrs["MassTable"][1] / 7.71739 - 1) < 1e-5
    f.close()
    #shutil.rmtree("./test_nu/")

def test_neutrino_semilinear():
    """Create a full simulation with semi-linear neutrinos.
    The important thing here is to test that OmegaNu is correctly set."""
    test_dir = os.path.join(os.getcwd(),"test_nu_semilin/")
    Sim = nus.NeutrinoSemiLinearICs(outdir=test_dir,box = 256,npart = 256, m_nu = 0.45, redshift = 99, separate_gas=False, code_args={'redend':0, 'do_build':False})
    Sim.make_simulation()
    assert os.path.exists(test_dir)
    #Check these files have not changed
    config = configobj.ConfigObj(os.path.join(test_dir,"_genic_params.ini"))
    assert config['Omega'] == "0.288"
    assert config['OmegaLambda'] == "0.712"
    assert config['NNeutrino'] == "0"
    assert config['NU_in_DM'] == "0"
    assert config['NU_Vtherm_On'] == "0"
    assert config['NU_PartMass_in_ev'] == "0.45"

    config = configobj.ConfigObj(os.path.join(test_dir,"_camb_params.ini"))
    assert abs(float(config['ombh2']) - 0.023127999999999996) < 1e-7
    assert abs(float(config['omch2']) - 0.11316056345286662) < 1e-7
    assert abs(float(config['omnuh2']) - 0.004831436547133348) < 1e-7
    assert config['massless_neutrinos'] == "0.046"
    assert config['massive_neutrinos'] == "3"

    config = configobj.ConfigObj(os.path.join(test_dir,"mpgadget.param"))
    assert config['MNue'] == "0.15"
    assert config['MNum'] == "0.15"
    assert config['MNut'] == "0.15"
    assert config['MassiveNuLinRespOn'] == "1"
    assert config['TimeTransfer'] == "0.01"
    assert config['OmegaBaryonCAMB'] == "0.0472"
    assert config['InputSpectrum_UnitLength_in_cm'] == "3.085678e+24"
    assert config['KspaceTransferFunction'] == "camb_linear/ics_transfer_99.dat"
    #Check that the output has no neutrino particles
    f = bigfile.BigFile(os.path.join(test_dir, "ICS/256_256_99"),'r')
    assert f["Header"].attrs["TotNumPart"][2] == 0
    #Check the mass is correct: the CDM particles should have the same mass as in the particle simulation
    assert np.abs(f["Header"].attrs["MassTable"][1] / 7.71739 - 1) < 1e-5
    f.close()
    #shutil.rmtree("./test_nu/")
