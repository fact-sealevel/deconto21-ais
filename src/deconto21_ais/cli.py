from deconto21_ais.deconto21_ais_preprocess import dp21_preprocess_icesheet
from deconto21_ais.deconto21_ais_project import (
    dp21_project_icesheet,
    dp21_project_icesheet_temperaturedriven,
)
from deconto21_ais.deconto21_ais_postprocess import dp21_postprocess_icesheet

import click


@click.command()
@click.option(
    "--scenario",
    type=str,
    help="Emission scenario for ice sheet projections",
    envvar="DP21_SCENARIO",
    default="rcp85",
)
@click.option(
    "--baseyear",
    type=int,
    help="Base year for ice sheet projections",
    envvar="DP21_BASEYEAR",
    default=2000,
)
@click.option(
    "--climate-data-file",
    type=str,
    help="NetCDF4/HDF5 file containing surface temperature data",
    envvar="DP21_CLIMATE_DATA_FILE",
)
@click.option(
    "--input-eais-rcp26-file",
    type=str,
    help="Input EAIS RCP2.6 data file",
    envvar="DP21_INPUT_EAIS_RCP26_FILE",
    required=True,
)
@click.option(
    "--input-eais-rcp45-file",
    type=str,
    help="Input EAIS RCP4.5 data file",
    envvar="DP21_INPUT_EAIS_RCP45_FILE",
    required=True,
)
@click.option(
    "--input-eais-rcp85-file",
    type=str,
    help="Input EAIS RCP8.5 data file",
    envvar="DP21_INPUT_EAIS_RCP85_FILE",
    required=True,
)
@click.option(
    "--input-wais-rcp26-file",
    type=str,
    help="Input WAIS RCP2.6 data file",
    envvar="DP21_INPUT_WAIS_RCP26_FILE",
    required=True,
)
@click.option(
    "--input-wais-rcp45-file",
    type=str,
    help="Input WAIS RCP4.5 data file",
    envvar="DP21_INPUT_WAIS_RCP45_FILE",
    required=True,
)
@click.option(
    "--input-wais-rcp85-file",
    type=str,
    help="Input WAIS RCP8.5 data file",
    envvar="DP21_INPUT_WAIS_RCP85_FILE",
    required=True,
)
@click.option(
    "--nsamps",
    type=int,
    help="Number of samples to draw from the ice sheet model ensemble",
    envvar="DP21_NSAMPS",
    default=500,
)
@click.option(
    "--pyear-start",
    type=int,
    help="Start year for ice sheet projections",
    envvar="DP21_PYEAR_START",
    default=2020,
)
@click.option(
    "--pyear-end",
    type=int,
    help="End year for ice sheet projections",
    envvar="DP21_PYEAR_END",
    default=2100,
)
@click.option(
    "--pyear-step",
    type=int,
    help="Year step for ice sheet projections",
    envvar="DP21_PYEAR_STEP",
    default=10,
)
@click.option(
    "--replace",
    type=bool,
    help="Whether to sample with replacement from the ice sheet model ensemble",
    envvar="DP21_REPLACE",
    default=True,
)
@click.option(
    "--rngseed",
    type=int,
    help="Random number generator seed for ice sheet model sampling",
    envvar="DP21_RNGSEED",
    default=1342,
)
@click.option(
    "--locationfile",
    type=str,
    help="File that contains name, id, lat, and lon of points for localization",
    envvar="DP21_LOCATIONFILE",
)
@click.option(
    "--chunksize",
    type=int,
    help="Number of locations to process at a time",
    envvar="DP21_CHUNKSIZE",
)
@click.option(
    "--pipeline-id",
    type=str,
    help="Unique identifier for this instance of the module",
    envvar="DP21_PIPELINE_ID",
)
@click.option(
    "--fpdir",
    type=str,
    help="Directory containing ice sheet fingerprints",
    envvar="DP21_FPDIR",
    default="$HOME/Desktop/facts_work/facts_v2/",
)
@click.option(
    "--output-ais-gslr",
    type=str,
    help="Output file for AIS global sea level rise projections",
    envvar="DP21_OUTPUT_AIS_GSLR_FILE",
)
@click.option(
    "--output-eais-gslr",
    type=str,
    help="Output file for EAIS global sea level rise projections",
    envvar="DP21_OUTPUT_EAIS_GSLR_FILE",
)
@click.option(
    "--output-wais-gslr",
    type=str,
    help="Output file for WAIS global sea level rise projections",
    envvar="DP21_OUTPUT_WAIS_GSLR_FILE",
)
@click.option(
    "--output-ais-lslr",
    type=str,
    help="Output file for AIS local sea level rise projections",
    envvar="DP21_OUTPUT_AIS_LSLR_FILE",
)
@click.option(
    "--output-eais-lslr",
    type=str,
    help="Output file for EAIS local sea level rise projections",
    envvar="DP21_OUTPUT_EAIS_LSLR_FILE",
)
@click.option(
    "--output-wais-lslr",
    type=str,
    help="Output file for WAIS local sea level rise projections",
    envvar="DP21_OUTPUT_WAIS_LSLR_FILE",
)
def main(
    scenario,
    baseyear,
    climate_data_file,
    input_eais_rcp26_file,
    input_eais_rcp45_file,
    input_eais_rcp85_file,
    input_wais_rcp26_file,
    input_wais_rcp45_file,
    input_wais_rcp85_file,
    nsamps,
    pyear_start,
    pyear_end,
    pyear_step,
    replace,
    rngseed,
    pipeline_id,
    locationfile,
    chunksize,
    fpdir,
    output_ais_gslr,
    output_eais_gslr,
    output_wais_gslr,
    output_ais_lslr,
    output_eais_lslr,
    output_wais_lslr,
):
    """Run the DP21 ice sheet workflow."""
    input_data_dict = {
        "rcp26": {"eais": input_eais_rcp26_file, "wais": input_wais_rcp26_file},
        "rcp45": {"eais": input_eais_rcp45_file, "wais": input_wais_rcp45_file},
        "rcp85": {"eais": input_eais_rcp85_file, "wais": input_wais_rcp85_file},
    }
    # Run the preprocessing stage
    dp21_preprocessed_data = dp21_preprocess_icesheet(
        scenario=scenario,
        baseyear=baseyear,
        input_paths_dict=input_data_dict,
        pipeline_id=pipeline_id,
        climate_data_file=climate_data_file,
    )

    # Run the projection stage
    if climate_data_file is not None:
        dp21_projected_data = dp21_project_icesheet_temperaturedriven(
            climate_data_file=climate_data_file,
            pyear_start=pyear_start,
            pyear_end=pyear_end,
            pyear_step=pyear_step,
            pipeline_id=pipeline_id,
            replace=replace,
            rngseed=rngseed,
            preprocess_dict=dp21_preprocessed_data,
            output_ais_gslr_file=output_ais_gslr,
            output_eais_gslr_file=output_eais_gslr,
            output_wais_gslr_file=output_wais_gslr,
        )
    # if climate_data_file is None:
    else:
        dp21_projected_data = dp21_project_icesheet(
            nsamps=nsamps,
            pyear_start=pyear_start,
            pyear_end=pyear_end,
            pyear_step=pyear_step,
            replace=replace,
            rngseed=rngseed,
            pipeline_id=pipeline_id,
            preprocess_dict=dp21_preprocessed_data,
            output_ais_gslr_file=output_ais_gslr,
            output_eais_gslr_file=output_eais_gslr,
            output_wais_gslr_file=output_wais_gslr,
        )

    # Run the post-processing stage
    dp21_postprocess_icesheet(
        locationfile=locationfile,
        chunksize=chunksize,
        pipeline_id=pipeline_id,
        projected_dict=dp21_projected_data,
        fpdir=fpdir,
        out_ais_lslr_file=output_ais_lslr,
        out_eais_lslr_file=output_eais_lslr,
        out_wais_lslr_file=output_wais_lslr,
    )
