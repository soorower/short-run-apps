import imghdr
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from discord_webhook import DiscordWebhook, DiscordEmbed
webhook = DiscordWebhook(
    url='https://discord.com/api/webhooks/966010327126933524/Ebs_zHX_QHNWkxRRGGJmTrVhUFI2D4vP8qulIc9KZuBUOIKih0DXZXaZChwzsSQlbFu3', username="EuroBasket Scraped File")



p_url = 'http://api.scrape.do?token=ad3d00b0025842afb0f1620cf7f3301dd3ddcc23d1a&url='
url = p_url + 'https://www.priceline.com.au/'
r = requests.get(url)
soup = bs(r.content,'html.parser')

urls_table = soup.findAll('li',attrs ={'class':'level0 nav-1 first level-top parent'})[1].find('ul').findAll('li')
cate1_urls = [x.find('a')['href'] for x in urls_table[1:12]]
cate1_names = [x.find('a').text for x in urls_table[1:12]]

#----All the multiprocessing part---------------------------------
def threading(links):
    res_html = []
    def fetch(session, url):
        with session.get(url) as response:
            if response.status_code == 200:
                res_html.append(response)
    def main():
        with ThreadPoolExecutor(max_workers=200) as executor:
            with requests.Session() as session:
                # print('Multithreading...')

                for link in links:
                    executor.map(fetch, [session], [link])
                executor.shutdown(wait=True)
    main()
    return res_html

#--------Scraping a list of products and saving them to final list(final_list)---------------------
def product_scraper(mother_cate_name,child_cate1_name,child_cate2_name,links):
    lists = links
    final_res_html3 = []
    #--------------sending requests five each time through threading-----------------------
    loop = int(len(lists)/5)
    if loop==0:
        loop = 1
    i_list = [x*5+5 for x in range(loop)]
    k_list = [x*5 for x in range(loop)]
    for i,k in zip(i_list,k_list):
        new_five = lists[k:i]
        res_html = threading(new_five) # calling the thread
        final_res_html3 = final_res_html3 + res_html
        sleep(0.5)
    if loop*5<len(lists):
        last_five = lists[i_list[-1]:]
        res_html = threading(last_five) # calling the thread
        final_res_html3 = final_res_html3 + res_html
        sleep(0.5)


    listan = []
    for r in final_res_html3:
        soup = bs(r.content,'html.parser')
        
        try:
            brand_name = soup.find('h1',attrs={'class':'product-name'}).find('span',attrs={'class':'brand-name'}).text.strip()
        except:
            brand_name = '-'
        try:
            product_name = soup.find('h1',attrs={'class':'product-name'}).text.strip().replace('\n',' ')
        except:
            product_name ='-'
        try:
            description = soup.find('div',attrs= {'class':'short-description std'}).text.strip()
        except:
            description = '-'
        try:
            try:
                sku_n = str(soup).find('"sku":"')
                sku = str(soup)[sku_n+7:sku_n+20].split('"')[0]
            except:
                sku = soup.find('span',attrs = {'id':'product-shop-sku'}).text
        except:
            sku = '-'
        try:
            price = soup.find('span',attrs = {'class':'regular-price'}).text.strip().replace('\n','')
        except:
            price = '-'
        if price == '-':
            try:
                price = '$' + str(soup.find('p',attrs = {'class':'special-price'}).find('span',attrs={'class':'price'}).text.strip())
            except:
                price = '-'
        try:
            image = soup.find('img',attrs = {'itemprop':'image'})['src']
        except:
            image = '-'
        try:
            ingred = ''
            ingreds = soup.find('div',attrs={'class':'std instructions'}).findAll('div')
            for ing in ingreds:
                try:
                    ingred = ingred + ing.text.strip() + '\n\n'
                except:
                    pass
        except:
            ingred = '-'
        try:
            prod_link = str(soup.find('a',attrs = {'class':'show-product-review-form'})['href']).split('#')[0]
        except:
            prod_link = '-'
        datan = {
            'Main Category': mother_cate_name,
            'Sub Category': child_cate1_name,
            'Child Category': child_cate2_name,
            'Product Link': prod_link,
            'Brand Name': brand_name,
            'Product Name': product_name,
            'Price': price,
            'SKU': sku,
            'Image': image,
            'Description': description,
            'Directions and Ingredients': ingred

        }
        listan.append(datan)
        prod_link = '-'
        brand_name = '-'
        product_name = '-'
        price = '-'
        sku = '-'
        image = '-'
        description = '-'
        ingred  = '-'
    return listan






