from pymongo import MongoClient

MONGO_URI = "mongodb+srv://chatbot:VBEZlriNjETVEfUV@cluster0.yau1zmm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["sha-bot"]
collection = db["documents"]
print("Connected successfully:", client.server_info())