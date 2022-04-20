import requests
from bs4 import BeautifulSoup as bs
import json
import os 
from time import sleep
import sys

headers = {
'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
}
from discord_webhook import DiscordWebhook, DiscordEmbed
webhook = DiscordWebhook(
    url='https://discord.com/api/webhooks/966010327126933524/Ebs_zHX_QHNWkxRRGGJmTrVhUFI2D4vP8qulIc9KZuBUOIKih0DXZXaZChwzsSQlbFu3', username="EuroBasket Scraped File")



#------------Finding all the country name and links in Europe----------------------------------------
url = 'https://www.eurobasket.com/'
r = requests.get(url,headers = headers)
soup = bs(r.content,'html.parser')
#-----------Change Continent and list range-------------------------------------

europe_co_list = soup.findAll('div',attrs = {'class':'col-sm-4 mobile4'})[:3] # done
l_america_co_list = soup.findAll('div',attrs = {'class':'col-sm-4 mobile4'})[3:6]
asia_co_list = soup.findAll('div',attrs = {'class':'col-sm-4 mobile4'})[6:9]
africa_co_list = soup.findAll('div',attrs = {'class':'col-sm-4 mobile4'})[9:]

eu_events_ev_list = soup.findAll('div',attrs = {'class':'col-sm-6 mobile6'})[:4]   #event name instead of country name
n_america_ev_list = soup.findAll('div',attrs = {'class':'col-sm-6 mobile6'})[4:12]  #event name instead of country name
oceania_co_list = soup.findAll('div',attrs = {'class':'col-sm-6 mobile6'})[12:14] 



#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------

def scraping_part(links,team_name_list,continent,co_name,GENDER):
    final_lists1 = []

    for team_link,team_name in zip(links,team_name_list):
        r = requests.get(team_link,headers =headers)
        soup = bs(r.content,'html.parser')
        try:
            league_name = soup.find('td',attrs = {'class':'padding-left-10 social'}).find('div').find('span').text.split('-',1)[1].replace(')','').strip()
        except:
            league_name = co_name
        try:
            team_logo = soup.find('img',attrs = {'class':'team-logo'})['src']
        except:
            team_logo = '-'


        # print(f'Scraping team: {team_name}    Link: {team_link}')

#-----Address and T-shirt Color-----------------------------------------------------------------
        address_is = []
        t_color_is = []
        try:
            address_list = soup.findAll('table',attrs = {'class':'team-authorstable'})
            for add in address_list:
                if 'Address' in add.find('tr').text:
                    address = add.findAll('tr')[1].find('p').text
                    address_is.append(address)
            for add in address_list:
                if 'Team Colors' in add.find('tr').text:
                    t_color = add.findAll('tr')[1].text.replace('\n',',')
                    if ',' == t_color[-1]:
                        t_color = t_color[:-1]
                    t_color_is.append(t_color)
        except:
            address = '-'
            address_is.append(address)
            t_color = '-'
            t_color_is.append(t_color)
        if len(address_is)==0:
            address = '-'
        else:
            address = address_is[0]
        if len(t_color_is)==0:
            t_color = '-'
        else:
            t_color = t_color_is[0]

