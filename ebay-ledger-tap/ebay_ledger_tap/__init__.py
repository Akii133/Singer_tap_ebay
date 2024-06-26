#!/usr/bin/env python3
import os
import json
import singer
import requests
from singer import utils
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema

REQUIRED_CONFIG_KEYS = ["start_date", "access_token"]
LOGGER = singer.get_logger()

def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def load_schemas():
    """ Load schemas from schemas folder """
    schemas = {}
    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = Schema.from_dict(json.load(file))
    return schemas

def discover():
    raw_schemas = load_schemas()
    streams = []
    for stream_id, schema in raw_schemas.items():
        # TODO: populate any metadata and stream's key properties here..
        stream_metadata = []
        key_properties = []
        streams.append(
            CatalogEntry(
                tap_stream_id=stream_id,
                stream=stream_id,
                schema=schema,
                key_properties=key_properties,
                metadata=stream_metadata,
                replication_key=None,
                is_view=None,
                database=None,
                table=None,
                row_count=None,
                stream_alias=None,
                replication_method=None,
            )
        )
    return Catalog(streams)

def sync(config, state, catalog):
    start_date = config.get("start_date")
    access_token = config.get("access_token")

    base_url = "https://apiz.ebay.com/sell/finances/v1/transaction"
    filter_params = f"transactionDate:[{start_date}..]"

    url = f"{base_url}?filter={filter_params}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Check if response is not empty
        if response.text.strip():
            data = response.json()
            if isinstance(data, list):
                for record in data:
                    singer.write_records(stream_name="transactions", records=[record])
            else:
                LOGGER.warning(f"Unexpected API response: {data}")
        else:
            LOGGER.warning("API response is empty.")

        if state is None:
            state = {}

        state["last_synced_date"] = start_date
        singer.write_state(state)

    except requests.exceptions.HTTPError as http_err:
        LOGGER.critical(f"HTTP error occurred: {http_err}")
        singer.write_record(stream_name="transactions", record={"error": str(http_err)})

    except requests.exceptions.RequestException as req_err:
        LOGGER.critical(f"Request error occurred: {req_err}")
        singer.write_record(stream_name="transactions", record={"error": str(req_err)})

    except Exception as err:
        LOGGER.critical(f"An unexpected error occurred: {err}")
        singer.write_record(stream_name="transactions", record={"error": str(err)})

def main():
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    if args.discover:
        catalog = discover()
        catalog.dump()
    else:
        if args.catalog:
            catalog = args.catalog
        else:
            catalog = discover()

        sync(args.config, args.state, catalog)

if __name__ == "__main__":
    main()
