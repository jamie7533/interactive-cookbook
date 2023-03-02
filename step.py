import spacy

class Step:
    def __init__(self, text, ingredients):
        self.text = text
        self.recipeIngredients = ingredients
        self.parse = self.parse_text()
        self.actions = self.verbs()
        self.ingredients = self.dobj()
        self.tools = self.pobj_list()
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
        dobj_list = []
        for token in self.parse:
            if token.dep_ == "dobj" and token.text in self.recipeIngredients:
                dobj_list.append(token.text)
        return dobj_list
    
    def pobj(self):
        pobj_list = []
        for token in self.parse:
            if token.dep_ == "pobj" and token.text not in self.recipeIngredients:
                pobj_list.append(token.text)
        return pobj_list
    
    def get_step_time(self):
        time = ""
        timeWords = ["second", "seconds", "minute", "minutes", "hour", "hours"]
        for token in self.parse:
            if token.dep_ == "nummod" and token.head.text in timeWords:
                time = time + " " + token.text + " " + token.head.text
        return time
    
    def get_temperature(self):
        for token in self.parse:
            if token.dep_ == "nummod" and token.head.text == "degrees":
                return token.text
        return ""