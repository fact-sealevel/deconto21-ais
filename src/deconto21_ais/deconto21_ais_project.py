import numpy as np
import argparse
import pickle
import xarray as xr
import os
import h5py
import time

""" dp21_project_icesheet.py

Runs the dp21 icesheet projection stage.

Parameters:
nsamps              Number of samples to produce
replace             Allow sampling with replacement
rngseed             Seed for the random number generator
pipeline_id         Unique identifier to attach to this pipeline

Note: 'pipeline_id' is a unique identifier that distinguishes it among other instances
of this module within the same workflow.

"""


def make_projection_ds(
    ice_source, global_samps, years, samples, locations, scenario, baseyear
):
    """
    Create an xarray Dataset for global sea level rise projections from ice sheet samples.

    Parameters
    ----------
    ice_source : str
            Name of the ice sheet source (e.g., 'EAIS', 'WAIS', 'AIS').
    global_samps : array-like
            Array of global sea level change samples, shape (samples, years).
    years : array-like
            Array of projection years.
    samples : array-like
            Array of sample indices.
    locations : array-like
            Array of location indices (typically a single value for global projections).
    scenario : str
            Emissions scenario name.
    baseyear : int
            Reference year for projections.

    Returns
    -------
    xarray.Dataset
            Dataset containing sea level change data and metadata, with dimensions ('samples', 'years', 'locations').

    Notes
    -----
    - The returned dataset includes variables for sea level change, latitude, and longitude, as well as metadata attributes.
    - Latitude and longitude are set to NaN (np.inf) for global projections.
    """

    data = np.asarray(global_samps, dtype=np.float32)[:, :, np.newaxis]

    ds = xr.Dataset(
        data_vars={
            "sea_level_change": (
                ("samples", "years", "locations"),
                data,
                {"units": "mm"},
            ),
            "lat": (
                ("locations",),
                np.array([np.float32(np.inf)], dtype=np.float32),
            ),
            "lon": (
                ("locations",),
                np.array([np.float32(np.inf)], dtype=np.float32),
            ),
        },
        coords={
            "years": (("years",), years),
            "samples": (("samples",), samples),
            "locations": (("locations",), locations),
        },
        attrs={
            "description": f"Global SLR contribution from {ice_source} from the Bamber et al. 2019 IPCC AR6 workflow",
            "history": "Created " + time.ctime(time.time()),
            "scenario": scenario,
            "baseyear": baseyear,
        },
    )
    return ds


def dp21_project_icesheet(
    nsamps,
    pyear_start,
    pyear_end,
    pyear_step,
    pipeline_id,
    replace,
    rngseed,
    preprocess_dict,
    output_ais_gslr_file,
    output_eais_gslr_file,
    output_wais_gslr_file,
):
    years = preprocess_dict["years"]
    wais = preprocess_dict["wais_samps"]
    eais = preprocess_dict["eais_samps"]
    scenario = preprocess_dict["scenario"]
    baseyear = preprocess_dict["baseyear"]

    # Define the target projection years
    targyears = np.arange(pyear_start, pyear_end + 1, pyear_step)

    # Extract the pool size from the data
    pool_size = eais.shape[1]

    # Find the data years that overlap with the target projection years
    (_, datayr_idx, targyear_idx) = np.intersect1d(
        years, targyears, return_indices=True
    )

    # Generate the sample indices
    rng = np.random.default_rng(rngseed)
    sample_idx = rng.choice(pool_size, size=nsamps, replace=replace)

    # Store the samples
    wais_samps = wais[datayr_idx[:, np.newaxis], sample_idx[np.newaxis, :]]
    eais_samps = eais[datayr_idx[:, np.newaxis], sample_idx[np.newaxis, :]]

    # Transpose the samples to fit the output data structure
    wais_samps = wais_samps.T
    eais_samps = eais_samps.T
    ais_samps = wais_samps + eais_samps

    output = {
        "eais_samps": eais_samps,
        "wais_samps": wais_samps,
        "ais_samps": ais_samps,
        "scenario": scenario,
        "targyears": targyears[targyear_idx],
        "baseyear": baseyear,
    }

    # Write to file
    samples = np.arange(nsamps, dtype=np.int64)
    locations = np.array([-1], dtype=np.int64)  # single “location”, value -1

    if output_eais_gslr_file is not None:
        ds_eais = make_projection_ds(
            ice_source="EAIS",
            global_samps=eais_samps,
            years=targyears,
            samples=samples,
            locations=locations,
            scenario=scenario,
            baseyear=baseyear,
        )
        ds_eais.to_netcdf(output_eais_gslr_file)

    if output_wais_gslr_file is not None:
        ds_wais = make_projection_ds(
            ice_source="WAIS",
            global_samps=wais_samps,
            years=targyears,
            samples=samples,
            locations=locations,
            scenario=scenario,
            baseyear=baseyear,
        )
        ds_wais.to_netcdf(output_wais_gslr_file)
    if output_ais_gslr_file is not None:
        ds_ais = make_projection_ds(
            ice_source="AIS",
            global_samps=ais_samps,
            years=targyears,
            samples=samples,
            locations=locations,
            scenario=scenario,
            baseyear=baseyear,
        )
        ds_ais.to_netcdf(output_ais_gslr_file)

    return output


