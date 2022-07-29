import numpy as np
import matplotlib.pyplot as plt
import h5py as h5
import argparse



def normalise_array(amplitude):
    """
    Normalises amplitude array relative to the start of each row
    """
    normalised_amplitude = 20*np.log10(amplitude/amplitude[:,0].reshape(-1,1))
    return normalised_amplitude


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
    h5_files = [h5.File(f'sample_files/{filename}') for filename in filenames]
    return h5_files


def current_frequency_amplitude(h5_block):
    """
    Takes h5 dataset and returns current, frequency and amplitude as dictionary containing each array
    """
    frame = {
        'current' : np.asarray(h5_block['entry']['data0']['current']),
        'frequency' : np.asarray(h5_block['entry']['data0']['frequency']),
        'amplitude' : np.asarray(h5_block['entry']['data0']['amplitude']).T
    }
    
    return frame


def current_frequency_mesh(current_axes,frequency_axes):
    """
    Takes current and frequency arrays and converts into meshgrid for contour plot
    """
    current_mesh, frequency_mesh = np.meshgrid(current_axes, frequency_axes)
    return current_mesh, frequency_mesh


def contour_plot(current, frequency, amplitude, v_min = -2.5, v_max = 0.7):
    """
    Returns contour plot of Frequency, Current and Amplitude
    """
    params = {'mathtext.default': 'regular' }          
    plt.rcParams.update(params)
    plt.pcolormesh(current * (1/14), frequency/1e9, amplitude, vmin=v_min, vmax=v_max)
    cbar = plt.colorbar()
    cbar.set_label("$S_{11}$ (Normalised Amplitude)")
    plt.xlabel('$\\mu_o$ $H_0$ /T')
    plt.ylabel('Frequency /GHz')
    plt.savefig('saved_plots/Testing_plot.png', transparent=False)


def background_separation(sample_amplitude, background_amplitude):
    """
    Converts signal to decibels after removing background noise.
    """
    return ((sample_amplitude * background_amplitude) / (sample_amplitude[0] * background_amplitude[0]))


def functionality(*filenames, vmin, vmax, background_removal):
    """
    Takes in a filename, reads the corresponding h5 file.
    Assigns current, frequency and amplitude to their own arrays.
    Depending on whether background removal is desired, contour plot is created accordingly.
    Inputs-
    filenames: paths to .h5 files, type = string
    background_removal: Toggles whether background removal is desired, type = bool
    """
    
    h5_files = read_and_scan(*filenames)# calling own function for reading h5 files
    sample = current_frequency_amplitude(h5_files[0]) #only sample file, not background

    #separating components into separate arrays
    current, frequency, sample_amplitude = sample['current'], sample['frequency'], sample['amplitude']
    
    if background_removal:
        background_amplitude = current_frequency_amplitude(h5_files[1])['amplitude']
        foreground_amplitude = background_separation(sample_amplitude, background_amplitude)
        contour_plot(current, frequency, normalise_array(foreground_amplitude), vmin, vmax)
    
    else:
        normalised_amplitude = normalise_array(sample_amplitude)
        contour_plot(current,frequency, normalised_amplitude)
        
    return


def parse_arguments():
    """
    This allows file paths and other parameters to be passed through the command line
    """
    parser = argparse.ArgumentParser(description = 'Run FMR Data Analysis')
    
    parser.add_argument(
        '-sample_name',
        metavar='sample_path',
        type = str,
        help = 'The path to sample .h5 file')
    
    parser.add_argument(
        '-background_name',
        metavar='background_path',
        type = str,
        help = 'The path to background .h5 file',
        default='no_sample.h5')

    parser.add_argument(
        '-vmin',
        type = float,
        default = '-2.5',
        help = 'The minimum of the amplitude scale'
    )

    parser.add_argument(
        '-vmax',
        type = float,
        default = '0.7',
        help = 'The maximum of the amplitude scale'
    )
    
    parser.add_argument('--background_removal', default=False, action='store_true')

    return parser.parse_args()



def main():
    args = parse_arguments()
    file_paths = {
        'sample' : args.sample_name,
        'background' : args.background_name
    }
    
    functionality(*file_paths.values(), vmin = args.vmin, vmax = args.vmax, background_removal = args.background_removal)



if __name__ == '__main__':
    main()