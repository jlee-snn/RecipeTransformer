from parser.RecipeParse import RecipeParse
import json
import math
from sys import argv

ALL_FOOD_GROUPS = [
    "Dairy and Egg Products",
    "Spices and Herbs",
    "Baby Foods",
    "Fats and Oils",
    "Poultry Products",
    "Soups, Sauces, and Gravies",
    "Sausages and Luncheon Meats",
    "Breakfast Cereals",
    "Fruits and Fruit Juices",
    "Pork Products",
    "Vegetables and Vegetable Products",
    "Nut and Seed Products",
    "Beef Products",
    "Beverages",
    "Finfish and Shellfish Products",
    "Legumes and Legume Products",
    "Lamb, Veal, and Game Products",
    "Baked Products",
    "Snacks",
    "Sweets",
    "Cereal Grains and Pasta",
    "Fast Foods",
    "Meals, Entrees, and Sidedishes",
    "Ethnic Foods",
    "Restaurant Foods",
]

NON_VEGETARIAN_GROUPS = [
    "Sausages and Luncheon Meats",
    "Pork Products",
    "Beef Products",
    "Finfish and Shellfish Products",
    "Lamb, Veal, and Game Products",
    "Poultry Products",
    "Ethnic Foods"
]

NON_PESCETARIAN_GROUPS = [
    "Sausages and Luncheon Meats",
    "Pork Products",
    "Beef Products",
    "Lamb, Veal, and Game Products",
    "Poultry Products",
    "Ethnic Foods"
]

