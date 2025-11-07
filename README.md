# deconto21-ais

An application producing sea level projections by directly sampling the Antarctic ice sheet ensembles of Deconto et al. (2021). 

## Example

This application can run on emissions-projected climate data. For example, you can use the output `climate.nc` file from the [fair model container](https://github.com/fact-sealevel/fair-temperature). Additional input data is located in this repository.

### Setup

Clone the repository and create directories to hold input and output data. 

```shell
mkdir -p ./data/input
curl -sL https://zenodo.org/record/7478192/files/deconto21_AIS_preprocess_data.tgz | tar -zx -C ./data/input
# Fingerprint input data for postprocessing step
curl -sL https://zenodo.org/record/7478192/files/grd_fingerprints_data.tgz | tar -zx -C ./data/input

#Make directory for inputs
mkdir -p ./data/output
# Add location file to input dir 
echo "New_York	12	40.70	-74.01" > ./data/input/location.lst
```

Then, run the container associated with the package, passing the necessary arguments to the CLI tool:

```shell
docker run --rm \
-v ./data/input:/mnt/deconto_data_in:ro \
-v ./data/output:/mnt/deconto_data_out \
ghcr.io/fact-sealevel/deconto21-ais:edge \
--input-eais-rcp26-file /mnt/deconto_data_in/dp21_eais_rcp26.nc \
--input-eais-rcp45-file /mnt/deconto_data_in/dp21_eais_rcp45.nc \
--input-eais-rcp85-file /mnt/deconto_data_in/dp21_eais_rcp85.nc \
--input-wais-rcp26-file /mnt/deconto_data_in/dp21_wais_rcp26.nc \
--input-wais-rcp45-file /mnt/deconto_data_in/dp21_wais_rcp45.nc \
--input-wais-rcp85-file /mnt/deconto_data_in/dp21_wais_rcp85.nc \
--nsamps 500 --pyear-start 2020 --pyear-end 2150 \
--pyear-step 10 --baseyear 2000 --replace True \
--locationfile  /mnt/deconto_data_in/location.lst \
--rngseed 1342 --pipeline-id MY_PIPELINE_ID \
--fpdir  /mnt/deconto_data_in/FPRINT \
--output-wais-lslr-file  /mnt/deconto_data_out/wais_lslr.nc \
--output-eais-lslr-file /mnt/deconto_data_out/eais_lslr.nc \
--output-ais-lslr-file /mnt/deconto_data_out/ais_lslr.nc \
--output-wais-gslr-file /mnt/deconto_data_out/wais_gslr.nc \
--output-eais-gslr-file /mnt/deconto_data_out/eais_gslr.nc \
--output-ais-gslr-file /mnt/deconto_data_out/ais_gslr.nc
```

## Features

Several options and configurations are available when running the container.

```shell
Usage: deconto21-ais [OPTIONS]

  Run the DP21 ice sheet workflow.

Options:
  --scenario TEXT               Emission scenario for ice sheet projections
  --baseyear INTEGER            Base year for ice sheet projections
  --climate-data-file TEXT      NetCDF4/HDF5 file containing surface
                                temperature data
  --input-eais-rcp26-file TEXT  Input EAIS RCP2.6 data file  [required]
  --input-eais-rcp45-file TEXT  Input EAIS RCP4.5 data file  [required]
  --input-eais-rcp85-file TEXT  Input EAIS RCP8.5 data file  [required]
  --input-wais-rcp26-file TEXT  Input WAIS RCP2.6 data file  [required]
  --input-wais-rcp45-file TEXT  Input WAIS RCP4.5 data file  [required]
  --input-wais-rcp85-file TEXT  Input WAIS RCP8.5 data file  [required]
  --nsamps INTEGER              Number of samples to draw from the ice sheet
                                model ensemble
  --pyear-start INTEGER         Start year for ice sheet projections
  --pyear-end INTEGER           End year for ice sheet projections
  --pyear-step INTEGER          Year step for ice sheet projections
  --replace BOOLEAN             Whether to sample with replacement from the
                                ice sheet model ensemble
  --rngseed INTEGER             Random number generator seed for ice sheet
                                model sampling
  --locationfile TEXT           File that contains name, id, lat, and lon of
                                points for localization
  --chunksize INTEGER           Number of locations to process at a time
  --pipeline-id TEXT            Unique identifier for this instance of the
                                module
  --fpdir TEXT                  Directory containing ice sheet fingerprints
  --output-ais-gslr-file TEXT        Output file for AIS global sea level rise
                                projections
  --output-eais-gslr-file TEXT       Output file for EAIS global sea level rise
                                projections
  --output-wais-gslr-file TEXT       Output file for WAIS global sea level rise
                                projections
  --output-ais-lslr-file TEXT        Output file for AIS local sea level rise
                                projections
  --output-eais-lslr-file TEXT       Output file for EAIS local sea level rise
                                projections
  --output-wais-lslr-file TEXT       Output file for WAIS local sea level rise
                                projections
  --help                        Show this message and exit.
```

See this help documentation by passing the `--help` flag when running the application, for example:
```shell
docker run --rm deconto21-ais --help
```

## Building the container locally
You can build the container with Docker by running the following command from the repository root:

```shell
docker build -t deconto21-ais . 
```

## Results 
If this module runs successfully, a NetCDF file will be written containing local and global sea level projections based on contributions from the western Antarctic Ice Sheet (WAIS), eastern Antarctic Ice Sheet (EAIS) and the Antarctic Ice Sheet as a whole (AIS). These will be written to `./data/output`. 

## Support
Source code is available online at https://github.com/fact-sealevel/deconto21-ais. This software is open source, available under the MIT license.

Please file issues in the issue tracker at https://github.com/fact-sealevel/deconto21-ais/issues.

