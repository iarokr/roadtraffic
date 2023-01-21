# roadtraffic

![PyPI](https://img.shields.io/pypi/v/roadtraffic)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/roadtraffic)
![PyPI - Format](https://img.shields.io/pypi/format/roadtraffic)


## Overview

The [roadtraffic](https://pypi.org/project/roadtraffic/) Python package for traffic data processing and fundamental diagram estimation. A fundamental diagram is estimated using convex quantile regression with the help of the [pyStoNED](https://github.com/ds2010/pyStoNED) package. The [mosek](https://www.mosek.com/) solver is used for the estimation. For the academic purposes, you can obtain a [free academic license](https://www.mosek.com/products/academic-licenses/) for the solver.

Currently only data from Finnish roads, collected through this package is supported. The source of data is [Fintraffic / digitraffic.fi](https://www.digitraffic.fi/en/), license CC 4.0 BY.

The package works with the raw data. The data could be aggregated across time and road direction/lane. The agreggated data is then bagged for the computational efficiency. The estimation of the fundamental diagram is done on the bagged data. Raw data availability depends on traffic measurement station. The earliest data comes from year 1995. New data becomes available every day at 3 am (Helsinki Time zone). Developers of the package are not affiliated with Fintraffic and can't influence neither the availability of data nor its quality.

This package is a part of my PhD journey - you can follow it on my [personal website](https://iaroslavkriuchkov.com).

## NOTE

The package is in the initial development stage, and it will be upgraded as my research journey progresses. Feedback, suggestion and comments are highly appreciated as well as the bug reports! For now, you can send me an [e-mail](mailto:iaroslav.kriuchkov@aalto.fi). The contribution will be set up later. 

## Installation
The installation of the package is avalable through the PyPI:
```shell
    pip install roadtraffic
```

## Basic usage
The package offers an opportunity to work with Finnish traffic data. You can select a traffic measurement station (TMS or LAM, in Finnish) from the official [metadata](https://tie.digitraffic.fi/api/tms/v1/stations) using *tmsNumber* field or the [map](https://www.arcgis.com/home/webmap/viewer.html?webmap=10d97c7d9d9b41c180e6eb7e26f75be7) taking the integer part or *lamid* field. 

Let's take as an example the traffic management station number 162, located on Kehä II in Espoo, Finland and load, process and vizualize the data for September 10-20, 2019.
```python
# Import dependencies
import roadtraffic
from roadtraffic import fintraffic 

# Traffic measurement station of interest
tms_id = 162

# Initiate the list of days of interest (Sep 10-20, 2019)
days_list = [
    [2019, 253],
    [2019, 254],
    [2019, 255],
    [2019, 256],
    [2019, 257],
    [2019, 258],
    [2019, 259],
    [2019, 260],
    [2019, 261],
    [2019, 262],
    [2019, 263],
]

# Specify the road direction
# Information about the direction could be obtained from the metadata or the map
direction = 2

# Initiate the class for Fintraffic data
tms = fintraffic.FintrafficTMS(tms_id, days_list, direction)

# Load raw data for the selected period
tms.load_raw_data()

# Aggregate data
tms.aggregate_lane()

# Plot data
tms.plot_data(fintraffic.Representations.agg)
```



## Authors
- [Iaroslav Kriuchkov](https://iaroslavkriuchkov.com), Doctoral Researcher at Aalto University, Finland
- [Timo Kuosmanen](https://www.researchgate.net/profile/Timo-Kuosmanen), Professor at Turku University School of Economics, Finland

## License

roadtraffic is licensed under the GNU GPLv3 License - see the [LICENSE](LICENSE) file for details


