import logging

# Configure logging
logger = logging.getLogger(__name__)

def decode_data(raw_data):
    logger.debug(f"Decoding raw data: {raw_data}")
    try:
        # Extract timestamp and data
        timestamp = raw_data[:10]  # Assuming timestamp is first 10 characters
        data = raw_data[10:]

        # Remove any trailing junk data
        data = data.rstrip('f')

        # Split data into chunks based on delimiter
        data_chunks = data.split('ffff')
        if data_chunks[-1] == '':
            data_chunks.pop()  # Remove empty chunk if present

        ppg_data, pulse_rates, spo2_levels = [], [], []

        for chunk in data_chunks:
            byte_list = [chunk[i:i+2] for i in range(0, len(chunk), 2)]
            if len(byte_list) >= 7:
                ppg = int(byte_list[4], 16) & 0x7f
                pulse_rate = int(byte_list[5], 16) & 0x7f
                spo2_level = int(byte_list[6], 16) & 0x7f
                
                ppg_data.append(ppg)
                pulse_rates.append(pulse_rate)
                spo2_levels.append(spo2_level)

        ppg_data_str = ', '.join(map(str, ppg_data))
        logger.debug(f"Decoded data - Timestamp: {timestamp}, PPG Data: {ppg_data_str}, Pulse Rates: {pulse_rates}, SpO2 Levels: {spo2_levels}")
        return timestamp, ppg_data_str, pulse_rates, spo2_levels

    except Exception as e:
        logger.error(f"Error decoding data: {e}")
        return "", "", [], []
