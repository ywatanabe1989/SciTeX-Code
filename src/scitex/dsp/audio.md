<!-- ---
!-- title: ./scitex_repo/src/scitex/dsp/audio.md
!-- author: ywatanabe
!-- date: 2024-11-08 09:20:07
!-- --- -->


## Audio Support
``` bash
sudo apt remove python3-pyaudio
sudo apt-get install -y libasound2-dev portaudio19-dev libportaudio2
pip install --no-cache-dir pyaudio

sudo apt-get install -y alsa-utils
speaker-test -t sine -f 440

sudo apt-get update
sudo apt-get install -y pulseaudio
sudo usermod -aG audio $USER
pulseaudio --start

```
