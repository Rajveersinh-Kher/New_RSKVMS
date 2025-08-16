from pymongo import MongoClient

uri = "mongodb+srv://rsksystem1017:x5O0p5lpvRNgJ8Y2@cluster0.lw9b3kq.mongodb.net/rsk_vms?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)

db = client["rsk_vms"]
print(db.list_collection_names())
