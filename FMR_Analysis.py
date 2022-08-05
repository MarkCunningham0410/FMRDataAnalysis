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


def read_h5_files(*filenames):
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


def contour_plot(current, frequency, amplitude, v_min = -2.5, v_max = 0.7, plot_filename = 'new_plot'):
    """
    Returns contour plot of Frequency, Current and Amplitude
    """
    params = {'mathtext.default': 'regular' }          
    plt.rcParams.update(params)
    plt.pcolormesh(current * (1/14), frequency/1e9, amplitude, vmin=v_min, vmax=v_max, cmap = 'magma_r')
    cbar = plt.colorbar()
    plt.title('Sample 3', fontsize=15)
    cbar.set_label("$S_{11}$ (Normalised Amplitude)", fontsize=15)
    plt.xlabel('$\\mu_o$ $H_0$ (T)', fontsize = 15)
    plt.xticks(fontsize=15)
    plt.ylabel('Frequency (GHz)', fontsize = 15)
    plt.yticks(fontsize=15)
    plt.savefig(f'saved_plots/{plot_filename}.png',bbox_inches = 'tight',  transparent=False)


def background_separation(sample_amplitude, background_amplitude):
    """
    Converts signal to decibels after removing background noise.
    """
    return ((sample_amplitude * background_amplitude) / (sample_amplitude[0] * background_amplitude[0]))


def functionality(*filenames, vmin, vmax, plot_name, background_removal):
    """
    Takes in a filename, reads the corresponding h5 file.
    Assigns current, frequency and amplitude to their own arrays.
    Depending on whether background removal is desired, contour plot is created accordingly.
    Inputs-
    filenames: paths to .h5 files, type = string
    vmin, vmax: scales of amplitude axis in resulting plot, type = float
    plot_name: name of output plot .png, type = string
    background_removal: Toggles whether background removal is desired, type = bool
    """
    
    fmr_datasets = read_h5_files(*filenames) # calling own function for reading h5 files
    sample = current_frequency_amplitude(fmr_datasets[0]) # only sample file, not background

    # separating components into separate arrays
    current, frequency, sample_amplitude = sample['current'], sample['frequency'], sample['amplitude']
    
    if background_removal:
        background_amplitude = current_frequency_amplitude(fmr_datasets[1])['amplitude']
        normalised_amplitude = normalise_array(background_separation(sample_amplitude, background_amplitude))
    
    else:
        normalised_amplitude = normalise_array(sample_amplitude)
    
    contour_plot(current,frequency, normalised_amplitude, vmin, vmax, plot_name)
        
    return


def parse_arguments():
    """
    This allows file paths and other parameters to be passed through the command line
    """
    parser = argparse.ArgumentParser(description = 'Run FMR Data Analysis')
    
    parser.add_argument(
        '-sample_name',
        type = str,
        help = 'The path to sample .h5 file'
    )
    
    parser.add_argument(
        '-background_name',
        type = str,
        help = 'The path to background .h5 file',
        default='upside down sample 1 to 15GHz -4 to 4 A.h5'
    )

    parser.add_argument(
        '-output_name',
        type = str,
        help = 'The name of output matplotlib contour plot .png',
        default='new_plot'
    )

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
    
    parser.add_argument(
        '--background_removal',
        default=False, 
        action='store_true'
    )

    return parser.parse_args()


def main():
    args = parse_arguments()
    file_paths = {
        'sample' : args.sample_name,
        'background' : args.background_name
    }
    
    functionality(
        *file_paths.values(),
        vmin = args.vmin,
        vmax = args.vmax,
        background_removal = args.background_removal,
        plot_name = args.output_name
    )



if __name__ == '__main__':
    main()