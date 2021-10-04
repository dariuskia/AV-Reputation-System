import random
import matplotlib.pyplot as plt
import matplotlib
import time
import numpy as np

OPPOSITE = {1: 0, 0: 1}

class AV:
    def __init__(self, model, vID, status):
        self.model = model
        self.vID = vID
        self.status = status
        #status: 0 = malicious, 1 = not malicious

    def __repr__(self):
        return self.vID + f"({self.status})"

    def broadcast(self, recipients):
        witnesses = random.sample(recipients, int(len(recipients)*random.random()*0.5)) # picks n number of witnesses where n is between 0 and 50% of the recipients
        r = random.choice(self.model.RSUs) # pick a random RSU
        transaction = {} # key is witness, value is witness's score
        expectedValue = self.status # change later once more statuses
        for w in witnesses:
           transaction[w] = w.score(self, expectedValue) # have each witness score the transaction
        r.updateOperatingRep(self, transaction, 0.05)
        for w in witnesses:
           r.updateReportingRep(w, transaction, 0.05) # update the reputation of each witness

    def score(self, sender, expected):
        #score must take into account the status of the AV that is witnessing the transaction
        # score = random.choice([0, 1]) # make it depend on status
        # if a vehicle that is scoring a transaction has its reputation fall below 0.4 disregards the scoring from the vehicle
        return expected if self.status == 1 else OPPOSITE[expected]
        # add nuance; good vehicles sometimes give bad scores

class RSU:

    def __init__(self, model, rID):
        self.model = model
        self.rID = rID
        self.operating_scores = {} # key is the av, value is its current reputation; should be stored by BS, RSU stores transaction info
        self.reporting_scores = {}
    
    def __repr__(self):
        return self.rID

    def updateOperatingRep(self, sender, transaction, velocity):
        # update the reputation of sender AV using the transaction
        # does this by iterating through the witness scores for the transaction and get weighted average
        tRep = 0
        repSum = sum([self.operating_scores[w] for w in transaction.keys()])
        for w in transaction.keys():
            weight = self.operating_scores[w] / repSum
            tRep += transaction[w] * weight

        currRep = self.operating_scores[sender]
        self.operating_scores[sender] = tRep * velocity + currRep * (1-velocity) # maybe change: first few transactions shouldn't have 95% weight; maybe have the 95 start off low and get higher over time
        # update reputation for every RSU
        # TO-DO weight based on recency AND number of witnesses
        

    def updateReportingRep(self, witness, transaction, velocity):
        # Calculate the average score based on the same method as used in Operating Reputation
        # 0.2 rep vehicle (malicious) reports 0 on a good transaction and 0.9 rep vehicle (non-malicious) reports 1 on a good transaction
        oRep = 0
        repSum = sum([self.operating_scores[w] for w in transaction.keys()])
        for w in transaction.keys():
            weight = self.operating_scores[w] / repSum
            oRep += transaction[w] * weight
        deviation = 1 - ((transaction[w] * weight) - oRep)
        currRep = self.reporting_scores[witness]
        self.reporting_scores[witness] = deviation * velocity + currRep * (1-velocity)


class Model:
    def __init__(self, nAVs, nRSUs, propNormal):
        # 270 status 0, 15 status 1, 10 status 2, 5 status 3
        # Decide how many AVs of each type (not random -> could use proportions later on in the simulation)
        # 90% good vehicles and 10% malicous vehicles
        statuses = [1]*int(round(nAVs*propNormal)) + [0]*(int(round(nAVs*(1-propNormal))))
        self.AVs = [AV(self, f"AV_{i}", statuses[i]) for i in range(nAVs)]
        self.RSUs = [RSU(self, f"RSU_{i}") for i in range(nRSUs)]
        # self.current_tick = 0
    
    def initialize_reputations(self):
        reps = {av: 1.0 for av in self.AVs} # give each av a default of 1.0
        for r in self.RSUs:
            r.operating_scores = reps # set the default operating score for each rsu
            r.reporting_scores = reps # set the default reporting score for each rsu
    
    def step(self):
        # tick = self.current_tick % 1440 # get tick of current day
        # if tick is 0:
        #     # end of day
        pass
        
    def plotOperating(self):
        scores = self.RSUs[0].operating_scores
        x1 = [str(i) for i in scores.keys()]
        y1 = list(scores.values()) 
        plt.xticks(rotation=90)
        plt.bar(x1, y1)
        plt.show()

    def plotReporting(self):
        scores = self.RSUs[0].reporting_scores
        x1 = [str(i) for i in scores.keys()]
        y1 = list(scores.values()) 
        plt.xticks(rotation=90)
        plt.bar(x1, y1)
        plt.show()

    def run(self, n_transactions):
        self.initialize_reputations()
        for i in range(n_transactions):
            av = random.choice(self.AVs)
            nRecipients = int(random.random()*10+10)
            recipients = random.sample([v for v in self.AVs if v is not av], nRecipients) # pick recipients as long as they aren't the sender
            av.broadcast(recipients)
        # for (int i = 0; i < n_days; i++){ broadcast ()}

model = Model(30, 1, 0.9) # start off with 1 rsu
model.run(2000)
scores = model.RSUs[0].reporting_scores
print(scores)
model.plotReporting()