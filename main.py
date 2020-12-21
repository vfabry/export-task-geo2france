import csv
import sys
import logging
import requests
import json
from pydantic import BaseSettings
from abc import ABC, abstractmethod
from requests import Response
from pathlib import Path
from urllib.parse import urlencode
from io import StringIO

class Settings(BaseSettings):
    OUTPUT_DIR: Path = Path("/mnt/apache_nas_data/public/export_json_csv")
    UNWANTED_CSV_COLUMNS: list = ("FID", "the_geom")
    UNWANTED_JSON_COLUMNS: list = ("bbox",)
    MAX_FEATURES: int = 5000
    GEOSERVER_WFS_URL: str = "https://www.geo2france.fr/geoserver/cr_hdf/wfs"
    GEOSERVER_LAYERS: list = ("epci",)
    LOG_LEVEL: str = "INFO"


class Process(ABC):
    """
    Common interface to fetching data from geoserver WFS in csv and json.
    """

    def __init__(self, settings: "Settings", layer: str) -> None:
        self.layer = layer
        self.settings = settings

    @abstractmethod
    def run(self) -> None:
        pass

    def download(self, output_format: str) -> Response:
        qs = urlencode(
            {
                "request": "GetFeature",
                "typeName": self.layer,
                "maxFeature": self.settings.MAX_FEATURES,
                "outputFormat": output_format,
                "version": "1.0.0"
            }
        )
        url = f"{self.settings.GEOSERVER_WFS_URL}?{qs}"
        r = requests.get(url)
        r.raise_for_status()
        return r

    @abstractmethod
    def clean(self, data: str) -> str:
        pass

    @abstractmethod
    def store(self, data: str, path: Path) -> None:
        pass


class ProcessCsv(Process):
    """
    Concrete implentation of fetching CSV from geoserver WFS
    """

    def run(self) -> None:
        csv = self.download("csv")
        cleaned = self.clean(csv.text)
        self.store(cleaned, f"result_{self.layer}.csv")

    def clean(self, data: str) -> StringIO:
        csv.field_size_limit(sys.maxsize)
        output = StringIO()
        reader = csv.DictReader(StringIO(data))
        writer = csv.DictWriter(output, fieldnames=[x for x in reader.fieldnames if x not in self.settings.UNWANTED_CSV_COLUMNS])
        writer.writeheader()
        for line in reader:
            for unwanted in self.settings.UNWANTED_CSV_COLUMNS:
                if unwanted in line:
                    del line[unwanted]
            writer.writerow(line)
        return output

    def store(self, data: StringIO, output_file: str) -> None:
        with open(self.settings.OUTPUT_DIR / output_file, 'w') as f:
            data.seek(0)
            f.write(data.read())



class ProcessJson(Process):
    """
    Concrete implentation of fetching JSON from geoserver WFS
    """

    def run(self):
        res = self.download("json")
        cleaned = self.clean(res.json())
        self.store(cleaned, f"result_{self.layer}.json")

    def clean(self, geojson: dict) -> dict:
        for features in geojson["features"]:
            for unwanted in self.settings.UNWANTED_JSON_COLUMNS:
                features.pop(unwanted, None)
        return geojson["features"]

    def store(self, data: dict, output_file: str) -> None:
        with open(self.settings.OUTPUT_DIR / output_file, "w") as f:
            json.dump(data, f)


if __name__ == "__main__":
    settings = Settings()
    logging.basicConfig(level=settings.LOG_LEVEL)
    for layer in settings.GEOSERVER_LAYERS:
        ProcessCsv(settings, layer).run()
        ProcessJson(settings, layer).run()
