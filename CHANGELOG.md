# Changelog

All notable changes to the `roadtraffic` project will be documented in this file.

## [Unreleased]

- Add full documentation for the package
- Add plotting functionality
- Add support for other data sources

## [1.0.1]

### Added

- Aggregation for lanes is added
- During raw data cleaning lanes for TMS 10, 11, 109, 116, 118, 126, 145, 146, 147, 148, 149 are cleaned automatically
  for the selected road direction, lane values are available in `roadtraffic.utils.constants.LANES`
- plots module added:
    - Plotting the timeline - flow, density, speed against time
    - Plotting the fundamental relationship - any pair of flow, density, speed
- Estimation with contextual variable is possible

### Fixed

- The aggregation for time periods measured in seconds is fixed

## [1.0.0] - 2023-12-04

### Added

- Estimation for the mean is added
- Estimation with penalties (L1 norm, L2 norm and Lipschitz norm) is added

### Changed

- Classes of data are introduced:
    - Raw data, which contains information on individual vehicles
    - Aggregated data, which contains information on time and/or lane aggregated traffic
    - Bagged data, which contains information on the bagged data

### Fixed

- The link to the raw data source is updated as Fintraffic introduced new API

## [0.0.1] - 2023-01-21

### Added

- Initial release