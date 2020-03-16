# folding-power-control
Control Folding@Home activity based on Swedish hourly electricity pricing

## Install
Python 3.6+

```bash
pip install -r requirements.txt
```

## Configure

### Values
1. Set area applicable to your electricity consumption
2. Set desired cut-off spot price above which Folding@Home should pause
3. Set Folding@Home address, port, and GPU/CPU slots

### Automate
```bash
sudo touch /var/log/fah-power-control.log
sudo chmod 777 /var/log/fah-power-control.log
0 * * * * /path/to/envs/bin/python /path/to/fah-power-control.py >> /var/log/fah-power-control.log 2>&1
```