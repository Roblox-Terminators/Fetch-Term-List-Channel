import sys, requests, re, time

baked_headers = {
    "Authorization": "",
    "Sec-Ch-Ua": '"Not(A:Brand";v="24", "Chromium";v="122"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Linux",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "x-debug-options": "bugReporterEnabled",
    "x-discord-locale": "de",
    "x-discord-timezone": "Europe/Berlin"
}

fetched_urls = []

def do_request_without_form(url):
    return requests.request(method="GET", url=url, headers=baked_headers)

def process_single_result(data):
    content = data["content"]
    pattern =  r'(?:http://)?\w+\.\S*[^.\s]'

    for x in re.findall(pattern, content):
        fetched_urls.append("https://" + x + "\n")

def process_large_result(data):
    for x in data:
        process_single_result(x)

def get_last_message_id(data):
    return data[len(data)-1]["id"]

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("./%s [token] [optional: depth]" % sys.argv[0])
        exit(-1)

    token = sys.argv[1]
    
    depth = 20

    if len(sys.argv) >= 3:
        depth = int(sys.argv[2])
    
    baked_headers['Authorization'] = token

    print("[-] Depth: %i" % depth)

    first_message_fetch = do_request_without_form("https://discord.com/api/v9/channels/1216087918725300397/messages?limit=50")

    if not first_message_fetch.status_code == 200:
        print("Received error: %s" % first_message_fetch.text)
        exit()
    
    process_large_result(first_message_fetch.json())

    last_fetch_result = first_message_fetch

    for _ in range(0, depth):
        last_fetch_result = do_request_without_form("https://discord.com/api/v9/channels/1216087918725300397/messages?before=%s&limit=50" % get_last_message_id(last_fetch_result.json()))
        if not last_fetch_result.status_code == 200:
            print("Received error (2): %s" % last_fetch_result.text)
            exit()
        
        print(last_fetch_result.text)
        process_large_result(last_fetch_result.json())

        time.sleep(2)
        print("[ ] Next...")
    
    open("output.json", "w+").writelines(fetched_urls)
    
