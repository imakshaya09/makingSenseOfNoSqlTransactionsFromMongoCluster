import os
from typing import Optional

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def get_mongo_client(uri: Optional[str] = None) -> MongoClient:
    """Return a MongoClient using MONGODB_URI from the environment or provided URI."""
    uri = uri or os.getenv("MONGODB_URI")
    if not uri:
        raise EnvironmentError("MONGODB_URI is not set. Add it to .env or the environment.")

    return MongoClient(uri, tls=True, tlsCAFile=certifi.where())
