import os


root_dir = os.getcwd()

# location of the GAMS sysdir
gams_sysdir = os.path.join("/", "Applications", "GAMS30.3", "Resources", "sysdir")


# data directories
data_dir = os.path.join(root_dir, "data")
raw_data_dir = os.path.join(data_dir, "raw_data")
processed_data_dir = os.path.join(data_dir, "processed_data")
map_dir = os.path.join(data_dir, "mappings")


# temp gdx file location
gdx_temp = os.path.join(root_dir, "gdx_temp")


# output directories
output_dir = os.path.join(root_dir, "output")
ldc_curves_dir = os.path.join(output_dir, "ldc_curves")
