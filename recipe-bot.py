from recipe_scrapers import scrape_me
from ytSearch import search_youtube, search_google
from ingredient_parser import parse_ingredient
from step import Step
import re
import random

from data import substitutions, veg_substitutes, meats, spices, cuisine_spices,cuisine_meats, healthy_subs, unhealthy_subs


### GLOBAL VARIABLES ###
scraper = None
ingredients = None
parsed_ingredients = []
ingredients_name = []
steps = None
parsed_steps = None

def scrape(url):
    global scraper, ingredients, parsed_ingredients, steps
    scraper = scrape_me(url, wild_mode=True)

    ingredients = scraper.ingredients()

    for i in ingredients:
        ingredient_parse = parse_ingredient(i)
        parsed_ingredients.append(ingredient_parse) # if only a comment, remove from ingredients
        ingredients_name.append(ingredient_parse["name"])
    parse_steps(scraper.instructions())

    steps = [s.text for s in parsed_steps]

def parse_steps(instructions):
    global parsed_steps
    instructions = instructions.replace("(", " ").replace(")", " ")
    shorter_steps = instructions.split('.')
    shorter_steps = [step for step in shorter_steps if len(step) > 0]
    final_steps = []
    carry_over = ""
    print("Processing recipe steps")
    for i, step in enumerate(shorter_steps):
        annotated_step = Step(text=(step + " " +carry_over).strip(), ingredients = ingredients_name)
        nsubj_exists = False
        pos = str(annotated_step.parse[0].pos_) # check if first word is a verb
        if pos != 'VERB':
            # find root, add to list of steps
            for token in annotated_step.parse:
                relation = str(token.dep_)
                if relation == 'nsubj':  # if not an imperative/command sentence
                    nsubj_exists = True
                    break
            
            if nsubj_exists:
                if i == 0:  # if not a command and the very first sentence
                    carry_over = annotated_step.text  # save it for the next step
                else:
                    # recreate the Step object for final_steps[i - 1]
                    # print(annotated_step.text)
                    new_text = final_steps[-1].text + "; " + annotated_step.text 
                    final_steps[-1] = Step(text=new_text, ingredients = ingredients_name)
            else:
                final_steps.append(Step(text=annotated_step.text, ingredients=ingredients_name))
                print(annotated_step.text)
        else:
            final_steps.append(Step(text=annotated_step.text, ingredients=ingredients_name))
            print(annotated_step.text)
    parsed_steps = final_steps
    print("Finished")

def sub_ingredients(sub_type, cuisine=None):
    """
    types are 'vegetarian', 'non-vegetarian', 'cuisine', 'healthy', 'unhealthy'
    
    """    
    # no need to generate new text
    # just output 'substitute this for that, leave out this, etc.'
    global ingredients_name
    found_substitute = False
    meats_flat = [item for sublist in meats.values() for item in sublist] # flatten the list of lists (meats.values())
    meats_no_organs = [m for m in meats_flat if m not in meats["Organ"]]
    spices_found = 0
    for ing in ingredients_name:
        if sub_type == 'vegetarian':
            for meat in meats_flat: 
                if meat in ing:  # check if meat is a substring of ingredient name
                    found_substitute = True
                    veg = random.choice(veg_substitutes)
                    if 'broth' in ing:
                        new_ing = ing.replace(meat, veg)  # replace the substring (e.g. beef broth becomes mushroom broth)
                    elif 'sauce' in ing:
                        new_ing = ing.replace(meat, 'vegetarian')
                    else:
                        new_ing = veg
                    print(f'substitute {new_ing} for {ing}')
        elif sub_type == 'non-vegetarian':
            for veg in veg_substitutes:
                if veg in ing:
                    found_substitute = True
                    print(f'substitute {random.choice(meats_no_organs)} for {ing}')
        elif sub_type == 'cuisine':
            if ing in spices:
                spices_found += 1
                found_substitute = True
                sub = substitutions.get(ing.capitalize(), None)
                if sub:
                    if(sub['Substitution'].lower() in cuisine_spices[cuisine.capitalize()]):
                        print('substitute ' +  sub['Substitution'] + 'for ' + sub['Amount'])
                    else:
                        print(f'substitute {random.choice(cuisine_spices[cuisine.capitalize()])} for {ing}')
                    
                else:
                    print(f'substitute {random.choice(cuisine_spices[cuisine.capitalize()])} for {ing}')

            for meat in meats_flat:
                if meat in ing:
                    found_substitute = True
                    if 'broth' in ing:
                        print(f'substitute {random.choice(cuisine_meats[cuisine.capitalize()])} broth for {ing}')
                        break
                    if 'sauce' in ing:
                        print(f'substitute {random.choice(cuisine_meats[cuisine.capitalize()])} sauce for {ing}')
                        break
                    else:
                        print(f'substitute {random.choice(cuisine_meats[cuisine.capitalize()])} for {ing}')
                        break
                    
        elif sub_type == 'healthy':
            sub = healthy_subs.get(ing, None)
            if sub:
                found_substitute = True
                print("You can substitute " + sub + " for " + ing)
            else:
               for sub in healthy_subs.keys():
                   if re.search(r"\b" + re.escape(sub) + r"[\b|s\b]", ing):
                        found_substitute = True
                        new_ing = ing.replace(sub, healthy_subs[sub])
                        print("You can substitute " + new_ing + " for " + ing)
                        break
        elif sub_type == 'unhealthy':
            sub = unhealthy_subs.get(ing, None)
            if sub:
                found_substitute = True
                print("You can substitute " + sub + " for " + ing)
            else:
               for sub in unhealthy_subs.keys():
                   if re.search(r"\b" + re.escape(sub) + r"[\b|s\b]", ing):
                        found_substitute = True
                        new_ing = ing.replace(sub, unhealthy_subs[sub])
                        print("You can substitute " + new_ing + " for " + ing)
                        break
                   
    if((spices_found < 3) & (sub_type == 'cuisine')):
        found_substitute = True
        choices = []
        while len(choices) < (3 - spices_found): 
            choice = random.choice(cuisine_spices[cuisine.capitalize()])
            if(choice not in choices):
                choices.append(choice)
                print(f'you may want to add additional spice: {choice}')
                
                    
    if not found_substitute: print("already transformed, no substitutes found")

