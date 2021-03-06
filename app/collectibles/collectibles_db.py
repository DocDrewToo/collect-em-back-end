from flask import current_app, g
from flask_pymongo import PyMongo
from werkzeug.local import LocalProxy
import os
from bson.objectid import ObjectId
from datetime import datetime
import pytz
import json

def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)

    if db is None:

        db = g._database = PyMongo(current_app).db
       
    return db


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)

def find_by_owner(owner_id, results_per_page, sort_by = "itemName"):
    query = {}
    query["ownerId"] = owner_id

    try:
        collectible = db.myCollectibles.find(query).sort(sort_by).limit(results_per_page)
        total_records = db.myCollectibles.count_documents(query)
        return list(collectible), total_records
    except Exception as exception:
        return exception

def find_by_item_id(item_id):
    mongo_id = ObjectId(item_id)
    try:
        collectible = db.myCollectibles.find({ "_id": mongo_id })
        total_records = db.myCollectibles.count_documents({ "_id": mongo_id })
        return list(collectible), total_records
    except Exception as exception:
        return exception

def delete_an_item(item_id):
    mongo_id = ObjectId(item_id)
    try:
        collectible, num_found = find_by_item_id(item_id)
        db.myCollectibles.delete_one({ "_id": mongo_id })
        return list(collectible), num_found
    except Exception as exception:
        return exception

def delete_an_item_by_object(data):
    try:
        collectible = db.myCollectibles.find(data)
        db.myCollectibles.delete_one(data)
        return list(collectible)
    except Exception as exception:
        return exception

def insert_a_collectible(data):
    data["lastModified"] = datetime.now(pytz.UTC)
    db.myCollectibles.insert_one(data)

def update_a_collectible(item_id, data):
    mongo_id = ObjectId(item_id)
    find_query = {}
    find_query["_id"] = mongo_id

    update_query = {}
    update_query["$set"] = data
    update_query["$currentDate"] = {"lastModified":True}

    db.myCollectibles.update_one(find_query, update_query)
    return find_by_item_id(find_query)

def update_a_collectible_by_name(data):
    item_owner = data.get("ownerId")
    item_name = data.get("itemName")
    find_query = {"ownerId":item_owner, "itemName":item_name}
    data.pop("ownerId")
    data.pop("itemName")
    update_query = {}
    update_query["$set"] = data
    print(find_query)
    if db.myCollectibles.find_one(find_query) == None:
        db.myCollectibles.insert_one(find_query)
    db.myCollectibles.update_one(find_query, update_query)

if __name__ == "__main__":
  print(os.path.basename(__file__))
