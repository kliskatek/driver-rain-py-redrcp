# redrcp

[![PyPI - Version](https://img.shields.io/pypi/v/redrcp)](https://pypi.org/project/redrcp)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/redrcp)](https://pypi.org/project/redrcp)
![OS](https://img.shields.io/badge/os-windows%20|%20linux-blue)

-----
*Python driver for Phychips RED-RCP UHF RFID readers*
## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Connect to the reader](#connect-to-the-reader)
  - [Get basic information about the reader](#get-basic-information-about-the-reader)
  - [Configure the reader](#configure-the-reader)
  - [Perform continuous asynchronous inventory](#perform-continuous-asynchronous-inventory)
  - [Execute Read/Write operations](#execute-readwrite-operations)
- [License](#license)

## Installation

```console
pip install redrcp
```

## Usage
### Connect to the reader
```python
# Create driver
reader = RedRcp()

# Connect
reader.connect(connection_string='COM3')

... use the reader ...

# Disconnect reader
reader.disconnect()
```

### Get basic information about the reader
```python
manufacturer = reader.get_info_manufacturer()
fw_version = reader.get_info_fw_version()
model = reader.get_info_model()
details = reader.get_info_detail()
```
Sample response values:

````
manufacturer = 'PHYCHIPS'
````
````
fw_version = 'v2.3.0'
````
````
model = 'RED4S-SKR'
````
````
details = ArgumentsReaderInformationDetail(TODO)
````


### Configure the reader

```python

# Set TX power level
logging.info('Setting max TX power')
reader.set_tx_power(details.max_tx_power)
tx_power: float = reader.get_tx_power()
```

### Perform continuous asynchronous inventory

```python
# Define callback
def notification_callback(tag: NotificationTpeCuiii):
    logging.info(tag)


# Configure the callback
reader.set_notification_callback(notification_callback=notification_callback)


# Start inventory stream
reader.start()

# Do other stuff
time.sleep(.5)

# Stop inventory stream
reader.stop()
```
Sample report:

`
NotificationTpeCuiii(TODO)
`

### Execute Read/Write operations
```python
reader.write(epc='010203040506070809101112',  # or bytearray
             target_memory=ParamMemory.USER, 
             word_pointer=0, 
             data='1234')  # or bytearray

data: bytearray = reader.read(epc='010203040506070809101112', # or bytearray
                              target_memory=ParamMemory.USER, 
                              word_pointer=0, 
                              word_count=1)
```

## License

`redrcp` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
