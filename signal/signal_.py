#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from gnuradio import gr
from gnuradio import blocks
from gnuradio import fft
from gnuradio import filter
from gnuradio.fft import window
import osmosdr
import time
from datetime import datetime
import csv
import os

class SignalCapture(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "Signal Capture")

        # Parameters
        self.samp_rate = 2e6      
        self.freq_start = 800e3   
        self.freq_end = 1050e3    
        self.gain = 40
        
        center_freq = (self.freq_start + self.freq_end) / 2
        bandwidth = self.freq_end - self.freq_start
        
        # RTL-SDR Source
        self.source = osmosdr.source(args="numchan=" + str(1) + " " + "rtl=0")
        self.source.set_sample_rate(self.samp_rate)
        self.source.set_center_freq(center_freq)
        self.source.set_gain(self.gain)
        self.source.set_if_gain(20)
        self.source.set_bb_gain(20)
        self.source.set_antenna("")
        self.source.set_dc_offset_mode(0)

        # Bandpass filter
        band_pass_taps = filter.firdes.band_pass(
            1.0,                  # Gain
            self.samp_rate,      # Sampling rate
            1000,                # Low cutoff
            self.samp_rate/2.1,  # High cutoff
            self.samp_rate/10,   # Transition width
            window.WIN_HAMMING   # Window type
        )
        
        self.band_pass = filter.fir_filter_ccf(1, band_pass_taps)
        
        # Probe to capture signal
        self.probe = blocks.probe_signal_c()

        # Connect blocks
        self.connect(self.source, self.band_pass, self.probe)

    def get_signal(self):
        """Get complex signal data"""
        return self.probe.level()

def capture_signal(duration=60, csv_file="signal_data.csv"):
    """Capture signal for specified duration and save to CSV"""
    print(f"=== Capturing signal for {duration} seconds ===")
    print(f"Frequencies: {800}-{1050} kHz")
    
    tb = SignalCapture()
    signal_data = []
    
    print("Starting capture...")
    tb.start()
    
    start_time = time.time()
    
    try:
        while (time.time() - start_time) < duration:
            # Get signal sample
            sample = tb.get_signal()
            timestamp = datetime.now().isoformat()
            
            signal_data.append({
                'timestamp': timestamp,
                'real': sample.real,
                'imag': sample.imag,
                'magnitude': abs(sample)
            })
            
            # Small delay to avoid CPU overload
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        print("\nUser requested stop")
    finally:
        print("Stopping capture...")
        tb.stop()
        tb.wait()
    
    # Save results
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'real', 'imag', 'magnitude'])
        writer.writeheader()
        writer.writerows(signal_data)
    
    print(f"\nCapture complete")
    print(f"Number of samples: {len(signal_data)}")
    print(f"Results saved to: {csv_file}")

if __name__ == '__main__':
    capture_signal(duration=60)  # 60 seconds capture
