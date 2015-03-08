from parser.RecipeParse import RecipeParse
import json
from random import randrange

NON_VEGETARIAN_GROUPS = [
    "Sausages and Luncheon Meats",
    "Pork Products",
    "Beef Products",
    "Finfish and Shellfish Products",
    "Lamb, Veal, and Game Products",
    "Poultry Products"
]

NON_PESCETARIAN_GROUPS = [
    "Sausages and Luncheon Meats",
    "Pork Products",
    "Beef Products",
    "Lamb, Veal, and Game Products",
    "Poultry Products"
]

def filter_food_groups(url, groups):
    """
    Takes a recipe url and a list of food groups to avoid, replaces ingredients
    in the ingredient list with suitable alternatives not in the banned groups
    """
    with open("food-data.json", "r") as f:
        print "Loading data from food-data.json"
        food_data = json.loads(f.read())

    recipe = RecipeParse(url)

    subs = {}

    for ingredient in recipe["ingredients"]:
        nut_info = resolve_ingredient(ingredient["name"], food_data)
        if nut_info["group"] in groups:
            print "Attempting to replace ", nut_info["description"]
            replacement = find_similar_food(nut_info, groups, food_data)
            print "Replacing with", replacement["description"]
            subs[ingredient["name"]] = replacement["description"]

    for ingredient in recipe["ingredients"]:
        if ingredient["name"] in subs:
            ingredient["name"] = subs[ingredient["name"]]

    return recipe

def to_vegetarian(url):
    return filter_food_groups(url, NON_VEGETARIAN_GROUPS)

def to_pescetarian(url):
    return filter_food_groups(url, NON_PESCETARIAN_GROUPS)

def resolve_ingredient(name, data):
    """
    Takes an ingredient name (as given by our allrecipies parser), and returns a
    dict from the FDA database with the closest match for this ingredient.
    """

    # obviously broken
    return data[randrange(0,6000)]

def find_similar_food(ingredient, groups, data):
    """
    Takes an ingredient (the whole dict) and a list of banned groups, and finds
    a similar ingredient in the food database
    """

    # obviously broken
    return data[randrange(0,6000)]

print to_vegetarian("http://allrecipes.com/Recipe/Asian-Beef-with-Snow-Peas/Detail.aspx?soid=recs_recipe_2")
