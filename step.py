import spacy
import re
from data import kitchen_tools

class Step:
    #step's text and parsed recipe ingredients list
    def __init__(self, text, ingredients):
        self.text = text
        self.recipeIngredients = ingredients
        self.parse = self.parse_text()
        self.actions = self.verbs()
        self.ingredients = self.dobj()
        self.tools = self.pobj()
        self.endWhen = self.get_step_end()
        self.time = self.get_step_time()
        self.temp = self.get_temperature()

    def parse_text(self):
        nlp = spacy.load("en_core_web_sm")
        return nlp(self.text)
    
    def verbs(self):
        verb_list = []
        for token in self.parse:
            if token.pos_ == "VERB":
                verb_list.append(token.text)
        return verb_list
    
    def dobj(self):
        #check list of ingredients for ingredients used in step
        pattern = re.compile('|'.join(self.recipeIngredients))
        return [match.group(0) for match in re.finditer(pattern, self.text)]
    
    
    def pobj(self):
        #find mentioned tools
        pattern = re.compile('|'.join(kitchen_tools))
        return [match.group(0) for match in re.finditer(pattern, self.text)]

    def get_step_end(self):
        end = ''
        endWords = ['until','once']
        for word in endWords:
            if word in self.text:
                end = word + " " + self.text.split(word)[-1] 
        return end

    
    def get_step_time(self):
        time = ""
        timeWords = ["second", "seconds", "minute", "minutes", "hour", "hours", "day", "days"]
        for token in self.parse:
            if token.dep_ == "nummod" and token.head.text in timeWords:
                if len(list(token.children)) > 0:
                    children = ' '.join([str(child) for child in token.children])
                    time = time + " " + children + " " + token.text + " " + token.head.text
                else:
                    time = time + " " + token.text + " " + token.head.text
        return time
    
    def get_temperature(self):
        for token in self.parse:
            if token.dep_ == "nummod" and token.head.text == "degrees":
                if len(list(token.children)) > 0:
                    children = ' '.join(token.children)
                    return children + " " + token.text
                else:
                    return token.text
        return ""
    
    def update_amounts(self, factor):
        nums = [int(i) for i in self.text.split() if i.isdigit()]
        maskTemp = [int(i) for i in self.temp.split() if i.isdigit()]
        maskTime = [int(i) for i in self.time.split() if i.isdigit()]
        mask = maskTemp + maskTime
        nums = [i for i in nums if i not in mask]

        for num in nums:
            self.text = self.text.replace(str(num) + " ", str(num*factor)+ " ")