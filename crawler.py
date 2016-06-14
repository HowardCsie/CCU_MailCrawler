from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urlparse import urlsplit
from collections import deque
import re
import Queue, time, threading, datetime ,sys 

if not len(sys.argv) == 3:
	print("please input parameter")
	sys.exit()
new_urls = deque([sys.argv[1]])
processed_urls = set()
emails = set()

class Job:    
     def __init__(self, name):    
             self.name = name    
     def do(self):
		if len(new_urls) > 0:
			url = new_urls.popleft()
			processed_urls.add(url)
			parts = urlsplit(url)
			base_url = "{0.scheme}://{0.netloc}".format(parts)
			path = url[:url.rfind('/')+1] if '/' in parts.path else url
			print("Job({})\t:{}".format(self.name,url.encode('utf-8'))) 
			try:
			    response = requests.get(url, timeout=3)
			except (requests.ReadTimeout,requests.ConnectTimeout,requests.Timeout,requests.RequestException,requests.ConnectionError,requests.HTTPError, requests.URLRequired,requests.TooManyRedirects,):
				pass
			try:
				new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
				for email in new_emails:
					print(email)
				emails.update(new_emails)
				soup = BeautifulSoup(response.text, "lxml")
				for anchor in soup.find_all('a'):
				    link = anchor.attrs["href"] if "href" in anchor.attrs else ''
				    if link.startswith('/'):
				        link = base_url + link
				    elif not link.startswith('http'):
				        link = path + link
				    if not link.endswith('pdf') and not link.endswith('doc') and not link.endswith('docx') and not link.endswith('jpg') and not link.endswith('zip') and not link.endswith('ppt') and not link.endswith('pptx') and not link.endswith('xlsb'):
					    if not link in new_urls and not link in processed_urls:
					        new_urls.append(link)
			except:
				pass

que = Queue.Queue()  
for i in range(int(sys.argv[2])):  
        que.put(Job(str(i+1)))
print("\t[Info] Queue size={0}...".format(que.qsize()))

def doJob(*args):
    queue = args[0]  
    while queue.qsize() > 0:  
        job = queue.get()  
        job.do()

thd1 = threading.Thread(target=doJob, name='Thd1', args=(que,))  
thd2 = threading.Thread(target=doJob, name='Thd2', args=(que,))  
thd3 = threading.Thread(target=doJob, name='Thd3', args=(que,))
thd4 = threading.Thread(target=doJob, name='Thd4', args=(que,))

st = datetime.datetime.now()  
thd1.start()
time.sleep(5)    
thd2.start()  
thd3.start()
thd4.start()

flag1 = 1
flag2 = 1
flag3 = 1
flag4 = 1

while thd1.is_alive() or thd2.is_alive() or thd3.is_alive() or thd4.is_alive():
     if not thd1.is_alive() and flag1 == 1:
     	print("td1 dead")
     	flag1 = 2
     if not thd2.is_alive() and flag2 == 1:
     	print("td2 dead")
     	flag2 = 2
     if not thd3.is_alive() and flag3 == 1:
     	print("td3 dead")
     	flag3 = 2
     if not thd4.is_alive() and flag4 == 1:
     	print("td4 dead")
     	flag4 = 2
     time.sleep(1)    
  
td = datetime.datetime.now() - st  
print("\t[Info] Spending time={0}!".format(td))
file = open("email.txt", "w")
num = len(emails)
file.write("num:")
file.write("{}".format(num))
file.write("\n")
file.write("time:")
file.write("{}".format(td))
file.write("\n")
for email in emails:
	file.write(email)
	file.write("\n")
file.close()
