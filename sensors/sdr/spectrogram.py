.
(base) janis@Legion:/mnt/c/Users/maros$ ssh rpi@169.254.72.10
rpi@169.254.72.10's password:
Linux raspberrypi 6.6.31+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.6.31-1+rpt1 (2024-05-29) aarch64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Thu Jul  4 10:47:13 2024 from 169.254.244.48
(base) rpi@raspberrypi:~ $ ls
radioconda  radioconda-2024.05.29-Linux-aarch64.sh  sdr_packages  spectrum_analysis.md  tetra
(base) rpi@raspberrypi:~ $ cd tetra
(base) rpi@raspberrypi:~/tetra $ ls
npy  png  spectrogram  spectrogram.py  spectrum_analysis.md  test.py  tetra2.py  tetra.py  tetra_to_npy.py
(base) rpi@raspberrypi:~/tetra $ cd png
(base) rpi@raspberrypi:~/tetra/png $ ls
(base) rpi@raspberrypi:~/tetra/png $ cd -
/home/rpi/tetra
(base) rpi@raspberrypi:~/tetra $ ls
npy  png  spectrogram  spectrogram.py  spectrum_analysis.md  test.py  tetra2.py  tetra.py  tetra_to_npy.py
(base) rpi@raspberrypi:~/tetra $ rm -rf spectrogram.py
(base) rpi@raspberrypi:~/tetra $ touch spectrogram.py
(base) rpi@raspberrypi:~/tetra $ nano spectrogram.py
(base) rpi@raspberrypi:~/tetra $ python spectrogram.py
=== Analyseur de Spectre RTL-SDR - Bande AM ===
Plage: 800-1050 kHz
Taux d'échantillonnage: 2 MHz
gr-osmosdr 0.2.0.0 (0.2.0) gnuradio 3.10.10.0
built-in source types: file fcd rtl rtl_tcp uhd miri hackrf bladerf rfspace airspy airspyhf soapy redpitaya
Using device #0 Realtek RTL2838UHIDIR SN: 00000001
Found Rafael Micro R820T tuner
Enabled direct sampling mode, input 2
Exact sample rate is: 2000000.052982 Hz
Démarrage de l'analyse...

Acquisition du spectrogramme...
....^C
Arrêt demandé par l'utilisateur
Arrêt de l'analyseur...
Terminé.
(base) rpi@raspberrypi:~/tetra $ nano spectrogram.py
(base) rpi@raspberrypi:~/tetra $ python spectrogram.py
=== Analyseur de Spectre RTL-SDR - Bande AM ===
Plage: 800-1050 kHz
Taux d'échantillonnage: 2 MHz
gr-osmosdr 0.2.0.0 (0.2.0) gnuradio 3.10.10.0
built-in source types: file fcd rtl rtl_tcp uhd miri hackrf bladerf rfspace airspy airspyhf soapy redpitaya
Using device #0 Realtek RTL2838UHIDIR SN: 00000001
Found Rafael Micro R820T tuner
Enabled direct sampling mode, input 2
Exact sample rate is: 2000000.052982 Hz
Démarrage de l'analyse...

Acquisition du spectrogramme...
.........................................................................^C
Arrêt demandé par l'utilisateur
Arrêt de l'analyseur...
Terminé.
(base) rpi@raspberrypi:~/tetra $ ls
npy  png  spectrogram  spectrogram.py  spectrum_analysis.md  test.py  tetra2.py  tetra.py  tetra_to_npy.py
(base) rpi@raspberrypi:~/tetra $ cd spectrogram/
(base) rpi@raspberrypi:~/tetra/spectrogram $ ls
(base) rpi@raspberrypi:~/tetra/spectrogram $ cd -
/home/rpi/tetra
(base) rpi@raspberrypi:~/tetra $ ls
npy  png  spectrogram  spectrogram.py  spectrum_analysis.md  test.py  tetra2.py  tetra.py  tetra_to_npy.py
(base) rpi@raspberrypi:~/tetra $ rm -rf spectrogram.py
(base) rpi@raspberrypi:~/tetra $ touch spectrogram.py
(base) rpi@raspberrypi:~/tetra $ nano spectrogram.py
(base) rpi@raspberrypi:~/tetra $ python spectrogram.py
=== Analyseur de Spectre FFT - Bande AM ===
gr-osmosdr 0.2.0.0 (0.2.0) gnuradio 3.10.10.0
built-in source types: file fcd rtl rtl_tcp uhd miri hackrf bladerf rfspace airspy airspyhf soapy redpitaya
Using device #0 Realtek RTL2838UHIDIR SN: 00000001
Found Rafael Micro R820T tuner
Enabled direct sampling mode, input 2
Exact sample rate is: 2000000.052982 Hz
/home/rpi/tetra/spectrogram.py:219: UserWarning: frames=None which we can infer the length of, did not pass an explicit *save_count* and passed cache_frame_data=True.  To avoid a possibly unbounded cache, frame data caching has been disabled. To suppress this warning either pass `cache_frame_data=False` or `save_count=MAX_FRAMES`.
  ani = FuncAnimation(
Traceback (most recent call last):
  File "/home/rpi/tetra/spectrogram.py", line 251, in <module>
    main()
  File "/home/rpi/tetra/spectrogram.py", line 219, in main
    ani = FuncAnimation(
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/animation.py", line 1695, in __init__
    super().__init__(fig, **kwargs)
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/animation.py", line 1417, in __init__
    super().__init__(fig, event_source=event_source, *args, **kwargs)
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/animation.py", line 888, in __init__
    self._setup_blit()
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/animation.py", line 1211, in _setup_blit
    self._post_draw(None, self._blit)
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/animation.py", line 1166, in _post_draw
    self._fig.canvas.draw_idle()
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/backend_bases.py", line 1893, in draw_idle
    self.draw(*args, **kwargs)
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/backends/backend_agg.py", line 388, in draw
    self.figure.draw(self.renderer)
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/artist.py", line 95, in draw_wrapper
    result = draw(artist, renderer, *args, **kwargs)
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/artist.py", line 72, in draw_wrapper
    return draw(artist, renderer)
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/figure.py", line 3164, in draw
    DrawEvent("draw_event", self.canvas, renderer)._process()
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/backend_bases.py", line 1271, in _process
    self.canvas.callbacks.process(self.name, self)
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/cbook.py", line 303, in process
    self.exception_handler(exc)
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/cbook.py", line 87, in _exception_printer
    raise exc
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/cbook.py", line 298, in process
    func(*args, **kwargs)
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/animation.py", line 912, in _start
    self._init_draw()
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/animation.py", line 1749, in _init_draw
    self._draw_frame(frame_data)
  File "/home/rpi/radioconda/lib/python3.10/site-packages/matplotlib/animation.py", line 1768, in _draw_frame
    self._drawn_artists = self._func(framedata, *self._args)
  File "/home/rpi/tetra/spectrogram.py", line 182, in update_plot
    ax.texts.clear()
AttributeError: 'ArtistList' object has no attribute 'clear'
(base) rpi@raspberrypi:~/tetra $; donne moi tout le code en 1 copy pastable