def dp21_project_icesheet_temperaturedriven(
    climate_data_file,
    pyear_start,
    pyear_end,
    pyear_step,
    pipeline_id,
    replace,
    rngseed,
    preprocess_dict,
    output_ais_gslr_file,
    output_eais_gslr_file,
    output_wais_gslr_file,
):
    # Load the data file
    years = preprocess_dict["years"]
    wais = preprocess_dict["wais_samps"]
    eais = preprocess_dict["eais_samps"]
    scenario = preprocess_dict["scenario"]
    baseyear = preprocess_dict["baseyear"]
    # Set the rng
    rng = np.random.default_rng(rngseed)

    # identify which samples to draw from which scenario
    useScenario = pickScenario(climate_data_file, scenario, rng)
    nsamps = useScenario.size

    # Define the target projection years
    targyears = np.arange(pyear_start, pyear_end + 1, pyear_step)

    # Extract the pool size from the data
    pool_size = eais.shape[1]

    # Find the data years that overlap with the target projection years
    (_, datayr_idx, targyear_idx) = np.intersect1d(
        years, targyears, return_indices=True
    )

    # Generate the sample indices
    sample_idx = rng.choice(pool_size, size=nsamps, replace=replace)

    # Store the samples
    wais_samps0 = wais[datayr_idx[:, np.newaxis], sample_idx[np.newaxis, :], :]
    eais_samps0 = eais[datayr_idx[:, np.newaxis], sample_idx[np.newaxis, :], :]

    # Store the samples for AIS components
    eais_samps = eais_samps0[:, :, 0]
    wais_samps = wais_samps0[:, :, 0]

    for ii in range(1, 3):
        eais_samps[:, useScenario == ii] = eais_samps0[:, useScenario == ii, ii]
        wais_samps[:, useScenario == ii] = wais_samps0[:, useScenario == ii, ii]

    # Transpose the samples to fit the output data structure
    wais_samps = wais_samps.T
    eais_samps = eais_samps.T
    ais_samps = wais_samps + eais_samps

    output = {
        "eais_samps": eais_samps,
        "wais_samps": wais_samps,
        "ais_samps": ais_samps,
        "scenario": scenario,
        "targyears": targyears[targyear_idx],
        "baseyear": baseyear,
    }

    # Write to file
    samples = np.arange(nsamps, dtype=np.int64)
    locations = np.array([-1], dtype=np.int64)  # single “location”, value -1

    if output_eais_gslr_file is not None:
        ds_eais = make_projection_ds(
            ice_source="EAIS",
            global_samps=eais_samps,
            years=targyears,
            samples=samples,
            locations=locations,
            scenario=scenario,
            baseyear=baseyear,
        )
        ds_eais.to_netcdf(output_eais_gslr_file)

    if output_wais_gslr_file is not None:
        ds_wais = make_projection_ds(
            ice_source="WAIS",
            global_samps=wais_samps,
            years=targyears,
            samples=samples,
            locations=locations,
            scenario=scenario,
            baseyear=baseyear,
        )
        ds_wais.to_netcdf(output_wais_gslr_file)
    if output_ais_gslr_file is not None:
        ds_ais = make_projection_ds(
            ice_source="AIS",
            global_samps=ais_samps,
            years=targyears,
            samples=samples,
            locations=locations,
            scenario=scenario,
            baseyear=baseyear,
        )
        ds_ais.to_netcdf(output_ais_gslr_file)

    return output


