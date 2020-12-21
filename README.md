Simple export script to export layer data from geoserver to a csv file and a json file. Here is the
list of environment variable you can provide to setup the script:

* `OUTPUT_DIR`: path to the output dir. Default `/mnt/apache_nas_data/public/export_json_csv`
* `UNWANTED_CSV_COLUMNS`: list of column trimmed from the returned csv. Default  `FID`, `the_geom`.
* `UNWANTED_JSON_COLUMNS`: list of column trimmed from the returned geojson. Geometry is always
  removed. This list removed filed from the "property". Default `bbox`
* `MAX_FEATURES`: default 5000
* `GEOSERVER_WFS_URL`: default ` https://www.geo2france.fr/geoserver/cr_hdf/wfs`
* `GEOSERVER_LAYERS`: list of layers, default "epci"
