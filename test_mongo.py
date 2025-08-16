from pymongo import MongoClient

uri = "mongodb+srv://rsksystem1017:RA101728vu@cluster0.lw9b3kq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)

db = client["rsk_vms"]
print(db.list_collection_names())
