#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  22 16:29:31 2020

@author: rvarela

# Module 2 - Create a cryptocurrency
"""

import random
import datetime
import json
import hashlib
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# build blockchain
class Blockchain:
    
    def __init__(self, miner):
        self.nodes = set()
        self.proof_seed = random.random()
        self.chain = []
        self.transactions = []
        self.create_block(1, miner)
        
    def create_block(self, proof, miner, previous_hash = None, data = None):
        # proof == nonce
        # TODO analyse transactions to determine the fee instead of hardcoding
        self.add_transaction(miner, miner, 1, 'fee')
        block = {'index' : len(self.chain) + 1,
                 'timestamp' : datetime.datetime.now(),
                 'proof' : proof,
                 'previous_hash' : previous_hash,
                 'transactions' : self.transactions}
        self.chain.append(block)
        self.transactions = []
        return block
    
    def get_previous_block(self):
        return self.chain[-1] #return last
    
    def next_block_index(self):
        try:
            return self.get_previous_block()['index'] + 1
        except:
            return 0
    
    def proof_of_work(self, previous_proof = None):
        if previous_proof == None:
            previous_proof = self.get_previous_block()['proof']
        new_proof = 1
        found = False
        while found is False:
            hash_work = self.hash_proof(previous_proof, new_proof)
            if self.is_valid_pow(hash_work):
                found = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block = None):
        if block == None:
            block = self.get_previous_block()   
        # source default{ https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
        return hashlib.sha256(json.dumps(block, sort_keys = True, default=str).encode()).hexdigest()
    
    def is_chain_valid(self, chain = None):
        if chain is None:
            chain = self.chain
        previous_block = self.chain[0]  
        index = 1
        while index < len(self.chain):
            block = self.chain[index]
            
            if block['previous_hash'] != self.hash(previous_block):
                return False
            if not self.is_valid_pow(self.hash_proof(previous_block['proof'], block['proof'])):
                return False
            
            previous_block = block
            index += 1
        return True
    
    def replace_chain(self):
        network = self.nodes
        longest_chain = self.chain
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if (response.status_code == 200):
                chain = response.json()
                if (chain['length'] > len(longest_chain)) and self.is_chain_valid(chain['blockchain']):
                    longest_chain = chain['blockchain']
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
    
    def hash_proof(self, previous_proof, new_proof):
        return hashlib.sha256(str(self.proof_seed + 
                                  new_proof**2 - 
                                  previous_proof**2).encode()).hexdigest()
    
    def is_valid_pow(self, hash_work):
        return hash_work[:4] == '0000'
    
    def add_node(self, url):
        self.nodes.add(urlparse(url).netloc)
    
    ## To refactor into rodicoin class?
    def add_transaction(self, sender, receiver, amount, description = None):
        # validations todo
        self.transactions.append({
                'sender' : sender,
                'receiver' : receiver,
                'amount' : amount,
                'description' : description
            })
        return self.next_block_index()
    
    
# Expoe the blockchain using Flask

## http://localhost:5000
node_address = str(uuid4()).replace('-','')

app = Flask(__name__)
# config to avoid runtime errors
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

blockchain = Blockchain(node_address)

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    new_block = blockchain.create_block(blockchain.proof_of_work(), 
                                        node_address,
                                        blockchain.hash())
    response = {'message' : 'A new block has been mined',
                'block' : new_block,
                'hash' : blockchain.hash(new_block)}
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'blockchain' : blockchain.chain,
                'length' : len(blockchain.chain)}.items()
    return jsonify(response), 200

@app.route('/chain_valid', methods = ['GET'])
def chain_valid():
    response = {'blockchain' : blockchain.chain,
                'valid' : blockchain.is_chain_valid()}
    return jsonify(response), 200

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    transaction = request.get_json()
    if not all (key in transaction for key in ['sender','receiver','amount']):
        return f'Invalid transaction {transaction}', 400
    index = blockchain.add_transaction(transaction['sender'], transaction['receiver'], transaction['amount'])
    response = f'This transaction will be in the next mined block {index}'
    return jsonify(response), 200   

app.run(host = '0.0.0.0', port = 5000)