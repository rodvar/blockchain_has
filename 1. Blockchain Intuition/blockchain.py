#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 16:29:31 2020

@author: rvarela

# Module 1 - Create a blockchain
"""

import random
import datetime
import json
import hashlib
from flask import Flask, jsonify

# build blockchain
class Blockchain:
    
    def __init__(self):
        self.proof_seed = random.random()
        self.chain = []
        self.create_block(proof = 1)
        
    def create_block(self, proof, previous_hash = None, data = None):
        block = {'index' : len(self.chain) + 1,
                 'timestamp' : datetime.datetime.now(),
                 'proof' : proof,
                 'previous_hash' : previous_hash,
                 'data' : None} # To be added
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1] #return last
    
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
    
    def is_chain_valid(self):
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
    
    def hash_proof(self, previous_proof, new_proof):
        return hashlib.sha256(str(self.proof_seed + 
                                  new_proof**2 - 
                                  previous_proof**2).encode()).hexdigest()
    
    def is_valid_pow(self, hash_work):
        return hash_work[:4] == '0000'
    
    
# Expoe the blockchain using Flask

## http://localhost:5000

app = Flask(__name__)
# config to avoid runtime errors
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

blockchain = Blockchain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    new_block = blockchain.create_block(blockchain.proof_of_work(), blockchain.hash())
    response = {'message' : 'A new block has been mined',
                'block' : new_block,
                'hash' : blockchain.hash(new_block)}
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'blockchain' : blockchain.chain,
                'lenght' : len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/chain_valid', methods = ['GET'])
def chain_valid():
    response = {'blockchain' : blockchain.chain,
                'valid' : blockchain.is_chain_valid()}
    return jsonify(response), 200

app.run(host = '0.0.0.0', port = 5000)