#-------------------------------------------------------------------------------------------------------
        try:
            coach = soup.find('tr',attrs = {'id':'trno1'}).text.replace('\n',' ').replace('\u00a0',' ')
        except:
            coach = '-'

        try:
            social_links_tab = soup.find('td',attrs = {'class':'padding-left-10 social'}).find('div').findAll('a')
            for social_links in social_links_tab:
                if 'facebook' in str(social_links['href']):
                    facebook = str(social_links['href']).split('url=')[1]
                if 'twitter' in str(social_links['href']):
                    twitter = str(social_links['href']).split('url=')[1]
                try:
                    if 'website' in str(social_links.find('img')['title']):
                        website = str(social_links['href']).split('url=')[1]
                except:
                    pass
            try:
                facebook = facebook
            except:
                facebook = '-'
            try:
                twitter = twitter
            except:
                twitter = '-'
            try:
                website = website
            except:
                website = '-'
        except:
            facebook = '-'
            twitter = '-'
            website = '-'
        #-------address------------------------------------------------------------
        address = address.replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('–','-')
        website = website.replace('\n',' ').replace('\r',' ').replace('\t',' ')
        twitter = twitter.replace('\n',' ').replace('\r',' ').replace('\t',' ')
        facebook = facebook.replace('\n',' ').replace('\r',' ').replace('\t',' ')
        coach  = coach.replace('\n',' ').replace('\r',' ').replace('\t',' ')
        team_name = team_name.replace('\n',' ').replace('\r',' ').replace('\t',' ')
        if address == '-':
            city = '-'
            phone_n = '-'
            street = '-'
        else:
            address = address.replace('City',' City').replace('\n',' ')
            e = address
            city_n = e.find('City')
            if city_n == -1:
                city = '-'
            else:
                city = e[city_n+5:]

            #-----Phone-------------------------------------
            e = e.replace(f'City:{city}','')
            phon_n = e.find('Telefon')
            if phon_n == -1:
                phone = '-'
            else:
                phone = e[phon_n+9:].strip()

            if phone == '-':
                phon_n = e.find('Tel')
                if phon_n == -1:
                    phone = '-'
                else:
                    phone = e[phon_n+5:].strip()
            if phone == '-':
                phon_n = e.find('Tel.')
                if phon_n == -1:
                    phone = '-'
                else:
                    phone = e[phon_n+5:].strip()
            if phone == '-':
                phon_n = e.find('Phone')
                if phon_n == -1:
                    phone = '-'
                else:
                    phone = e[phon_n+6:].strip()
            if phone == '-':
                phon_n = e.find('Phone&Fax')
                if phon_n == -1:
                    phone = '-'
                else:
                    phone = e[phon_n+10:].strip()
            if phone == '-':
                phon_n = e.find('Télephone')
                if phon_n == -1:
                    phone = '-'
                else:
                    phone = e[phon_n+11:].strip()
            if phone == '-':
                phon_n = e.find('Tél')
                if phon_n == -1:
                    phone = '-'
                else:
                    phone = e[phon_n+5:].strip()
            if phone == '-':
                phon_n = e.find('Tél.')
                if phon_n == -1:
                    phone = '-'
                else:
                    phone = e[phon_n+5:].strip()
            if phone == '-':
                phon_n = e.find('Tel/Fax')
                if phon_n == -1:
                    phone = '-'
                else:
                    phone = e[phon_n+8:].strip()
            if phone == '-':
                phon_n = e.find('T.')
                if phon_n == -1:
                    phone = '-'
                else:
                    phone = e[phon_n+3:].strip()
            if phone == '-':
                phon_n = e.find('T:')
                if phon_n == -1:
                    phone = '-'
                else:
                    phone = e[phon_n+3:].strip()
            if phone == '-':
                phon_n = e.find('Telephone')
                if phon_n == -1:
                    phone = '-'
                else:
                    phone = e[phon_n+11:].strip()
            if phone == '-':
                phon_n = e.find('tel')
                if phon_n == -1:
                    phone = '-'
                else:
                    phone = e[phon_n+5:].strip()
            if phone == '-':
                phon_n = e.find('M:')
                if phon_n == -1:
                    phone = '-'
                else:
                    phone = e[phon_n+3:].strip()


            phone_n = ''  
            for each in phone:
                if each == '+':
                    phone_n = phone_n + each
                elif each == '/':
                    phone_n = phone_n + each
                elif each == '-':
                    phone_n = phone_n + each
                elif each == ' ':
                    phone_n = phone_n + each
                elif each == '(':
                    phone_n = phone_n + each
                elif each == ')':
                    phone_n = phone_n + each
                elif each.isdigit():
                    phone_n = phone_n + each
                else:
                    break
            if phone_n == '':
                phone_n = '-'
    #------------Fax----------------------------------------------------------
            fax_n = e.find('Fax:')
            if fax_n == -1:
                fax = '-'
            else:
                fax = e[fax_n+4:].strip()
            if fax == '-':
                fax_n = e.find('Fax')
                if fax_n == -1:
                    fax = '-'
                else:
                    fax = e[fax_n+3:].strip()
            if fax == '-':
                fax_n = e.find('Fax :')
                if fax_n == -1:
                    fax = '-'
                else:
                    fax = e[fax_n+5:].strip()
            if fax == '-':
                fax_n = e.find('F:')
                if fax_n == -1:
                    fax = '-'
                else:
                    fax = e[fax_n+2:].strip()
            fax_n = ''  
            for each in fax:
                if each == '+':
                    fax_n = fax_n + each
                elif each == '/':
                    fax_n = fax_n + each
                elif each == '-':
                    fax_n = fax_n + each
                elif each == ' ':
                    fax_n = fax_n + each
                elif each == '(':
                    fax_n = fax_n + each
                elif each == ')':
                    fax_n = fax_n + each
                elif each.isdigit():
                    fax_n = fax_n + each
                else:
                    break
            if fax_n == '':
                fax_n = '-'
          
            
            #-----Street-------------------------------------------
            try:
                street = e.replace('Tel:','').replace('Telefon','').replace(phone_n,'').replace(fax_n,'').replace('Tel:','').replace('Tel','').replace('Tel.','').replace('Tel.:','').replace('tel','').replace('M:','').replace('Telephone:','').replace('T:','').replace('T.','').replace('Tel/Fax','').replace('Tél.','').replace('Tél','').replace('Télephone','').replace('Phone','').replace('Phone&Fax','').replace('Phone:','').replace('Fax','').replace('Fax:','').replace('F:','').strip()
                street = street.replace(':',' ')
                street_num = street.find('City')
                street = street[:street_num].strip()
                street =  " ".join(street.split())
            except:
                street = '-'

        city = city.strip()
        coach = coach.strip()
        team_name = team_name.strip()
        #_-------------------------------------------------------------------------------------------------------------------------
        # if 'N.America' or 'EU EVENTS' in continent:
        #     data_each_team = {
        #         "Region": continent,
        #         "League": league_name,
        #         "Event": co_name,
        #         "Team Name": team_name,
        #         "Team Logo": team_logo,
        #         # "URL": team_link,
        #         "Address": street,
        #         "City": city,
        #         "Street": street,
        #         "Phone": phone_n,
        #         "Coach": coach,
        #         "Website": website,
        #         "Facebook": facebook,
        #         "Twitter": twitter,
        #         "Team Colors": t_color
        #         }
        # else:
    
        data_each_team = {
            "Region": continent,
            "League": league_name,
            "Country": co_name,
            "Team Name": team_name,
            "Team Logo": team_logo,
            # "URL": team_link,
            "Address": street,
            "City": city,
            "Street": street,
            "Phone": phone_n,
            "Coach": coach,
            "Website": website,
            "Facebook": facebook,
            "Twitter": twitter,
            "Team Colors": t_color
            }
        final_lists1.append(data_each_team)
        address = '-'
        coach = '-'
        website = '-'
        facebook = '-'
        twitter = '-'
        t_color = '-'

    
    if len(final_lists1)>0:
        try:
            mylist = [dict(t) for t in {tuple(d.items()) for d in final_lists1}]
            with open(f"{co_name}_{league_name}_{GENDER}.json", "w", encoding="utf-8-sig") as final:
                json.dump(mylist, final,ensure_ascii=False, indent=4, separators=(", ", ": "), sort_keys=False)
            sleep(0.1)
            # from google.colab import files
            # files.download(f"{co_name}_{league_name}_{GENDER}.json")
            embed = DiscordEmbed(title=f'{continent}', description=f'''For country: {co_name}''')
            with open(f"{co_name}_{league_name}_{GENDER}.json", "rb") as f:
                webhook.add_file(file=f.read(), filename=f"{co_name}_{league_name}_{GENDER}.json")
            webhook.add_embed(embed)
            response = webhook.execute()
            webhook.remove_embeds()
            webhook.remove_files()
        except:
            pass




