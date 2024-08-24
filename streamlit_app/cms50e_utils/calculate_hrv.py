import neurokit2 as nk
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('app.log'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

def calculate_hrv(pulse_rates_input, sampling_rate=60):
    try:
        # Check if input is a string, if so, convert it to a list of floats
        if isinstance(pulse_rates_input, str):
            pulse_rates = np.array([float(rate) for rate in pulse_rates_input.split(',')])
        elif isinstance(pulse_rates_input, list):
            pulse_rates = np.array(pulse_rates_input, dtype=float)
        else:
            raise ValueError("Invalid input type for pulse_rates. Expected string or list.")

        if len(pulse_rates) == 0:
            raise ValueError("No pulse rates provided.")

        # Handle any zero or very small pulse rates to prevent division by zero
        pulse_rates = np.clip(pulse_rates, 1e-5, None)

        # Convert pulse rates (BPM) to RR intervals (in seconds)
        rr_intervals = 60.0 / pulse_rates  # RR intervals in seconds

        # Convert RR intervals to peak indices
        peak_indices = nk.intervals_to_peaks(rr_intervals, sampling_rate=sampling_rate)
        
        # Convert peak_indices to DataFrame if it is not already one
        if isinstance(peak_indices, np.ndarray):
            peak_indices = nk.data_to_dataframe(peak_indices, columns=['Peak'])

        if peak_indices.empty:
            raise ValueError("No peaks detected in RR intervals.")
        
        # Calculate HRV using the peak indices
        hrv = nk.hrv_time(peak_indices, sampling_rate=sampling_rate, show=False)

        if hrv.empty:
            raise ValueError("HRV calculation returned an empty DataFrame.")
        
        # Extract HRV metrics
        rmssd = hrv["HRV_RMSSD"].iloc[0] if not hrv["HRV_RMSSD"].empty else 0.0
        sdnn = hrv["HRV_SDNN"].iloc[0] if not hrv["HRV_SDNN"].empty else 0.0
        
        return rmssd, sdnn
    except Exception as e:
        logger.error(f"Error calculating HRV: {e}")
        return 0.0, 0.0
