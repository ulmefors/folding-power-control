# folding-power-control
Control Folding@Home activity based on Swedish hourly electricity pricing

### Install
```bash
pip install -r requirements.txt
```

### Crontab
```bash
0 * * * * /path/to/envs/bin/python /path/to/fah-power-control.py >> /var/log/fah-power-control.log 2>&1
```