#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
def scrape(continent,GENDER,co_list):
    country_names = []
    country_links = []
    for euro in co_list:
        data_list = euro.find('ul').findAll('li')
        for data in data_list:
            try:
                country_names.append(data.text)
                country_links.append(data.find('a')['href'])
            except:
                pass
            
#---------------iterating through each of the country-------------------------------------------------
    for co_name,co_link in zip(country_names,country_links):
        if GENDER == 'male':
            co_link = co_link.replace('.aspx','-Teams.aspx')
        else:
            co_link = co_link.replace('.aspx','-Teams.aspx') + '?women=1'
        print(f'Scraping continent: {continent};; country: {co_name};; link: {co_link} Gender: {GENDER}')
#--------------making new folder---------------------------------------------------------
        # directory = co_name
        # try:
        #     path = os.path.join(parent_dir, directory) 
        #     os.mkdir(path) 
        # except:
        #     pass
#--------Getting list of leagues---------------------------------------------------------------------
        r = requests.get(co_link,headers = headers)
        soup = bs(r.content,'html.parser')
        try:
            list_of_leagues1 = soup.findAll('div',attrs = {'class':'BasketBallTeamMain'})
            list_of_leagues2 = soup.findAll('div',attrs = {'class':'BasketBallTeamMainNoGame'})
        except:
            list_of_leagues1 = []
            list_of_leagues2 = []
        
