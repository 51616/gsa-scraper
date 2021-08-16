from __future__ import print_function
import os.path
import base64
from collections import Counter

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from bs4 import BeautifulSoup
from tqdm import tqdm

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def create_md(paper_list, counter):
    with open('output.md','w') as f:
        f.write('# Google Scholar Alerts\n')
        for i, p in enumerate(paper_list):
            f.write(f'#### {i}. [{p["title"]}]({p["link"]}) ({counter[p["title"]]})\n')
            f.write(f'*Authors: {p["authors"]}* <br>\n')
            f.write(f'{p["snippet"]}\n')
            f.write('\n')

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    l = service.users().messages().list(userId='me',
                                        q='from:scholaralerts-noreply@google.com',
                                        labelIds=['INBOX'],
                                        maxResults=500).execute().get('messages',[])
    counter = Counter()
    out = []
    for m in tqdm(l):
        msg = service.users().messages().get(userId='me',id=m['id']).execute()
        html = BeautifulSoup(base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8'),features="html.parser")
        paper = html.find_all('h3')
        auth = html.find_all(attrs={'style':'color:#006621'})
        snip = html.find_all(attrs={'class':'gse_alrt_sni'})

        for (p,a,s) in zip(paper,auth,snip):
            counter[p.a.string] += 1
            if counter[p.a.string]>1:
                continue
            d = {'title':p.a.string, 'link':p.a.get("href"), 'authors':a.string,
                'snippet':s.get_text()}
            out.append(d)

    out = sorted(out, key=lambda x:counter[x['title']], reverse=True)
    create_md(out, counter)

if __name__ == '__main__':
    main()