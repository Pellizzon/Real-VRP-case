import os
from dataclasses import dataclass
from typing import Dict

import pandas as pd
import requests
from dotenv import load_dotenv


@dataclass
class DistanceMatrix:

    input_data: pd.DataFrame
    matrix: pd.DataFrame = None

    def __format_payload(self) -> Dict:
        """Builds dictionary with origins and destinations info to be
        sent as payload in the API request.

        Returns:
            Dict: Dictionary with the payload info for the API.
        """
        payload = {
            "origins": [],
            "destinations": [],
            "travelMode": "driving",
        }

        for lat, long in zip(self.input_data["Latitude"], self.input_data["Longitude"]):
            entry = {}
            entry["latitude"] = lat
            entry["longitude"] = long
            payload["origins"] += [entry]
            payload["destinations"] += [entry]

        return payload

    def __format_output(self, data: Dict) -> pd.DataFrame:
        """Formats output from API request as a DataFrame.

        Args:
            data (Dict): JSON data from API response.

        Returns:
            pd.DataFrame: DataFrame containing distance matrix.
        """
        cols = list(self.input_data["Name"])
        cols.insert(0, "Name")
        df = pd.DataFrame(columns=cols)
        df["Name"] = self.input_data["Name"]

        for r in data["resourceSets"][0]["resources"][0]["results"]:
            df.iloc[r["originIndex"], r["destinationIndex"] + 1] = r["travelDistance"]
        df.index = df["Name"]
        df.drop(columns=["Name"], inplace=True)
        return df

    def calculate(self) -> None:
        """Calculates the distance matrix of the input locations.

        Raises:
            err: API request error.
        """

        # Loading .env info
        current_path = os.path.dirname(os.path.abspath(__file__))
        dotenv_path = os.path.join(current_path, "..", "..", ".env")
        load_dotenv(dotenv_path=dotenv_path)

        # Setting up request URL
        api_key = os.getenv("BING_MAPS_KEY")
        url = (
            f"https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?key={api_key}"
        )

        payload = self.__format_payload()

        try:

            res = requests.post(
                url=url,
                json=payload,
            )

            if res.status_code == 200:
                output = self.__format_output(res.json())
                self.matrix = output
                return
            else:
                return

        except requests.RequestException as err:
            raise err

    def store_backup(self) -> None:
        """Saves a backup Distance Matrix as a CSV file in the data directory."""
        self.calculate()

        current_path = os.path.dirname(os.path.abspath(__file__))
        backup_path = os.path.join(
            current_path, "..", "..", "data", "distance_matrix.csv"
        )

        self.matrix.to_csv(backup_path, sep=";")


if __name__ == "__main__":

    current_path = os.path.dirname(os.path.abspath(__file__))
    locations_path = os.path.join(current_path, "..", "..", "data", "locations.csv")

    df = pd.read_csv(locations_path, sep=";", index_col=False)

    DistanceMatrix(df).store_backup()
