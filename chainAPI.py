from flask import Flask, jsonify, request
from flask_ngrok import run_with_ngrok
from cryptoChain import Blockchain
from uuid import uuid4
from urllib import response

app = Flask(__name__)
# run_with_ngrok(app)

app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False

# Create a new node address
node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route("/mine_block", methods=["GET"])
def mine_block():
    
    previous_block = blockchain.get_previous_block()    
    previous_proof = previous_block["proof"]  
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.blockHash(previous_block)
    blockchain.create_transaction(sender = node_address, receiver = "Lux", amount = 15)
    block = blockchain.create_block(proof, previous_hash)
    
    response = {
        
        "message"               : "Successfully mined a new block.",
        "index"                 : block["index"],
        "timestamp"             : block["timestamp"],
        "proof"                 : block["proof"],
        "previous_hash"         : block["previous_hash"],
        "transactions"          : block["transactions"] 
        
    }
    return jsonify(response), 200    
    
    
@app.route("/get_chain", methods=["GET"])
def get_chain():
    response = {
        "chain"     : blockchain.chain,
        "length"    : len(blockchain.chain)   
    }    
    return jsonify(response), 200

    
@app.route("/is_valid", methods=["GET"])
def is_valid():
    is_valid = blockchain.isChainValid(blockchain.chain)
    
    if is_valid:
        response = {"message"   :  "The blockchain is valid."}
    else:
        response = {"message" : "The blockchain is not valid."}
    
    return jsonify(response), 200

@app.route("/create_transaction", methods=["POST"])
def create_transaction():
    json = request.get_json()
    transaction_keys = ["sender", "receiver", "amount"]
    
    if not all (key in json for key in transaction_keys):
        return "There is at least one parameter missing to perform the transaction"
    
    index = blockchain.create_transaction(json["sender"], json["receiver"], json["amount"])
    response = {"message" : f'The transaction was successfully added to the block {index}'}
    return jsonify(response), 201
    

@app.route("/connect_node", methods=["POST"])    
def connect_node():
    json = request.get_json()
    nodes = json.get("nodes")
    
    if nodes in None:
        return "There are no nodes to connect add", 400
    
    for node in nodes:
        blockchain.add_node(node)
    
    response = {
        "message"       : 'Every node provided was succesfully connected to the chain. Current working nodes:',
        "total_nodes"   : list(blockchain.nodes)        
    }
    return jsonify(response), 201


@app.route("/replace_chain", methods=["GET"])   
def replace_chain():
    is_chain_replaced = blockchain.inject_longest_chain()
    if is_chain_replaced:
        response = {
            "message"   :  "Some nodes were behind. The blockchain has been replaced with the longest chain",
            "new_chain" : blockchain.chain
            }
    else:
        response = {
            "message"   :  "Everything is working good. Every node is up to date",
            "new_chain" : blockchain.chain
            }
    return jsonify(response), 200

          
 
app.run(host = "localhost", port = 3003) # (need to coment flask_ngrok also)
# app.run()