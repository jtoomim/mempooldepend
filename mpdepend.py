#!/usr/bin/python3

import random

operation_counter = 0

class Transaction:
    def __init__(self, txid, inputs, outputs, fee):
        # don't care about signatures, nValue, etc for this
        self.txid = txid
        self.most_recent_block = 0
        self.inputs = inputs
        self.outputs = outputs
        self.ancestorcount = None
        self.confirmed = False
        self.fee = fee # this tx only -- not yet finished
        self.cumsize = None
        self.cumfeerate = None
        self.size = 100 * len(inputs) + 30 * len(outputs) # not yet finished

    def on_new_block(self, block):
        if self.most_recent_block == block:
            return
        self.most_recent_block = block
        self.ancestorcount = None
        self.cumsize = None
        self.cumfeerate = None

    def count_ancestor_inputs(self, blockheight):
        # this code counts the total number of unconfirmed ancestor inputs
        # NOT the number of unique ancestor transactions
        global operation_counter
        operation_counter += 1
        if self.confirmed: 
            self.ancestorcount = 0
            return 0
        if self.most_recent_block == blockheight and self.ancestorcount != None:
            # print("self.tx=%i has cached ancestorcount=%i" %(self.txid, self.ancestorcount))
            return self.ancestorcount

        count = 0
        for tx, out in self.inputs:
            if not tx.confirmed:
                operation_counter += 1
                # print("self.tx=%i has input tx=%i input=%i. Recursing." %(self.txid, tx.txid, out))
                count += 1 + tx.count_ancestor_inputs(blockheight)
                # print("tx %i input (%i,%i) count now %i" % (self.txid, tx.txid, out, count))
        if blockheight > self.most_recent_block:
            self.most_recent_block = blockheight
            self.ancestorcount = count
            # print ("setting tx=%i count to %i" % (self.txid, self.ancestorcount))
        return self.ancestorcount

    def cum_size(self, blockheight):
        #incomplete, WIP
        global operation_counter
        operation_counter += 1
        if self.confirmed:
            self.cumsize = 0
            return 0
        if self.most_recent_block == blockheight and self.cumsize != None:
            return self.cumsize
        size = 0
        for tx, out in self.inputs:
            operation_counter += 1
            size += tx.cum_size(blockheight)
            #fixme: finish this and test

    def worst_case_cum_feerate(self):
        #incomplete, WIP
        global operation_counter
        operation_counter += 1


    def __str__(self):
        return "TX=%s" %str(self.txid)
    def __repr__(self):
        return str(self)

root_transaction = Transaction(txid=0, inputs=[], outputs=[0], fee=30)
root_transaction.confirmed = True


utxos = [(root_transaction, output) for output in root_transaction.outputs] # should this be a dict or set?
by_txid = {root_transaction.txid:root_transaction}
unconfirmed = {}
confirmed = {root_transaction.txid:root_transaction}

tx_count = 10000

for txid in range(1, tx_count):
    in_count = random.randint(1, 4)
    out_count = random.randint(1, 8)
    inputs = []
    for i in range(in_count):
        if utxos:
            idx = random.randint(0, len(utxos)-1)
            inputs.append(utxos[idx])
            del utxos[idx]
    outputs = range(out_count)
    tx = Transaction(txid, inputs, outputs, random.randint(1,5000))
    utxos.extend([(tx, out) for out in outputs])
    unconfirmed[txid] = tx
    by_txid[txid] = tx

# print("utxos: ", utxos)
# print("by_txid: ", by_txid)

print("ancestor counting ops so far: ", operation_counter)
my_txid = random.randint(1,tx_count)
print("TX %i's unconfirmed ancestor input count: %i" % (my_txid, by_txid[my_txid].count_ancestor_inputs(blockheight=1)))
print("operation counter: ", operation_counter)
