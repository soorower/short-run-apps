from calendar import c
from discord_webhook import DiscordWebhook, DiscordEmbed
webhook = DiscordWebhook(
    url='https://discord.com/api/webhooks/956803950378623036/OSYz7_37q-7dlqXwY8_oIovhlipIRzgFpZPY8t_0xCR7zLNAWHVlTPbE0IlzCrjLq07s', username="Exchange Scraped File")
from bs4 import BeautifulSoup as bs
import pandas as pd   
import requests
import datetime

headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
}
#----------Input and getting the data-------------------------------------------------------------
print('Date input type: (Month/Date/Year) Ex. 07/23/2021')
# start_d = input('Enter First Date Range: ')
# end_d = input('Enter Second Date Range: ')
excel_name = 'dot_sent_fiverr'

start_d = '11/01/2021'
end_d = '03/23/2022'
start = datetime.datetime.strptime(start_d, "%m/%d/%Y")
end = datetime.datetime.strptime(end_d, "%m/%d/%Y")
date_generated = pd.date_range(start, end)
date_list = date_generated.strftime("%m/%d/%Y")


dot_list = pd.read_excel(f'{excel_name}.xlsx')['DOT No'].tolist()
    
#---------------Scraping the data-----------------------------------------------------------------------------
datas = {}
lists = []
count = 1
for dot in dot_list:
    url = f'https://ai.fmcsa.dot.gov/SMS/Carrier/{dot}/CompleteProfile.aspx'
    print(count)
    print(f'Scraping dot: {dot}')
    print(url)
    count = count + 1
    try:
        r = requests.get(url,headers = headers)
        soup = bs(r.content,'html.parser')
        if 'Complete SMS Profile' in soup.find('title').text:
            inspection_tab = soup.find('table',attrs = {'id':'inspectionTable'}).find('tbody',attrs = {'class':'dataBody'}).findAll('tr')

            inspec_date = []
            weight_list = []


            #---finding weight => 10 -----------------------------------------------------------------
            count = 0
            for row in inspection_tab:
                try:
                    inspec = row.find('td').text.strip()
                    weight = row.findAll('td')[6].text.strip()
                    if weight == '':
                        pass
                    elif int(weight) >= 10:
                        inspec_date.append(inspec)
                        weight_list.append(weight)

                except:
                    try:
                        weight = row.findAll('td')[-2].text.strip()
                        if weight == '':
                            pass
                        elif int(weight) >= 10:
                            inspec = inspection_tab[count-1].find('td').text.strip()
                            weight_list.append(weight)
                            inspec_date.append(inspec)
                    except:
                        pass
                count = count + 1


            #------finding rest of the weight----------------------------------------------------------------------------------
            count = 0
            for row in inspection_tab:
                clas = str(row['class']).strip()
                if 'viol' in clas:
                    if count+1 == len(inspection_tab):
                        weight = row.findAll('td')[-2].text.strip().replace('\r\n ','').replace(' (OOS)','').replace(' ','')
                        inspec = inspection_tab[count-1].find('td').text.strip()
                        if '10' in weight:
                            pass
                        else:
                            weight_list.append(weight)
                            inspec_date.append(inspec) 
                    else:
                        up_clas = str(inspection_tab[count-1]['class']).strip()
                        try:
                            down_clas = str(inspection_tab[count+1]['class']).strip()
                        except:
                            down_clas = '-'
                        if 'viol' in up_clas:
                            pass
                        elif 'viol' in down_clas:
                            weight = row.findAll('td')[-2].text.strip().replace('\r\n ','').replace(' (OOS)','').replace(' ','')
                            inspec = inspection_tab[count-1].find('td').text.strip()
                            wei = inspection_tab[count+1].findAll('td')[-2].text.strip().replace('\r\n ','').replace(' (OOS)','').replace(' ','')
                            weight = weight + '+' + wei

                            try:
                                if not 'viol' in str(inspection_tab[count+2]['class']).strip():
                                    pass
                                else:
                                    wei = inspection_tab[count+2].findAll('td')[-2].text.strip().replace('\r\n ','').replace(' (OOS)','').replace(' ','')
                                    weight = weight + '+' + wei
                                    if not 'viol' in str(inspection_tab[count+3]['class']).strip():
                                        pass
                                    else:
                                        wei = inspection_tab[count+3].findAll('td')[-2].text.strip().replace('\r\n ','').replace(' (OOS)','').replace(' ','')
                                        weight = weight + '+' + wei
                                        if not 'viol' in str(inspection_tab[count+4]['class']).strip():
                                            pass
                                        else:
                                            wei = inspection_tab[count+4].findAll('td')[-2].text.strip().replace('\r\n ','').replace(' (OOS)','').replace(' ','')
                                            weight = weight + '+' + wei
                            except:
                                pass

                            if '10' in weight:
                                pass
                            else:
                                weight_list.append(weight)
                                inspec_date.append(inspec)    
                        else:
                            try:
                                weight = row.findAll('td')[-2].text.strip().replace('\r\n ','').replace(' (OOS)','').replace(' ','')
                                inspec = inspection_tab[count-1].find('td').text.strip()
                                if '10' in weight:
                                    pass
                                else:
                                    weight_list.append(weight)
                                    inspec_date.append(inspec)  
                            except:
                                pass
                count = count + 1

            new_inspec_date = []
            new_weight_list = []
            for ins,we in zip(inspec_date,weight_list):
                check = ins.split('/')
                one = check[0]
                if len(one) == 1:
                    one = '0' +  one
                two = check[1]
                if len(two) == 1:
                    two = '0' +  two
                ins = one + '/' +  two + '/' + check[2]
                if ins in date_list:
                    new_inspec_date.append(ins)
                    new_weight_list.append(we)


            url2 = f'https://ai.fmcsa.dot.gov/SMS/Carrier/{dot}/CarrierRegistration.aspx'
            r = requests.get(url2,headers = headers)
            soup = bs(r.content,'html.parser')
            rows = soup.find('div',attrs = {'id':'regBox'}).find('ul').findAll('li')
            company_name = rows[0].find('span').text.strip()
            try:
                address1 = str(rows[3].find('span')).split('"dat">')[1].strip().split('<br/>')[0]
                address2 = str(rows[3].find('span')).split('<br/>')[1].replace('</span>','').replace(' ','').strip()
                address = address1 + '\n' + address2 
            except:
                address = rows[3].find('span').text.strip()
            phone = rows[4].find('span').text.strip()
            email = rows[6].find('span').text.strip()
            print(phone)
            print(email)
         
            if len(new_inspec_date)>0:
                for insp,weig in zip(new_inspec_date,new_weight_list):
                    datas= {
                        'Dot No.': dot,
                        'URL': url,
                        'Inspection Date': insp,
                        'Severity Weight': weig,
                        'Company Name': company_name,
                        'Phone': phone,
                        'Email': email,
                        'Address': address
                    }
                    lists.append(datas)
    except:
        pass
df = pd.DataFrame(lists)
df.to_excel('ai_fmcsa_dot_output.xlsx',encoding = 'utf-8-sig',index = False)



embed = DiscordEmbed(title='dot lists', description=f'''Scraping Done!''')
with open(f'ai_fmcsa_dot_output.xlsx', "rb") as f:
    webhook.add_file(file=f.read(), filename=f'ai_fmcsa_dot_output.xlsx')
webhook.add_embed(embed)
response = webhook.execute()
webhook.remove_embeds()
webhook.remove_files()