MEAT_AND_FISH_GROUPS = [
    "Sausages and Luncheon Meats",
    "Pork Products",
    "Beef Products",
    "Finfish and Shellfish Products",
    "Lamb, Veal, and Game Products",
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
        if nut_info[u'group'] in groups:
            print "Attempting to replace:", nut_info[u'description']
            print nut_info[u'group']
            replacement = find_similar_food(nut_info, groups, food_data)
            print "Replacing with:", replacement[u'description']
            print replacement[u'group']
            subs[ingredient["name"]] = replacement[u'description']
    for ingredient in recipe["ingredients"]:
        if ingredient["name"] in subs:
            ingredient["name"] = subs[ingredient["name"]]

    return recipe

def to_vegetarian(url):
    return filter_food_groups(url, NON_VEGETARIAN_GROUPS)

def to_pescetarian(url):
    return filter_food_groups(url, NON_PESCETARIAN_GROUPS)

def remove_unhealthy(url, nutrient_name):
    """
    Removes ingredient in recipe with highest amounts of specified
    ingredients, replaces them with similar foods that are healthier
    """

    with open("processed-food-data.json", "r") as f:
        "Loading food data...."
        food_data = json.loads(f.read())

    recipe = RecipeParse(url)
    subs = {}

    highest_amount = float("-inf")
    nutrient = {}
    ingredient_name = ""

    for ingredient in recipe["ingredients"]:
        nut_info = resolve_ingredient(ingredient["name"], food_data)
        amnt = get_amount_of_nutrient(nut_info, nutrient_name, "g")
        if amnt > highest_amount:
            highest_amount = amnt
            nutrient = nut_info
            ingredient_name = ingredient["name"]

    print "Attempting to replace: ", nut_info[u'description']
    print "Food group ", nut_info['group']
    print "Nutrient content", highest_amount

    replacement = find_healthier_food(nut_info, nutrient_name, amnt, food_data)

    print "Replacing with:", replacement[u'description']
    print replacement['group']
    print "Nutrient Content", get_amount_of_nutrient(replacement, nutrient_name, "g")
    subs[ingredient_name] = replacement[u'description']

    for ingredient in recipe["ingredients"]:
        if ingredient["name"] in subs:
            ingredient["name"] = subs[ingredient["name"]]

    return recipe

def get_amount_of_nutrient(nut_info, nutrient_name, unit):
    total_nut_amount = [n for n in nut_info["nutrients"]
            if n["units"] == unit and n["description"] == nutrient_name][0]["value"]
    return total_nut_amount

def to_lowfat(url):
    remove_unhealthy(url, u'Total lipid (fat)')

def resolve_ingredient(name, data):
    """
    Takes an ingredient name (as given by our allrecipies parser), and returns a
    dict from the FDA database with the closest match for this ingredient.
    """
    name_tokens = name.lower().replace(',','').split()
    best_match = {}
    best_match_tokens = []
    matching_words = 0
    for ingredient in data:
    	ingredient_tokens = ingredient[u'description'].lower().replace(',','').split()
    	matches = [itm for itm in ingredient_tokens if itm in name_tokens]
    	"""
    	Figured that the best match would be the one with the shortest ingredient name length if there is
    	a conflict where two ingredients have the same number of matches.
    	"""
    	if len(matches) == matching_words:
    		if len(ingredient_tokens) < len(best_match_tokens):
    			best_match = ingredient
    			best_match_tokens = ingredient_tokens
    	if len(matches) > matching_words:
    		matching_words = len(matches)
    		best_match = ingredient
    		best_match_tokens = ingredient_tokens
    return best_match

def find_similar_food(ingredient, groups, data):
    """
    Takes an ingredient (the whole dict) and a list of banned groups, and finds
    a similar ingredient in the food database
    """
    best_distance = float("inf")
    best_match = {}
    for item in data:
    	if item[u'group'] not in groups:
            distance = calculate_distance(ingredient, item)
            if distance < best_distance:
                    best_distance = distance
                    best_match = item
    print best_distance
    return best_match

def find_healthier_food(ingredient, nutrient_name, amount, data, percent_diff_acceptable=0.2):
    """
    Finds shortest distance food with less of specified nutrient than original,
    for most food groups, also ensures we get one in the same group, but treats
    all meats the same in terms of food groups
    """
    best_distance = float("inf")
    best_match = {}

    if ingredient["group"] in MEAT_AND_FISH_GROUPS:
        acceptable_groups = MEAT_AND_FISH_GROUPS
    else:
        acceptable_groups = [ingredient["group"]]


    for item in data:
        total_nut_amount = get_amount_of_nutrient(item, nutrient_name, "g")
        percent_difference = total_nut_amount - amount/ float(amount)

        if percent_difference <= percent_diff_acceptable and item["group"] in acceptable_groups:
            distance = calculate_distance(ingredient, item)
            if distance < best_distance:
                best_distance = distance
                best_match = item

    if len(best_match.keys()) == 0:
        if percent_diff_acceptable < 0.01:
            "Giving up, no healthier foods availabe"
            return ingredient
        else:
            print "Could not find better ingredient! Trying again with", percent_diff_acceptable * 0.8
            return find_healthier_food(ingredient, nutrient_name, amount, data,
                    percent_diff_acceptable * 0.8)

    return best_match

def calculate_distance(ingredient, arg_ingredient):
	"""
	Each ingredient has different numbers of nutrients, so the distance is calculated
	by only using nutrients present in both ingredients (of the first 5 nutrients).
	"""
	distance = 0.0
	ingredient_nutrients = {}
	arg_ingredient_nutrients = {}
	for i in range(0, 4):
		ingredient_nutrients[ingredient[u'nutrients'][i][u'description']] = ingredient[u'nutrients'][i][u'value']
	for i in range(0, 4):
		arg_ingredient_nutrients[arg_ingredient[u'nutrients'][i][u'description']] = arg_ingredient[u'nutrients'][i][u'value']
	for nutrient in ingredient_nutrients.keys():
		count = 0
		if nutrient in arg_ingredient_nutrients.keys():
			count = float(ingredient_nutrients[nutrient]) - float(arg_ingredient_nutrients[nutrient])
			count = count * count
			distance = distance + count
	distance = 	float(math.sqrt(distance))
	return distance



def pretty_print_dict(dict):
    print json.dumps(dict, indent = 4)
    return

to_lowfat(argv[1])