def category_scraper(url1):
    url = p_url + str(url1)
    r = requests.get(url)
    soup = bs(r.content,'html.parser')
    category_name = soup.find('h1').text.strip()
    print(f'Scraping: {category_name}')
    boxes = soup.find('ul',attrs = {'id':'vertnav'}).findAll('li')
    category_box = [x for x in boxes if x.find('span').text==category_name]
    
    #----getting mother and child category 1, names and links-------------------------
    mother_cate_name = category_box[0].find('span').text
    child_cate1_urls = [x.find('span').find('a')['href'] for x in category_box[0].find('ul').findAll('li')]
    child_cate1_names = [x.find('span').find('a').text for x in category_box[0].find('ul').findAll('li')]

    final_list = []
    #-----from child category 1, getting child category 2 links-----------------------
    for child_cate1_url,child_cate1_name in zip(child_cate1_urls,child_cate1_names):      # range!!
        url = p_url + str(child_cate1_url)
        r = requests.get(url)
        soup = bs(r.content,'html.parser')
        print(f'Scraping: {mother_cate_name} > {child_cate1_name}')
        
        #----finding category 2 urls, to scrape from----------------------------------
        for x in soup.find('ul',attrs = {'id':'vertnav'}).findAll('li'):
            try:
                child_cate1 = x.find('ul').findAll('li')
                for child1 in child_cate1:
                    try:
                        child_cate2_urls = [p_url+str(x.find('span').find('a')['href']) for x in child1.find('ul').findAll('li')]
                        child_cate2_names = [x.find('span').find('a').text for x in child1.find('ul').findAll('li')]
                    except:
                        pass
            except:
                pass
        #------From each child 2 url, finding all product pagination links------------------------------
        lists = child_cate2_urls
        final_res_html = []
        #--------------sending requests five each time through threading-----------------------
        loop = int(len(lists)/5)
        if loop==0:
            loop = 1
        i_list = [x*5+5 for x in range(loop)]
        k_list = [x*5 for x in range(loop)]
        for i,k in zip(i_list,k_list):
            new_five = lists[k:i]
            res_html = threading(new_five) # calling the thread
            final_res_html = final_res_html + res_html
            sleep(0.5)
        if loop*5<len(lists):
            last_five = lists[i_list[-1]:]
            res_html = threading(last_five) # calling the thread
            final_res_html = final_res_html + res_html
            # sleep(0.5)


        
        for r in final_res_html:                                                                 # range!!
            # we are at a specific child_2_category like: Makeup > Eyes > Eyeshadow
            soup = bs(r.content,'html.parser')
            child_cate2_name = soup.find('h1').text.strip()
            print(f'Scraping: {mother_cate_name} > {child_cate1_name} > {child_cate2_name}')
            try:
                number_of_pages = int(soup.find('li',attrs = {'class':'page-status'}).text.split('of')[1].strip())
            except:
                number_of_pages = 1
            child_cate2_url = str(soup.find('dl',attrs = {'id':'narrow-by-list'}).find('dd').find('ol').find('li').find('span')['data-href']).split('?')[0]
            child2_page_links = [p_url+f'{child_cate2_url}/p/{x}' for x in range(1,number_of_pages+1)]
            print(f'Number of pages of products: {len(child2_page_links)}')


            #--------From product pagination links, finding product links-------------------------
            lists = child2_page_links
            #--------------sending requests five each time through threading-----------------------
            final_res_html2 = []
            loop = int(len(lists)/5)
            if loop==0:
                loop = 1
            i_list = [x*5+5 for x in range(loop)]
            k_list = [x*5 for x in range(loop)]
            for i,k in zip(i_list,k_list):
                new_five = lists[k:i]
                res_html = threading(new_five) # calling the thread for five links(as we have 5 concurrent requests)
                final_res_html2 = final_res_html2 + res_html
                sleep(0.5)
            if loop*5<len(lists):
                last_five = lists[i_list[-1]:]
                res_html = threading(last_five) # calling the thread
                final_res_html2 = final_res_html2 + res_html
                # sleep(0.5)


            product_links_child_cate2 = []

            for r in final_res_html2:
                soup = bs(r.content,'html.parser')
                for x in soup.findAll('div',attrs={'class':'product-name brand-name'}):
                    product_link= p_url+str(x.find('a')['href'])
                    product_links_child_cate2.append(product_link)
            print(f'Total Number of products in this child category: {len(product_links_child_cate2)}')
            # --scraping all the product of a category 2------and saving them to a list of dictionary--------------------
            print(f'Scraping all products from {child_cate2_name}')
            scraped_dict_list = product_scraper(mother_cate_name,child_cate1_name,child_cate2_name,product_links_child_cate2)          # range!!


            mini_final = []
            print('This child category is scraped! Moving to the next one...')
            for dictt in scraped_dict_list:
                final_list.append(dictt)
                mini_final.append(dictt)

            df = pd.DataFrame(final_list)
            df.to_csv(f'priceline_category_{child_cate2_name}.csv',encoding='utf-8-sig',index = False)
            
            sleep(0.5)
            embed = DiscordEmbed(title=f'{child_cate2_name}', description=f'''Mini file from one child category''')
            with open(f'priceline_category_{child_cate2_name}.csv', "rb") as f:
                webhook.add_file(file=f.read(), filename=f'priceline_category_{child_cate2_name}.csv')
            webhook.add_embed(embed)
            response = webhook.execute()
            webhook.remove_embeds()
            webhook.remove_files()



    df = pd.DataFrame(final_list)
    df.to_csv(f'priceline_category_{mother_cate_name}.csv',encoding='utf-8-sig',index = False)
    print('Finished, Finally!')

    sleep(0.5)
    embed = DiscordEmbed(title=f'{mother_cate_name}', description=f'''Scraped File..''')
    with open(f'priceline_category_{mother_cate_name}.csv', "rb") as f:
        webhook.add_file(file=f.read(), filename=f'priceline_category_{mother_cate_name}.csv')
    webhook.add_embed(embed)
    response = webhook.execute()
    webhook.remove_embeds()
    webhook.remove_files()
            

        
            
    
    
    
# makeup   
category_scraper(cate1_urls[0])
# Hair
# category_scraper(cate1_urls[1])
# category_scraper(cate1_urls[2])