def scale_ingredients(factor):
    # need to generate new text
    global parsed_ingredients, ingredients
    for i in range(len(parsed_steps)):
        parsed_steps[i].update_amounts(factor)
        steps[i] = parsed_steps[i].text
    for i in range(len(ingredients)):
        oldQ = parsed_ingredients[i]['quantity']
        try:
            newQ = float(oldQ)*factor
            if newQ.is_integer():
                newQ = int(newQ)
            parsed_ingredients[i]['quantity'] = newQ
            parsed_ingredients[i]['sentence'] = parsed_ingredients[i]['sentence'].replace(str(oldQ), str(newQ), 1)
            ingredients[i] = parsed_ingredients[i]['sentence']
        except:
            pass
    print('The new list of ingredients: ')
    for i, ing in enumerate(ingredients):
        print(str(i + 1) + '. ', ing)
    pass
    
#interaction outside of navigation and recipe retreval 
#add current step interaction
def answer(question: str, current_step: int)->str:
    how_to = r"(?i)how to (.*)"
    substitute_for = r"(?i)substitute for (.*)"

    #how to questions
    result = re.search(how_to, question)
    if result: 
        if "that" in result.group(1):
            if len(parsed_steps[current_step].actions) > 0:
                if len(parsed_steps[current_step].ingredients) > 0:
                    return "Here is a how to video " + search_youtube("how to " + parsed_steps[current_step].actions[0] + " " + parsed_steps[current_step].ingredients[0])
                elif len(parsed_steps[current_step].tools) > 0:
                    return "Here is a how to video " + search_youtube("how to " + parsed_steps[current_step].actions[0] + " " + parsed_steps[current_step].tools[0])
                else:
                    return "Here is a how to video " + search_youtube("how to " + parsed_steps[current_step].text)
            else:
                return "Here is a how to video " + search_youtube("how to " + parsed_steps[current_step].text)
        else:
            return "Here is a how to video " + search_youtube("how to " + result.group(1))
    
    #what is questions
    if "what is" in question:
        return "This may answer your question " + search_google(question)
    
    #substitution questions
    result = re.search(substitute_for, question)
    if result: 
        sub = substitutions.get(result.group(1).capitalize(), None)
        if sub:
            return "You can substitute " + sub['Amount'] + " for " + sub['Substitution']
        else:
            return "I'm not sure if that can be substituted, but this may help " + search_google(question)
    
    #Current Step Questions

    #temperature questions
    if 'temperature' in question:
        if len(parsed_steps[current_step].temp) > 0:
            return parsed_steps[current_step].temp + " degrees"
        else:
            return "There is no temperature for this step."
    
    #How much
    if 'how much' in question or 'how many' in question:
        for ingredient in parsed_ingredients:
            if ingredient['name'].lower() in question and len(ingredient['name']) > 1:
                return ingredient['sentence']
        for ingredient in parsed_ingredients:
            if ingredient['name'].lower().split(" ")[-1] in question and len(ingredient['name']) > 1:
                return ingredient['sentence']
        return "I'm not sure about that ingredient."
    
    #How long
    if 'how long' in question:
        if len(parsed_steps[current_step].time) > 0:
            return parsed_steps[current_step].time
        else:
            return "I'm not sure about that."
    #When is it done
    if 'when' in question and 'done' in question:
        if len(parsed_steps[current_step].endWhen) > 0:
            return parsed_steps[current_step].endWhen
        else:
            return "There is no indication of when this step is finished, following the instruction in the step should be sufficient."

    return "I didn't understand your question, please ask another."


