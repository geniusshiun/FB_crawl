import requests as rq
from bs4 import BeautifulSoup
import time
import re
import sys
import json
def main():
    headers = {
        'cookie': '不告訴你...',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    }
    rooturl = 'https://mbasic.facebook.com/'
    
    nexturl = ''
    postInfo = []
    allPage = True
    
    while allPage:
        url = 'https://mbasic.facebook.com/kobeengineer/?rc=p&__tn__=R'
        #url = 'https://mbasic.facebook.com/search/?q=%E9%9D%A0%E5%8C%97%E5%B7%A5%E7%A8%8B%E5%B8%AB&searchtype=top&_rdr'
        print(url)
        res = rq.get(url,headers = headers)
        soup = BeautifulSoup(res.text, "lxml")
        #sys.exit()
        for item in soup.find_all("div", {"role": "article"}):
            # item.contents[0] #picture
            # item.contents[1] #date and msgUrl
            #item.contents[1].contents[1].contents[2].text
            msgnumber = int(re.findall(r'[\d,]+',item.contents[1].contents[1].contents[2].text)[0].replace(',',''))
            print(msgnumber)
            if msgnumber > 100:
                continue
            peopleSay = {}
            moodurl = rooturl+item.contents[1].contents[1].contents[0].contents[0].get('href')
            moodInfo = {}
            moodInfo['url'] = moodurl
            moodInfo['msgNumber'] = msgnumber
            nextExist = True
            while nextExist:
                print(moodurl)
                res = rq.get(moodurl,headers = headers)
                moodSoup = BeautifulSoup(res.text, "lxml")
                try:
                    for eachmsg in moodSoup.find('div', id=re.compile('^see_next_')).parent.contents:
                        if not '查看更多留言' in eachmsg.text and not '顯示先前的留言' in eachmsg.text:
                            # use name as a key, but the same name? look at profile
                            name = eachmsg.contents[0].contents[0].text
                            if not name in peopleSay:
                                peopleSay[name] = [eachmsg.contents[0].contents[1].text]
                            else:
                                peopleSay[name].append(eachmsg.contents[0].contents[1].text)
                            #peopleSay[eachmsg.contents[0].contents[0].text] = 
                
                    nexturl = rooturl+moodSoup.find('div', id=re.compile('^see_next_')).next.get('href')[1:]
                    if nexturl == rooturl:
                        nextExist = False
                    else:
                        moodurl = nexturl
                    print(len(peopleSay))
                    time.sleep(3)
                except:
                    print('嚶嚶嚶')
                    nextExist = False
                    time.sleep(5)
            moodInfo['peopleSay'] = peopleSay
            postInfo.append(moodInfo)
            
        for item in soup.find_all("div", {"class": "i"}):
            try:
                if '顯示更多' in item.text:
                    url = rooturl+item.contents[0].get('href')
            except:
                print('ohohoh')
                allPage = False
        if len(postInfo) > 2:
            allPage = False
    with open('crawlDataJson.txt','w',encoding='utf8') as f:
        json.dump(postInfo,f,ensure_ascii=False)
    with open('crawlDataJsonNewLine.txt','w',encoding='utf8') as f:
        for item in postInfo:
            f.write('url, '+ item['url']+'\n'+ 'msgNumber, '+str(item['msgNumber'])+'\n')
            for name,msg in item['peopleSay'].items():
                f.write(name+':'+str(msg)+'\n')
            
        #json.dump(postInfo,f,ensure_ascii=False)
if __name__ == '__main__':
    main()