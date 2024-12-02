from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

chrome_options = Options()

service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)

data = []
j = 1 

def extract_products(products):
    global j  
    for product in products:
        print(j)
        try:
            product_SalePrice = product.find_element(By.CSS_SELECTOR, ".amount").text.replace('AED ', '')
            product_brand = product.find_element(By.CSS_SELECTOR, ".sc-66eca60f-24.fPskJH").text
            product_avgRating = product.find_element(By.CSS_SELECTOR, ".bLaxTl").text
            old_price = ""
            try:
                product_Price = product.find_element(By.CSS_SELECTOR, ".oldPrice").text.replace('AED ', '')
                old_price = product_Price
            except:
                old_price = "N/A"

            express = ""
            try:
                product_express = product.find_element(By.CSS_SELECTOR, "img[alt='noon-express']").get_attribute("alt")
                if product_express:
                    express = "Y"
                else:
                    express = "N"
            except:
                express = "N"

            product_Link = product.find_element(By.XPATH, ".//a")
            link = product_Link.get_attribute("href")
            sku = product_Link.get_attribute("id")

            expectedDelivery = ""
            try:
                product_expectedDelivery = product.find_element(By.CSS_SELECTOR, ".sc-66eca60f-33.ejILia").text
                expectedDelivery = product_expectedDelivery
            except:
                expectedDelivery = "N/A"

            sponsor = ""
            try:
                product_sponsor = product.find_element(By.CSS_SELECTOR, ".sc-66eca60f-23.AkmCS").text
                sponsor = "Y"
            except:
                sponsor = "N"

            ratingAvg = ""
            ratingCount = ""
            if product_avgRating:
                rating_parts = product_avgRating.split("\n")
                if len(rating_parts) >= 2:
                    ratingAvg = rating_parts[0]
                    ratingCount = rating_parts[1]
            else:
                ratingAvg = "N/A"
                ratingCount = "N/A"

            print(link)
            
        
            sku = sku.split("-")[1][:8]
            converted_date = datetime.now().strftime("%d-%b-%Y")
            brand = product_brand.split("\n")[0].split(" ")[0]
            name = link.split("/")[4]
           
            data.append({
                "Date": converted_date,
                "SKU": sku,
                "Name": name,
                "Brand": brand,
                "Avg Rating": ratingAvg,
                "Rating Count": ratingCount,
                "Sponsor": sponsor,
                "Price": old_price,
                "Sales Price": product_SalePrice,
                "Express": express,
                "Rank": j,
                "Link": link,
                "Delivery": expectedDelivery
            })

            j += 1  
            print("-----------------------------")
        except Exception as e:
            print("Error processing product:", e)
          
i = 1
while True:
    try:
        print(f"data {i}")
        url = f"https://www.noon.com/uae-en/sports-and-outdoors/exercise-and-fitness/yoga-16328/?limit=150&page={i}&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc"
        driver.get(url)

        product_list_container = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".sc-61baf88b-7.dRkNeo.grid"))
        )

        products = product_list_container.find_elements(By.CSS_SELECTOR, ".sc-980f39e6-0.iNoaVH.wrapper.productContainer")
        extract_products(products)

        if i >= 2:  
            break
        i += 1
    except Exception as e:
        print("No more pages or encountered an error:", e)
        break

csv_file = 'scraped_data.csv'
df = pd.DataFrame(data)
try:
    df.to_csv(csv_file, index=False)
    print(f"Data successfully saved to {csv_file}")
except Exception as e:
    print(f"Error writing to CSV: {e}")


df['Sales Price'] = pd.to_numeric(df['Sales Price'].replace('N/A', '0'), errors='coerce')
df['Price'] = pd.to_numeric(df['Price'].replace('N/A', '0'), errors='coerce')


max_price_product = df.loc[df['Sales Price'].idxmax()]
min_price_product = df.loc[df['Sales Price'].idxmin()]

print(f"Max Price Product: {max_price_product['Name']} - Price: {max_price_product['Sales Price']}")
print(f"Min Price Product: {min_price_product['Name']} - Price: {min_price_product['Sales Price']}")


brand_counts = df['Brand'].value_counts()

plt.figure(figsize=(24, 6))


plt.subplot(1, 2, 1)
brand_counts.plot(kind='bar', color='skyblue')
plt.title('Products by Brand')
plt.xlabel('Brand')
plt.ylabel('Number of Products')

# Scatter plot for max and min price products
plt.subplot(1, 2, 2)
plt.scatter([max_price_product['Name'], min_price_product['Name']], 
            [max_price_product['Sales Price'], min_price_product['Sales Price']], 
            color=['red', 'green'])
plt.title('Max and Min Price Products')
plt.xlabel('Product Name')
plt.ylabel('Sales Price')
plt.xticks(rotation=15)
plt.grid()

plt.tight_layout()
plt.show()

driver.quit()