def main():
    commands = ["Start/Start over: Starts the recipe from the first step", 
                "Next: Prints the next step",
                "Back: Prints the previous step",
                "Repeat: Prints the current step", 
                "Go to step <Step Number>: Prints the specified step", 
                "Ingredients: Prints a list of ingredients", 
                "Instructions: Prints a list of instructions",
                "Help: Prints this list of commands",
                "How to <Action>: Gives a Youtube link to a how to video",
                "What is <Tool/Ingredient>: Gives a link to a search result",
                "How much/many <Ingredient>: Tells how much of the ingredient is needed",
                "What temperature: Tells the temperature for the current step",
                "How long: Tells the length of the current step", 
                "When is it done: Tells the sign to look for",
                "What can I substitute for <Ingredient>: Gives potential substutions",
                "Transform: modify the recipe by diet (veg or non-veg), cuisine, or scaling"]
    input_flag = 1
    url = input("Hello, this is RecipeBot. Please enter a url for a recipe: ").strip()
    scrape(url)
    print("Enter \'help\' for a list of commands")
    print("Enter \'Start\' to start the recipe from the first step")

    current_step = 0

    while(input_flag == 1):
       
        user = input("Please enter a command, type help for a list of available commands: ").lower().strip()
        if "start" in user:
            current_step = 0
            print("Step " + str(current_step + 1) + ". " + steps[current_step])
        elif user == "next":
            if current_step == len(steps) - 1:
                print("This is the last step")
            else:
                current_step += 1
            print("Step " + str(current_step + 1) + ". " + steps[current_step])
        elif user == "back":
            if current_step == 0:
                print("This is the first step")
            else:
                current_step -= 1
            print("Step " + str(current_step + 1) + ". " + steps[current_step])
        elif user == "repeat":
            print("Step " + str(current_step + 1) + ". " + steps[current_step])
        elif "step" in user:
            try:
                stepNum = int(user.strip().split(" ")[-1])
            
                if 1 <= stepNum <= len(steps):
                    current_step = stepNum - 1  # get the 'n' from "step n"

                    print("Step " + str(current_step + 1) + '. ' + steps[current_step])
                else:
                    print("That step doesn't exist")
            except:
                print("That step doesn't exist")
        elif user == 'ingredients':
            for i, ing in enumerate(ingredients):
                print(str(i + 1) + '. ', ing)
        elif user == 'instructions':
            for i, step in enumerate(steps):
                print(str(i + 1) + '. ', step)
        elif user == 'transform':
            choice = input("type 1 for vegetarian, 2 for non-vegetarian, 3 for cuisine, 4 for scaling, 5 for healthy, 6 for unhealthy: ").strip()
            if choice == '1':
                sub_ingredients('vegetarian')
            elif choice == '2':
                sub_ingredients('non-vegetarian')
            elif choice == '3':
                cuisine = input("what cuisine are you interested in? ").lower().strip()
                while cuisine.capitalize() not in cuisine_spices.keys():
                    print("Sorry, that cuisine is not supported")
                    cuisine = input("what cuisine are you interested in? ").lower().strip()
                sub_ingredients('cuisine', cuisine=cuisine)
            elif choice == '4':
                factor = input('What factor would you like to scale by? ')
                scale_ingredients(float(factor))
            elif choice == '5':
                sub_ingredients('healthy')
            elif choice == '6':
                sub_ingredients('unhealthy')
        elif user == 'help':
            for i, command in enumerate(commands):
                print(str(i + 1) + '. ', command)
        elif user == 'stop':
            print('Terminated')
            input_flag = 0
            break
        else:
            print(answer(user, current_step))
        
        

if __name__ == '__main__':
    main()



# Meat: beef, chicken, pork, lamb, turkey, duck, venison, rabbit, bison, goat, veal, boar, camel.
# Fish: salmon, tuna, cod, halibut, trout, mackerel, sardines, tilapia, catfish, sea bass, snapper, swordfish, and haddock.
# Seafood: shrimp, crab, lobster, scallops, clams, oysters, and mussels.
# Organ meats: liver, heart, kidney, and tripe.
# Deli meats: ham, turkey, roast beef, pastrami, corned beef, and salami.
# Sausages: bratwurst, chorizo, andouille, kielbasa, Italian sausage, and breakfast sausage, sausage.


#cuisin subs
#Jamaican jerk: allspice, nutmeg, black pepper, thyme, cayenne pepper, paprika, sugar, salt, garlic, and ginger
#Mexican: annatto, dried oregano, cumin, clove, cinnamon, black pepper, allspice, and garlic
#Cajun: paprika, mustard powder, garlic, black pepper, onion, dried oregano, cumin, caraway, crushed red pepper, cayenne, thyme, celery seed, and bay leaves
#Indian: turmeric, cardamom, cinnamon, cloves, cumin, coriander, black pepper, curry powder, and nutmeg
#Moroccan: cumin, ginger, turmeric, paprika, coriander, cinnamon, cardamom,


#Tofu
#Tempeh
#Seitan (also known as wheat meat or wheat gluten)
#Legumes (e.g. lentils, chickpeas, black beans)
#Mushrooms (e.g. portobello, shiitake)
#Quorn (a type of mycoprotein)
#Textured vegetable protein (TVP)
#Nutritional yeast (a source of vegan protein and B vitamins)
#Eggplant
#Jackfruit
#Beyond patty
#Tofu dog


