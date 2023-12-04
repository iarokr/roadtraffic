# roadtraffic

![PyPI](https://img.shields.io/pypi/v/roadtraffic)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/roadtraffic)
![Build](https://img.shields.io/github/actions/workflow/status/iarokr/roadtraffic/publish-roadtraffic.yml)



## Overview

The [roadtraffic](https://pypi.org/project/roadtraffic/) Python package for traffic data processing and fundamental diagram estimation. A fundamental diagram is estimated using convex regression with the help of the [pyStoNED](https://github.com/ds2010/pyStoNED) package. The [mosek](https://www.mosek.com/) solver is used for the estimation. For the academic purposes, you can obtain a [free academic license](https://www.mosek.com/products/academic-licenses/) for the solver. You can also use the free NEOS server for the estimation, but the computational time will be longer.

Currently only data from Finnish roads, collected through this package is supported. The source of data is [Fintraffic / digitraffic.fi](https://www.digitraffic.fi/en/), license CC 4.0 BY.

The package works on the raw data. The data can be aggregated over time and road direction/lane. The aggregated data is then bagged for computational efficiency. The estimation of the fundamental diagram is done on the bagged data. The availability of raw data depends on the traffic measurement station. The earliest data are from 1995. New data are available every day at 3 am (Helsinki time zone). The developers of the package are not affiliated with Fintraffic and can't influence the availability or quality of the data.

## Installation
The installation of the package is avalable through the PyPI:
```shell
    pip install roadtraffic
```

## Basic usage
The package offers an opportunity to work with Finnish traffic data. You can select a traffic measurement station (TMS or LAM, in Finnish) from the official [metadata](https://tie.digitraffic.fi/api/tms/v1/stations) using *tmsNumber* field or the [map](https://liikennetilanne.fintraffic.fi/kartta/?lang=fi&x=3010000&y=9720000&z=5&checkedLayers=1,10&basemap=streets-vector) taking the integer part or *lamid* field. 

Let's take as an example the traffic management station number 162, located on Kehä II in Espoo, Finland and load, process the data and estimate the model for September 10-11, 2019.
```python
# Import dependencies
from roadtraffic import fintraffic 

# Traffic measurement station of interest
tms_id = 162

# Initiate the list of days (tuples) of interest (Sep 10-11, 2019)
days_list = [
    (2019, 253),
    (2019, 254),
]

# Specify the road direction
# Information about the direction could be obtained from the metadata or the map
direction = 1

# Initiate the class for Fintraffic data
tms = fintraffic.TrafficMeasurementStation(tms_id, days_list)

# Load raw data for the selected period
tms.raw.load()

# Clean data for the direction
tms.raw.clean(direction=direction)

# Aggregate data
tms.raw_to_agg(aggregation_time_period='5', aggregation_time_period_unit='min')

# Bag data
tms.agg_to_bag(num_bags_density=40, num_bags_flow=200)

# Estimate the model for the median
tms.bag.estimate_model("quantile", [0.5], email="test@test.test") # you can specify your email to receive the log file

# Obtain the results
tms.bag.models.get_estimate(0.5)

# Estimate the model for the mean
tms.bag.estimate_model("mean", email="test@test.test")

# Obtain the results
tms.bag.models.get_estimate("mean")

```



## Authors
- [Iaroslav Kriuchkov](https://www.researchgate.net/profile/Iaroslav-Kriuchkov-3), Doctoral Researcher at Aalto University School of Business, Finland
- [Timo Kuosmanen](https://www.researchgate.net/profile/Timo-Kuosmanen), Professor at Turku University School of Economics, Finland

## License

roadtraffic is licensed under the GNU GPLv3 License - see the [LICENSE](LICENSE) file for details


