import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import re
import csv

MLA_PRODUCTO = []
PRODUCTO_PRICE = []
TITLES_PRODUCTOS = []
LINKS_PRODUCTOS = []


def main():
#Ingresar objeto a buscar
    keyword = input('Objeto a Buscar: ')
    driver = configChrome()
    
    # Navigating to MercadoLibre Argentina
    driver.get("https://www.mercadolibre.com.ar")

    # Maximiza Ventana
    driver.maximize_window()

    # Input de busqueda de mercado libre
    inputSerch = driver.find_element(By.CLASS_NAME, "nav-search-input")

    # Introducir texto en el input y preciona ENTER
    inputSerch.send_keys(keyword, Keys.ENTER)

    # Configurar de menor a mayor precio
    configProducts(driver, 'ASC')
    
    #obtine todo los porductos de una pagina, segundo argumento la cantidad si es necesario 
    obtenerProductos(driver)

    #pasa a la segunda pagian
    pasarPagina(driver)

    #obtine 10 productos de la segunda pagina
    obtenerProductos(driver, 12)

    #configura el listado de productos de Mayor a Menor
    configProducts(driver, 'DESC')

    #obtine todo los productos
    obtenerProductos(driver)

    #pasa a la segunda pagina
    pasarPagina(driver)
    
    #obtiene 10 productos
    obtenerProductos(driver, 12)

    productos = crearDict(keyword)
    #guardarlos en un csv o json

    # Close the browser after 5 seconds
    time.sleep(30)
    driver.quit()

    #print(productos)

    crearCSV(keyword, productos)
   
        
def configChrome():
    # Setting up and running the Chrome browser
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    return driver
   

def configProducts(driver, order):
    try:
        btnOrderBy = driver.find_element(By.XPATH, "//*[@id=':R2m55ee:-trigger']")
        time.sleep(5)
        btnOrderBy.click()
    except:
        print('No se encontro el boton')
        return
        

    order_options = {
        'ASC': "//*[@id=':R2m55ee:-menu-list-option-price_asc']",
        'DESC': "//*[@id=':R2m55ee:-menu-list-option-price_desc']"
    }

    if order in order_options:
        try:
            time.sleep(2)  
            order_button = driver.find_element(By.XPATH, order_options[order])
            time.sleep(1) 
            order_button.click()
        except:
            print(f"Error: No se encontró el botón para ordenar en {order}.")
    else:
        print(f"Error: Orden '{order}' no válido. Usa 'ASC' o 'DESC'.")


def obtenerProductos(driver, limit=None):
    
    productsTitlesWeb = driver.find_elements(By.CLASS_NAME, "poly-component__title")
    productsPriceWeb = driver.find_elements(By.XPATH, '//*/div[2]/div/div/span/span[2]')
    productsLinkWeb = driver.find_elements(By.XPATH, "//*/div/h2/a")

    if limit == None:
        for title in productsTitlesWeb[:limit]:
            TITLES_PRODUCTOS.append(title.text)
        
        for price in productsPriceWeb:
            floatPrice = float(price.text.replace(".",""))
            PRODUCTO_PRICE.append(floatPrice)
                
        for link in productsLinkWeb:
            productLink = link.get_attribute("href")
            match = re.search(r"MLA-?(\d+)", productLink)
            MLA_PRODUCTO.append(match.group(1))
            LINKS_PRODUCTOS.append(productLink)

    for title in productsTitlesWeb[:limit]:
            TITLES_PRODUCTOS.append(title.text)

    for price in productsPriceWeb[:limit]:
        floatPrice = float(price.text.replace(".",""))
        PRODUCTO_PRICE.append(floatPrice)
            
    for link in productsLinkWeb[:limit]:
        productLink = link.get_attribute("href")
        match = re.search(r"MLA-?(\d+)", productLink)
        MLA_PRODUCTO.append(match.group(1))
        LINKS_PRODUCTOS.append(productLink)


def pasarPagina(driver):
    actions = ActionChains(driver)
    
    try:
        btnSiguintePag = driver.find_element(By.XPATH, '//*[@id="root-app"]/div/div[3]/section/nav/ul/li[12]/a')
        divFooter = driver.find_element(By.XPATH, '//*[@id="ui-search-bottom-ads__wrapper"]/div')
        actions.move_to_element(divFooter).perform()
        time.sleep(5)
        btnSiguintePag.click()
    except:
        print('No se puedo pasar a la segunda paguina')
        return


def crearDict(keyword):
    productos = {}

    for title, price, links, mla in zip(TITLES_PRODUCTOS,PRODUCTO_PRICE, LINKS_PRODUCTOS, MLA_PRODUCTO):
        productos[mla] = {
            'keyword' : keyword,
            'MLA_ID' : mla,
            'Product_name' : title,
            'Price': price,
            'URL' : links
        }
        
        
    return productos


def crearCSV(keyword, productos):
    with open(f'{keyword}.csv', 'w', newline='', encoding='utf-8') as file:
        w = csv.writer(file)
        
        w.writerow(['MLA_ID', 'keyword', 'Product_name', 'Price', 'URL'])
        
        
        for producto in productos.values(): 
            w.writerow([
                producto['MLA_ID'],
                producto['keyword'],
                producto['Product_name'],
                producto['Price'],
                producto['URL']
            ])

    print('Documento Creado')


main()