import spacy
import re
kitchen_tools = [
    'spoon',
    'fork',
    'knife',
    'spatula',
    'ladle',
    'whisk',
    'tongs',
    'grater',
    'peeler',
    'can opener',
    'bottle opener',
    'corkscrew',
    'scissors',
    'mixing bowl',
    'measuring cups',
    'measuring spoons',
    'cutting board',
    'colander',
    'strainer',
    'rolling pin',
    'pastry brush',
    'oven mitts',
    'pot holder',
    'kitchen shears',
    'grill brush',
    'basting brush',
    'pizza cutter',
    'ice cream scoop',
    'garlic press',
    'nutcracker',
    'egg slicer',
    'cheese slicer',
    'melon baller',
    'canister',
    'jar opener',
    'funnel',
    'salad spinner',
    'kitchen timer',
    'food thermometer',
    'baking dish',
    'roasting pan',
    'cake pan',
    'muffin tin',
    'baking sheet',
    'pie dish',
    'ramekins',
    'mixing spoons',
    'basting spoon',
    'slotted spoon',
    'skimmer',
    'soup ladle',
    'meat thermometer',
    'meat tenderizer',
    'potato masher',
    'potato peeler',
    'meat fork',
    'meat cleaver',
    'bread knife',
    'paring knife',
    'utility knife',
    'chef knife',
    'steak knives',
    'scalloped knife',
    'microplane grater',
    'spice grater',
    'zester',
    'fish scaler',
    'fish spatula',
    'skillet',
    'saucepan',
    'stockpot',
    'dutch oven',
    'wok',
    'roasting pan',
    'griddle',
    'paella pan',
    'frying pan',
    'saute pan',
    'double boiler',
    'baking dish',
    'casserole dish',
    'loaf pan',
    'bundt pan',
    'springform pan',
    'sheet pan',
    'muffin tin',
    'cake pan',
    'pie dish',
    'ramekins',
    'crockpot',
    'rice cooker',
    'slow cooker',
    'pressure cooker',
    'grill pan',
    'smoker',
    'stovetop griddle',
    'electric griddle',
    'grill basket',
    'stir fry pan',
    'tagine',
    'fondue pot',
    'bean pot',
    'tajine',
    'broiler pan',
    'brazier',
    'chafing dish',
    'fryer',
    'popcorn maker',
    'crepe pan',
    'milk frother',
    'moka pot',
    'espresso machine',
    'coffee maker',
    'tea kettle',
    'blender',
    'food processor',
    'stand mixer',
    'hand mixer',
    'immersion blender',
    'juicer',
    'citrus juicer',
    'food chopper',
    'meat grinder',
    'bread maker',
    'toaster',
    'microwave oven',
    'gas range',
    'electric range',
    'oven',
    'cooktop',
    'hood',
    'dishwasher',
    'refrigerator',
    'freezer',
    'wine cooler',
    'trash can',
    'kitchen island',
    'pantry',
    'utensil holder',
    'knife block',
    'cutting board',
    'dish rack',
    'pot rack',
    'apron',
    'oven mitts',
    'pot holder',
    'dish towels'
]

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
        timeWords = ["second", "seconds", "minute", "minutes", "hour", "hours"]
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