import pandas as pd
import pickle
from CopyMachine import CM_Page, CM_EMail

UDA_Contacts_XLSX = 'UDA_Contacts (2).xlsx'
req_cols = [
    'District',
    'UDA_NM',
    'Jurisdiction',
    'prime_contact_name_2019',
    'prime_contact_email_2019',
    'sec_contact_name_2019',
    'sec_contact_email_2019'
    ]

df_contact_list = pd.read_excel(UDA_Contacts_XLSX, usecols=req_cols)
with open('urls.pkl', 'rb') as file:
    urls = pickle.load(file)


class UDA_Contact:
    def __init__(self, contact):
        self.primary_contact = contact
        self.primary_contact_email = self.get_primary_contact_email()
        self.secondary_contacts = self.get_secondary_contacts(contact)
        self.secondary_contact_emails = self.get_secondary_contact_emails()
        self.UDAs = self.get_UDAs(contact)
        self.jurisdiction = self.get_jurisdiction()
        self.district = self.get_district()

    def get_primary_contact_email(self):
        return df_contact_list.loc[df_contact_list['prime_contact_name_2019'] == self.primary_contact, 'prime_contact_email_2019'].unique()[0]

    def get_secondary_contacts(self, contact):
        return df_contact_list.loc[df_contact_list['prime_contact_name_2019'] == self.primary_contact]['sec_contact_name_2019'].unique().tolist()

    def get_secondary_contact_emails(self):
        secondary_emails = []
        for secondary_contact in self.secondary_contacts:
            email = df_contact_list.loc[df_contact_list['sec_contact_name_2019'] == secondary_contact]['sec_contact_email_2019'].unique()
            if len(email) > 0:
                secondary_emails.append(email[0])
            else:
                secondary_emails.append('')
        return secondary_emails

    def get_district(self):
        return df_contact_list.loc[df_contact_list['prime_contact_name_2019'] == self.primary_contact, 'District'].unique()[0]

    def get_UDAs(self, contact):
        return df_contact_list.loc[df_contact_list['prime_contact_name_2019'] == self.primary_contact]['UDA_NM'].unique().tolist()
    
    def get_jurisdiction(self):
        return df_contact_list.loc[df_contact_list['prime_contact_name_2019'] == self.primary_contact, 'Jurisdiction'].unique()[0]

    def __repr__(self):
        return f'<UDA_Contact {self.primary_contact} - {self.secondary_contacts}: {self.UDAs}>'


UDA_Contacts = []

for name in df_contact_list['prime_contact_name_2019'].unique().tolist():
    UDA_Contacts.append(UDA_Contact(name))

page = CM_Page()
for contact in UDA_Contacts:
    email = CM_EMail()
    email.to = [contact.primary_contact_email]
    email.cc = contact.secondary_contact_emails
    email.subject = f'{contact.jurisdiction} UDA Data Update'
    email.email_title = f'{contact.jurisdiction} - {contact.primary_contact} ({contact.district} District)'

    txt_uda_list = ''
    for uda in contact.UDAs:
        txt_uda_list += f'    - {uda},\n'
    txt_uda_list = txt_uda_list[:-2]  # Remove trailing comma

    survey_url = None
    map_url = urls.get(contact.jurisdiction)

    email.message = f"""Hello {contact.primary_contact.split(' ')[0]},

My name is Dan Fourquet from the Office of Intermodal Planning and Investment (OIPI).  We are in the process of updating the UDA data that we have on file and I am writing to request that you fill out the UDA survey found at the link below.  

It is important that we have the latest data on your UDAs as this is used to determine UDA VTrans needs, which will have implications on the eligibility in various funding programs for projects in your UDAs.  We have you listed as the primary contact for the following {'UDAs' if len(contact.UDAs) > 1 else 'UDA'}:

{txt_uda_list}

You can find the UDA survey here: {survey_url}

The survey will ask you to verify that the geometry that we have on file is accurate.  Please use the map in InteractVTrans to verify your UDA geometry here: {map_url}

Thank you for your attention to this matter,
 in your UDAs.  We have you listed as the primary contact for the following UDA:

Norton Rd - Cherry St.
"""
   
    page.add(email)
    

with open('copy_machine.html','w') as file:
    file.write(page.get_html())