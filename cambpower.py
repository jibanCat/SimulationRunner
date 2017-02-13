"""Small module to store CAMB power spectrum manipulation routines"""
import scipy.interpolate as interp
import numpy as np

class CAMBPowerSpectrum(object):
    """Class to store some routines for manipulating and storing power spectra as generated by CAMB.
        The implementation mostly mirrors that in C++ in N-GenIC."""
    def __init__(self, camb_matter, camb_transfer, kmin=1e-5,kmax=1e10):
        pk_camb = np.log10(np.loadtxt(camb_matter))
        assert np.shape(pk_camb)[1] == 2
        lpi,hpi = list(np.searchsorted(pk_camb[:,0], [np.log10(kmin), np.log10(kmax)]))
        # Build an interpolator for the matter power spectrum
        self.dpk = interp.interp1d(pk_camb[lpi:hpi, 0], pk_camb[lpi:hpi, 1], kind='cubic')
        self.kk = 10**pk_camb[lpi:hpi,0]
        # Build interpolators for various species of transfer functions.
        tk_camb = np.loadtxt(camb_transfer)
        #Do this dividing by the total, to avoid the odd CAMB units.
        lti,hti = list(np.searchsorted(tk_camb[:,0], [kmin, kmax]))
        logktrans = np.log10(tk_camb[lti:hti,0])
        self.dtk = {}
        self.dtk['DM'] = interp.interp1d(logktrans, (tk_camb[lti:hti, 1]/tk_camb[lti:hti, 6])**2, kind='cubic')
        #Baryons
        self.dtk['by'] = interp.interp1d(logktrans, (tk_camb[lti:hti, 2]/tk_camb[lti:hti, 6])**2, kind='cubic')
        #Massive neutrinos
        self.dtk['nu'] = interp.interp1d(logktrans, (tk_camb[lti:hti, 5]/tk_camb[lti:hti, 6])**2, kind='cubic')
        #DM + baryons
        self.dtk['DMby'] = interp.interp1d(logktrans, (tk_camb[lti:hti, 7]/tk_camb[lti:hti, 6])**2, kind='cubic')

    def get_camb_power(self, kvals, species='tot'):
        """Get a matter power spectrum for DM, baryons, nu from CAMB.
        kvals - k values to interpolate to
        species - dm, bar or nu. Transfer function to use."""
        lgkvals = np.log10(kvals)
        if species == 'tot':
            return 10**self.dpk(lgkvals)
        tk =  self.dtk[species](lgkvals)
        return 10**self.dpk(lgkvals)*tk
