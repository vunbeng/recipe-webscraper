from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re
import csv

# creates the chrome driver
browser_driver = Service(r"[driver path]")
page = webdriver.Chrome(service=browser_driver)

# gets the recipe data of each breakfast type
def getRecipeData(givenLink):
    page.get(givenLink)
    i = 1
    recipes = []

    while True:
        try:
            breakfast = page.find_element(By.ID, f"mntl-card-list-items_{i}-0")
            name = breakfast.find_element(By.CLASS_NAME, "card__title").text
            link = breakfast.get_attribute("href")
        
            recipes.append({"name": name, "link": link})
            i += 1
        except NoSuchElementException:
            break
        
    # goes through each recipe to find the protein data and fat data
    for recipe in recipes:
        page.get(recipe["link"])
        try:
            nutri_data = page.find_element(By.CLASS_NAME, "mm-recipes-nutrition-facts-summary__table").text
            protein = re.search(r"(\d+g)(?=\sProtein)", nutri_data).group()
            fat = re.search(r"(\d+g)(?=\sFat)", nutri_data).group()
        except:
            protein = "NA"
            fat = "NA"
        recipe["protein"] = protein
        recipe["fat"] = fat
    return recipes
    
# creates the csv file to store the recipes of a breakfast type
def createRecipeFile(breakfast, recipes):
    file = open(f"{breakfast}.csv", "w", newline="")
    writer = csv.writer(file)

    writer.writerow(["Name", "Protein", "Fat", "Link"])

    for r in recipes:
        writer.writerow([r["name"], r["protein"], r["fat"], r["link"]])

# gets each breakfast type and its link (that has all the recipes)
def getBreakfastType(page):
    breakfastInfo = []

    num = 1
    while True:
        try:
            page.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # finds the breakfast type and create a csv for it
            breakfast = page.find_element(By.ID, f"mntl-taxonomy-nodes__item_{num}-0")
            breakfastLink = breakfast.find_element(By.TAG_NAME, "a").get_attribute("href")
            print(breakfastLink)
            print(f"{breakfast.text}'s recipes scraped!") # for some reasons, the last 6 breakfast types are white space; must fix

            breakfastInfo.append({"breakfast": breakfast.text, "link": breakfastLink})

            num += 1
        except NoSuchElementException:
            break
    return breakfastInfo

# gets the main page
page.get("https://www.allrecipes.com/recipes/78/breakfast-and-brunch/")
page.find_element(By.PARTIAL_LINK_TEXT, "View").click() # allows other types of breakfast links to be loaded

# gets each breakfast type via the function
breakfast = getBreakfastType(page)

# iterate through each breakfast type and get its recipes
for b in breakfast:
    breakfastRecipes = getRecipeData(b["link"])
    createRecipeFile(b["breakfast"], breakfastRecipes)
    print(f"{b['breakfast']}.csv has been created!")