def GetSATData(
    fname,
    scenario,
    refyear_start=1850,
    refyear_end=1900,
    year_start=1900,
    year_end=2300,
):
    # Open the file
    df_ssp = h5py.File(fname, "r")

    # Extract the surface temperature for this scenario
    if scenario not in df_ssp.keys():
        raise ValueError("Scenario {} not found in {}".format(scenario, fname))
    ssp_folder = df_ssp.get(scenario)
    sat_ssp = ssp_folder.get("surface_temperature")

    # Get the number of ensemble members from the data
    _, nens = sat_ssp.shape

    # Extract the years available
    sat_years = df_ssp["year"][()]

    # Which indices align with the reference and trim years
    refyear_start_idx = np.flatnonzero(sat_years == refyear_start)[0]
    refyear_end_idx = np.flatnonzero(sat_years == refyear_end)[0]  # + 1
    year_start_idx = np.flatnonzero(sat_years == year_start)[0]
    year_end_idx = np.flatnonzero(sat_years == year_end)[0] + 1

    # Normalize and crop temperature series
    Time = np.arange(year_start, year_end + 1)
    SATave = np.mean(sat_ssp[refyear_start_idx:refyear_end_idx, :], axis=0)
    SAT = sat_ssp[year_start_idx:year_end_idx, :] - SATave

    # Close the h5 file
    df_ssp.close()

    # Done
    return (SAT, Time, nens)


def pickScenario(climate_data_file, scenario, rng):
    # Load the temperature data

    SAT, Time, _ = GetSATData(climate_data_file, scenario)

    # find integrated SAT over 2000-2099
    x2 = np.where((Time[:] < 2100) * (Time[:] >= 2000))
    SAT2 = SAT[x2]
    iSAT = SAT2.sum(axis=0)
    selector = rng.random(iSAT.size)

    # convert integrated temperature into a normalized variable between low and high scenarios

    # Based on CCSM temperature projections used in the paper, integrated
    # 21st century temperature is about 133, 167 and 245 C*yr for RCP 2.6, 4.5 and 8.5,
    # respectively.

    iSAT_marker = np.array([133, 167, 245])

    f1 = np.minimum(
        1, np.maximum(0, (iSAT - iSAT_marker[0]) / (iSAT_marker[1] - iSAT_marker[0]))
    )
    f2 = np.minimum(
        1, np.maximum(0, (iSAT - iSAT_marker[1]) / (iSAT_marker[2] - iSAT_marker[1]))
    )

    # Select which scenario to draw from for each sample
    useScenario = np.multiply(selector < f1, 1)
    useScenario[iSAT > iSAT_marker[1]] = 1 + np.multiply(
        selector[iSAT > iSAT_marker[1]] < f2[iSAT > iSAT_marker[1]], 1
    )
    return useScenario


def LoadDataFile(pipeline_id):
    # Load the data file
    datafilename = "{}_data.pkl".format(pipeline_id)
    datafile = os.path.join(os.path.dirname(__file__), datafilename)

    with open(datafile, "rb") as f:
        my_data = pickle.load(f)

    years = my_data["years"]
    wais = my_data["wais_samps"]
    eais = my_data["eais_samps"]
    scenario = my_data["scenario"]
    baseyear = my_data["baseyear"]

    return years, wais, eais, scenario, baseyear


if __name__ == "__main__":
    # Initialize the command-line argument parser
    parser = argparse.ArgumentParser(
        description="Run the DP21 projection stage.",
        epilog="Note: This is meant to be run as part of the Framework for the Assessment of Changes To Sea-level (FACTS)",
    )

    # Define the command line arguments to be expected
    parser.add_argument(
        "--nsamps",
        help="Number of samples to draw (default = 10000)",
        default=10000,
        type=int,
    )
    parser.add_argument(
        "--pyear_start",
        help="Projection year start [default=2020]",
        default=2020,
        type=int,
    )
    parser.add_argument(
        "--pyear_end", help="Projection year end [default=2100]", default=2100, type=int
    )
    parser.add_argument(
        "--pyear_step", help="Projection year step [default=10]", default=10, type=int
    )
    parser.add_argument(
        "--replace",
        help="Allow sampling with replacement [default = 1]",
        choices=("0", "1"),
        default=1,
    )
    parser.add_argument(
        "--seed",
        help="Seed for the random number generator [default = 1234]",
        default=1234,
        type=int,
    )
    parser.add_argument(
        "--pipeline_id", help="Unique identifier for this instance of the module"
    )
    parser.add_argument(
        "--climate_data_file",
        help="NetCDF4/HDF5 file containing surface temperature data",
        type=str,
        default="",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Run the projection stage with the provided arguments
    if len(args.climate_data_file) == 0:
        # Run the preprocessing stage with the user defined RCP scenario
        dp21_project_icesheet(
            args.nsamps,
            args.pyear_start,
            args.pyear_end,
            args.pyear_step,
            args.pipeline_id,
            args.replace,
            args.seed,
        )
    else:
        dp21_project_icesheet_temperaturedriven(
            args.climate_data_file,
            args.pyear_start,
            args.pyear_end,
            args.pyear_step,
            args.pipeline_id,
            args.replace,
            args.seed,
        )

    exit()
