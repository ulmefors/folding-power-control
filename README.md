# folding-power-control
Control [Folding@Home](https://foldingathome.org/) activity based on Swedish hourly electricity pricing.

## Install Folding@Home
Folding@Home clients are available for Linux, Mac and Windows. The script is only tested on Ubuntu but will likely work with minor tweaks on other Linux distributions and MacOS.

### Linux
* [Linux packages](https://foldingathome.org/start-folding/)
* [Linux Installation Guide](https://foldingathome.org/support/faq/installation-guides/linux/)

## Python requirements
Python 3.6+

```bash
pip install -r requirements.txt
```

## Configure

### YAML values
1. Set `area` applicable to your location. Choose one of the supported Swedish regions.
2. Set `price_threshold` as the maximum spot price you are willing to pay. Folding@Home will pause if spot price exceeds this value.
3. Set Folding@Home socket `address` and `port`.
4. Set Folding@Home `config_files` and `slots`. Commands will be sent to the union of all slots found in config files and explicitly declared slots.

### Automate
```bash
$ sudo touch /var/log/cron/fah-power-control.log
$ sudo chmod 777 /var/log/cron/fah-power-control.log
$ crontab -e

# m h dom mon dow command
0 * * * * /path/to/envs/bin/python /path/to/fah-power-control.py >> /var/log/cron/fah-power-control.log 2>&1
```
