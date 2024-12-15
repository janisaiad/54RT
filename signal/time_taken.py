#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from gnuradio import gr
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
import osmosdr
import time
from datetime import datetime, timedelta
import csv
import os

class SignalRecorder(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "Signal Recorder")

        # Parameters
        self.samp_rate = 2e6      
        self.freq_start = 380e6   
        self.freq_end = 410e6    
        self.gain = 40
        
        # RTL-SDR Source
        self.source = osmosdr.source(args="numchan=" + str(1) + " " + "rtl=0")
        self.source.set_sample_rate(self.samp_rate)
        self.source.set_center_freq((self.freq_start + self.freq_end) / 2)
        self.source.set_gain(self.gain)
        self.source.set_if_gain(20)
        self.source.set_bb_gain(20)
        self.source.set_antenna("")

        # Complex probe
        self.probe = blocks.probe_signal_c()

        # Connect source to probe
        self.connect(self.source, self.probe)

    def get_signal_data(self):
        """Get complex signal data"""
        return self.probe.level()

def write_to_csv(timestamp, signal_value):
    """Write signal data to CSV file"""
    file_exists = os.path.isfile('signal_data.csv')
    
    with open('signal_data.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'real', 'imag', 'magnitude'])
        
        real = np.real(signal_value)
        imag = np.imag(signal_value)
        magnitude = np.abs(signal_value)
        writer.writerow([timestamp.isoformat(), real, imag, magnitude])

def main():
    print("=== RTL-SDR Signal Recording ===")
    print(f"Frequency range: {380}-{410} MHz")
    print(f"Sample rate: 2 MHz")
    print("Recording 30 seconds every minute")
    
    # Create recorder
    tb = SignalRecorder()
    recording = False
    
    try:
        while True:
            print("\nStarting 30 second recording...")
            tb.start()
            recording = True
            
            # Record for 30 seconds
            start_time = time.time()
            while time.time() - start_time < 30:
                signal_value = tb.get_signal_data()
                write_to_csv(datetime.now(), signal_value)
                time.sleep(0.001)  # Small delay to prevent overwhelming the system
                
            tb.stop()
            tb.wait()
            recording = False
            
            print("Recording complete, waiting for next minute...")
            
            # Wait until start of next minute
            next_minute = (datetime.now().replace(second=0, microsecond=0) + 
                         timedelta(minutes=1))
            time.sleep((next_minute - datetime.now()).total_seconds())
            
    except KeyboardInterrupt:
        print("\nUser requested stop")
    finally:
        print("\nStopping recorder...")
        if recording:
            tb.stop()
            tb.wait()
        print("Recording completed.")

if __name__ == '__main__':
    main()
