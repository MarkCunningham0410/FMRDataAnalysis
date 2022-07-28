import numpy as np
import matplotlib.pyplot as plt
import h5py as h5
import argparse
import pandas as pd
from sklearn.preprocessing import normalize



def normalise_array(data):
    data_normed = data / data.max(axis=0)

    return data_normed


def scan_hdf5(path, recursive=True, tab_step=2):
    """
    Takes path to .h5 file and prints all contents.
    """
    def scan_node(g, tabs=0):
        print(' ' * tabs, g.name)
        for k, v in g.items():
            if isinstance(v, h5.Dataset):
                print(' ' * tabs + ' ' * tab_step + ' -', v.name)
            elif isinstance(v, h5.Group) and recursive:
                scan_node(v, tabs=tabs + tab_step)
    with h5.File(path, 'r') as f:
        scan_node(f)


def read_and_scan(*filenames):
    """
    Takes path to multiple .h5 files and returns h5 datasets as list
    """
    h5_files = [h5.File(filename) for filename in filenames]
    return h5_files


def current_frequency_amplitude(h5_block):
    """
    Takes h5 dataset and returns current, frequency and amplitude as dictionary containing each array
    """
    frame = {
        'current' : np.asarray(h5_block['entry']['data0']['current']),
        'frequency' : np.asarray(h5_block['entry']['data0']['frequency']),
        'amplitude' : 20*np.log10(np.asarray(h5_block['entry']['data0']['amplitude']).T)
    }
    
    return frame


def current_frequency_mesh(current_axes,frequency_axes):
    """
    Takes current and frequency arrays and converts into meshgrid for contour plot
    """
    current_mesh, frequency_mesh = np.meshgrid(current_axes, frequency_axes)
    return current_mesh, frequency_mesh


def contour_plot(current, frequency, amplitude, maximum_y = 8):
    """
    Returns contour plot of Frequency, Current and Amplitude
    """
    params = {'mathtext.default': 'regular' }          
    plt.rcParams.update(params)
    current_mesh, frequency_mesh = current_frequency_mesh(current, frequency)

    plt.pcolormesh(current_mesh,frequency_mesh/1e9, amplitude, vmin=-25, vmax=-10)

    cbar = plt.colorbar()
    cbar.set_label("$S_{11}$ (Normalised Amplitude)")
    plt.xlabel('Current /A')
    plt.ylabel('Frequency /GHz')
    plt.ylim(ymax=maximum_y)
    plt.xlim()

    plt.savefig('saved_plots/Testing_plot.png', transparent=False)


def background_separation(sample_amplitude, background_amplitude):
    """
    Converts signal to decibels after removing background noise.
    """
    return ((sample_amplitude * background_amplitude) / (sample_amplitude[0] * background_amplitude[0]))


def functionality(*filenames, background_removal = False):
    h5_files = read_and_scan(*filenames)
    sample = current_frequency_amplitude(h5_files[0])
    current, frequency, sample_amplitude = sample['current'], sample['frequency'], sample['amplitude']

    background_amplitude = current_frequency_amplitude(h5_files[1])['amplitude']

    if background_removal:
        foreground_amplitude = background_separation(sample_amplitude, background_amplitude)
        contour_plot(current, frequency, normalise_array(foreground_amplitude))
    
    else:
        normalised_amplitude = normalise_array(sample_amplitude)
        contour_plot(current,frequency, normalised_amplitude)
        
    return


def parse_arguments():
    parser = argparse.ArgumentParser(description = 'Run FMR Data Analysis')
    parser.add_argument('-sample_path', metavar='sample_path', type = str, help = 'The path to sample .h5 file')
    parser.add_argument('-background_path', metavar='background_path', type = str, help = 'The path to background .h5 file', default='sample_files/no_sample.h5')
    parser.add_argument('-background_removal', action='store_true', help = 'Toggles removal of background amplitudes')
    
    return parser.parse_args()



def main():
    args = parse_arguments()
    file_paths = {
        'sample' : args.sample_path,
        'background' : args.background_path
    }
    functionality(*file_paths.values()) #args.background_removal)



if __name__ == '__main__':
    main()