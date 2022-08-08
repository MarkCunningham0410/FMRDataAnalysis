import qkit


def qkit_setup():

    qkit.cfg['load_visa'] = True
    qkit.cfg['datafolder_structure'] = 2
    # New Qkit does not create folder. Must be done before run! (think a txt doc is created which causes this)
    qkit.cfg['datadir'] = r'd:\notebooks\Adam_FMR'
    qkit.cfg['run_id'] = 'Test_Rair_Py_21_07_22'
    qkit.cfg['user'] = 'Rair'

    return


from qkit.measure import samples_class # awful but need to review qkit setup structure
import numpy as np
from qkit.measure.spectroscopy import spectroscopy



def instrument_setup():
    caen = qkit.instruments.create('caen', 'Caen_FAST_PS', address='10.22.197.101')
    vna = qkit.instruments.create('vna', 'ZVA_40_VNA', address='GPIB0::20::INSTR')

    return caen, vna


def sample_setup(vna):
    our_sample = samples_class.Sample()
    sample_spectrum = spectroscopy.spectrum(vna = vna, exp_name = '', sample = our_sample)

    return sample_spectrum


def caen_vna_setup(caen, vna):
    caen.on()
    caen.get_current()

    vna.set_ifbandwidth(3e3)
    vna.set_power(-5)
    vna.set_startfreq(3.00e9) # use the correct values should be somewhere between 4 and 6 GHz
    vna.set_stopfreq(15.00e9)
    vna.set_nop(5001)

    return


def _current_ramping_x(caen, i):
    return caen.ramp_current(i, 1e-1)


def spectrum_main(spectrum, caen):
    spectrum.set_resonator_fit(fit_resonator=False)

    spectrum.set_x_parameters(x_vec = np.arange(-4, 4.0, 0.05),
                    x_coordname = 'current',
                    x_set_obj = _current_ramping_x, #potential bug here
                    x_unit = 'A')

    spectrum.measure_2D()


def main():
    qkit.start()
    caen, vna = instrument_setup()
    caen_vna_setup(caen, vna)
    spectrum = sample_setup(vna)
    spectrum_main(spectrum, caen)

    caen.ramp_current(0, 3)


if __name__ == '__main__':
    main()