#-----------from each league finding and scraping teams data------------------------------------------------------------------------
        if len(list_of_leagues1)> 0:
            for league_data in list_of_leagues1:
                team_name_list = []
                links = []
                for team in league_data.find('div',attrs = {'class':'BasketBallTeamDetails'}).findAll('div',attrs = {'class':'BasketBallTeamDetailsLine'}):
                    team_link = team.find('div',attrs = {'class':'BasketBallTeamName'}).find('a')['href']
                    team_name = team.find('div',attrs = {'class':'BasketBallTeamName'}).find('a').text.strip().lower()
                    team_name_list.append(team_name)
                    links.append(team_link)
                scraping_part(links,team_name_list,continent,co_name,GENDER)
                    
        if len(list_of_leagues2)> 0:
            for league_data in list_of_leagues2:
                team_name_list = []
                links = []
                for team in league_data.find('div',attrs = {'class':'BasketBallTeamDetails'}).findAll('div',attrs = {'class':'BasketBallTeamDetailsLine'}):
                    team_link = team.find('div',attrs = {'class':'BasketBallTeamName'}).find('a')['href']
                    team_name = team.find('div',attrs = {'class':'BasketBallTeamName'}).find('a').text.strip().lower()
                    team_name_list.append(team_name)
                    links.append(team_link)
                scraping_part(links,team_name_list,continent,co_name,GENDER)

        links = []
        team_name_list = []
        try:
            try:
                try:
                    table1 = soup.find('table',attrs = {'id':'DDDD'})
                    for team in table1.findAll('tr'):
                        team_li = team.findAll('td')[1].find('a')['href']
                        team_na = team.findAll('td')[1].find('a').text.lower().strip()
                        links.append(team_li)
                        team_name_list.append(team_na)
                except:
                    pass
                try:
                    table2 = soup.find('table',attrs = {'id':'EEEE'})
                    for team in table2.findAll('tr'):
                        team_li = team.findAll('td')[1].find('a')['href']
                        team_na = team.findAll('td')[1].find('a').text.lower().strip()
                        links.append(team_li)
                        team_name_list.append(team_na)
                except:
                    pass
                
                aa = links[0]
            except:
                list_of_tables = soup.findAll('table',attrs = {'id':'BBBB'})
                for table in list_of_tables:
                    for team in table.findAll('tr')[1:]:
                        try:
                            team_li = team.findAll('td')[1].find('a')['href']
                            team_na = team.findAll('td')[1].find('a').text.lower().strip()
                            links.append(team_li)
                            team_name_list.append(team_na)
                        except:
                            pass
        except:
            pass
        if len(links)>0:
            scraping_part(links,team_name_list,continent,co_name,GENDER)
        
        try:
            tables = soup.findAll('table',attrs = {'class':'CollegeTeamTable'})
            for table in tables:
                links = []
                team_name_list = []
                for team in table.findAll('tr'):
                    try:
                        links.append(team.find('td').find('a')['href'])
                        team_name_list.append(team.find('td').find('a').text.strip().lower())
                    except:
                        pass
                if len(links) > 0:
                    scraping_part(links,team_name_list,continent,co_name,GENDER)
        except:
            pass
        print('\n\n\n')







#-------------Uncomment the below lines to scrape the specific continent------
# scrape('Europe','male',europe_co_list)
# scrape('Europe','female',europe_co_list)

# scrape('L.America','male',l_america_co_list)
# scrape('L.America','female',l_america_co_list)

# scrape('Asia','male',asia_co_list)
# scrape('Asia','female',asia_co_list)

# scrape('Oceania','male',oceania_co_list)
# scrape('Oceania','female',oceania_co_list)

# scrape('Africa','male',africa_co_list)
scrape('Africa','female',africa_co_list)


scrape('EU EVENTS','male',eu_events_ev_list)
scrape('EU EVENTS','female',eu_events_ev_list)


scrape('N.America','male',n_america_ev_list)
scrape('N.America','female',n_america_ev_list)


sys.exit()