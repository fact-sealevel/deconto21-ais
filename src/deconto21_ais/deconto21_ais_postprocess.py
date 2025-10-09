import numpy as np
import os
import time
import argparse
from deconto21_ais.read_locationfile import ReadLocationFile
from deconto21_ais.AssignFP import AssignFP

import xarray as xr
import dask.array as da

""" dp21_postprocess_icesheet.py

This script runs the ice sheet post-processing task for the DP20 workflow. This task
uses the global projections from the 'dp21_project_icesheet' script and applies
spatially resolved fingerprints to the ice sheet contribution. The result is a netCDF4
file that contains spatially and temporally resolved samples of ice sheet contributions
to local sea-level rise

Parameters:
locationfile = File that contains points for localization
pipeline_id = Unique identifer for the pipeline running this code

Output: NetCDF file containing local contributions from ice sheets

"""


def dp21_postprocess_icesheet(
    chunksize,
    pipeline_id,
    projected_dict,
    locationfile,
    fpdir,
    out_ais_lslr_file,
    out_eais_lslr_file,
    out_wais_lslr_file,
):
    waissamps = projected_dict["wais_samps"]
    eaissamps = projected_dict["eais_samps"]
    targyears = projected_dict["targyears"]
    scenario = projected_dict["scenario"]
    baseyear = projected_dict["baseyear"]

    # Load the site locations
    (_, site_ids, site_lats, site_lons) = ReadLocationFile(locationfile)

    # Get some dimension data from the loaded data structures
    nsamps = eaissamps.shape[0]

    # Get the fingerprints for all sites from all ice sheets
    waisfp = da.from_array(
        AssignFP(os.path.join(fpdir, "fprint_wais.nc"), site_lats, site_lons),
        chunks=chunksize,
    )
    eaisfp = da.from_array(
        AssignFP(os.path.join(fpdir, "fprint_eais.nc"), site_lats, site_lons),
        chunks=chunksize,
    )

    # Rechunk the fingerprints for memory
    # waisfp = waisfp.rechunk(chunksize)
    # eaisfp = eaisfp.rechunk(chunksize)

    # Apply the fingerprints to the projections
    waissl = np.multiply.outer(waissamps, waisfp)
    eaissl = np.multiply.outer(eaissamps, eaisfp)

    # Add up the east and west components for AIS total
    aissl = waissl + eaissl

    # Define the missing value for the netCDF files
    nc_missing_value = np.nan  # np.iinfo(np.int16).min

    # Create the xarray data structures for the localized projections
    ncvar_attributes = {
        "description": "Local SLR contributions from icesheets according to DP21 workflow",
        "history": "Created " + time.ctime(time.time()),
        "source": "SLR Framework: DP21 workflow",
        "scenario": scenario,
        "baseyear": baseyear,
    }

    wais_out = xr.Dataset(
        {
            "sea_level_change": (
                ("samples", "years", "locations"),
                waissl,
                {"units": "mm", "missing_value": nc_missing_value},
            ),
            "lat": (("locations"), site_lats),
            "lon": (("locations"), site_lons),
        },
        coords={
            "years": targyears,
            "locations": site_ids,
            "samples": np.arange(nsamps),
        },
        attrs=ncvar_attributes,
    )

    eais_out = xr.Dataset(
        {
            "sea_level_change": (
                ("samples", "years", "locations"),
                eaissl,
                {"units": "mm", "missing_value": nc_missing_value},
            ),
            "lat": (("locations"), site_lats),
            "lon": (("locations"), site_lons),
        },
        coords={
            "years": targyears,
            "locations": site_ids,
            "samples": np.arange(nsamps),
        },
        attrs=ncvar_attributes,
    )

    ais_out = xr.Dataset(
        {
            "sea_level_change": (
                ("samples", "years", "locations"),
                aissl,
                {"units": "mm", "missing_value": nc_missing_value},
            ),
            "lat": (("locations"), site_lats),
            "lon": (("locations"), site_lons),
        },
        coords={
            "years": targyears,
            "locations": site_ids,
            "samples": np.arange(nsamps),
        },
        attrs=ncvar_attributes,
    )

    # Write the netcdf output files
    wais_out.to_netcdf(
        out_wais_lslr_file,
        engine="netcdf4",
        encoding={
            "sea_level_change": {
                "dtype": "f4",
                "zlib": True,
                "complevel": 4,
                "_FillValue": nc_missing_value,
            }
        },
    )
    eais_out.to_netcdf(
        out_eais_lslr_file,
        engine="netcdf4",
        encoding={
            "sea_level_change": {
                "dtype": "f4",
                "zlib": True,
                "complevel": 4,
                "_FillValue": nc_missing_value,
            }
        },
    )
    ais_out.to_netcdf(
        out_ais_lslr_file,
        engine="netcdf4",
        encoding={
            "sea_level_change": {
                "dtype": "f4",
                "zlib": True,
                "complevel": 4,
                "_FillValue": nc_missing_value,
            }
        },
    )
    return None


if __name__ == "__main__":
    # Initialize the command-line argument parser
    parser = argparse.ArgumentParser(
        description="Run the post-processing stage for the DP21 icesheet SLR projection workflow",
        epilog="Note: This is meant to be run as part of the Framework for the Assessment of Changes To Sea-level (FACTS)",
    )

    # Define the command line arguments to be expected
    parser.add_argument(
        "--locationfile",
        help="File that contains name, id, lat, and lon of points for localization",
        default="location.lst",
    )
    parser.add_argument(
        "--chunksize",
        help="Number of locations to process at a time [default=50]",
        type=int,
        default=50,
    )
    parser.add_argument(
        "--pipeline_id", help="Unique identifier for this instance of the module"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Run the postprocessing for the parameters specified from the command line argument
    dp21_postprocess_icesheet(args.locationfile, args.chunksize, args.pipeline_id)

    # Done
    exit()
