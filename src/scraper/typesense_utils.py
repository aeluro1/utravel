import argparse
import json
from pathlib import Path
from pprint import pprint

import typesense
from typesense.exceptions import ObjectAlreadyExists
from dotenv import dotenv_values


curr_path = Path(__file__).resolve().parent
config = dotenv_values(curr_path / "ts_admin.env")
client: typesense.Client = None # type: ignore


def init_client():
    global client
    if client is not None:
        return
    client = typesense.Client({
        "nodes": [{
            "host": config["TYPESENSE_HOST"],
            "port": config["TYPESENSE_PORT"],
            "protocol": config["TYPESENSE_PROTOCOL"]
        }],
        "api_key": config["TYPESENSE_API_KEY"],
        "connection_timeout_seconds": 2
    })


def to_jsonl():
    path = curr_path / "data"
    if not path.is_dir():
        raise RuntimeError("No data to process")
    jsonl_path = path / "all.jsonl"
    
    with open(jsonl_path, "w") as f:
        for file in path.iterdir():
            with open(file) as fr:
                try:
                    data = json.load(fr)
                except json.JSONDecodeError:
                    continue
                for d in data:
                    try:
                        d["imgs"] = json.loads(d["imgs"])
                        d["tags"] = json.loads(d["tags"])
                    except Exception:
                        pass
                    f.write(json.dumps(d))
                    f.write("\n")
        # f.flush()


def push_docs(fn: str):
    global client
    rst_schema = {
        "name": "restaurants",
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "url", "type": "string"},
            {"name": "imgs", "type": "string[]", "optional": True, "index": False}, # Non-indexed fields will not be loaded into memory
            {"name": "address", "type": "string"},
            {"name": "phone", "type": "string"},
            {"name": "id", "type": "string", "index": False},
            {"name": "rating", "type": "float"},
            {"name": "review_count", "type": "int32"},
            {"name": "tags", "type": "string[]", "facet": True},
            {"name": "price", "type": "string", "facet": True}
        ],
        "default_sorting_field": "review_count"
    }

    try:
        client.collections.create(rst_schema)
    except ObjectAlreadyExists:
        pass
        

    jsonl_path = curr_path / "data" / f"{fn}.jsonl"
    with open(jsonl_path) as jsonl_file:
        client.collections["restaurants"].documents.import_(jsonl_file.read().encode("utf-8")) # type: ignore


def get_collections():
    pprint(client.collections.retrieve())


def search_docs(query: str,
                query_by: str = "",
                sort_by: str = "",
                filter_by: str = ""):
    params = {
        "q": query,
        "query_by": query_by if query_by != "" else "name",
        "filter_by": filter_by,
        "sort_by": sort_by # if sort_by != "" else "rating:desc"
    }
    if filter_by != "":
        params["filter_by"] = filter_by
    results = client.collections["restaurants"].documents.search(params) # type: ignore
    pprint(results)
    pprint(f"Number of results: {results['found']}")
    
    
def main(args: argparse.Namespace):
    if args.jsonl:
        to_jsonl()
    if args.push or args.get or args.search:
        init_client()
    if args.push:
        push_docs(args.push)
    if args.get:
        get_collections()
    if args.search:
        search_args = args.search.split(";")
        search_docs(*search_args)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Typesense utilities")
    parser.add_argument(
        "--jsonl",
        action = "store_true",
        help = "convert JSON array into JSONL of array elements"
    )
    parser.add_argument(
        "--push", "-p",
        action = "store",
        help = "push documents in [file].jsonl to typesense server"
    )
    parser.add_argument(
        "--get", "-g",
        action = "store_true",
        help = "print all collections in typesense server"
    )
    parser.add_argument(
        "--search", "-s",
        action = "store",
        help = "search documents with format string '[query];[query by];[filter by];[sort by]'"
    )
    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.error("No arguments provided")
    main(args)