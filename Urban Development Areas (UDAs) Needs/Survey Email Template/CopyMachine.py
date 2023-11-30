class CM_EMail:
    def __init__(self, to=[], cc=[], subject='', message='', email_title=''):
        self.to = to if isinstance(to, list) else [to]
        self.cc = cc if isinstance(cc, list) else [cc]
        self.subject = subject
        self.message = message
        self.email_title = email_title
    
    def get_html(self):
        to = ''
        for address in self.to:
            to += f'{address};'
        to = to[:-1]  # Remove trailing semicolon

        cc = ''
        for address in self.cc:
            cc += f'{address};'
        cc = cc[:-1]

        return f"""<div class="section"><div class="card"><div class="card-header vtrans-blue"><div class="card-header-title has-text-white"><p>{self.email_title}</p></div><div class="card-header-icon"><button class="delete" onclick='this.parentElement.parentElement.parentElement.parentElement.style.display="none"'></button></div></div><div class="card-content"><div class="columns"><div class="column is-one-fifth"><button class="btnCopy button is-primary is-outlined is-fullwidth" data-clipboard-text="{to}">To:</button></div><div class="column">{to}</div></div><div class="columns"><div class="column is-one-fifth"><button class="btnCopy button is-primary is-outlined is-fullwidth" data-clipboard-text="{cc}">Cc:</button></div><div class="column">{cc}</div></div><div class="columns"><div class="column is-one-fifth"><button class="btnCopy button is-primary is-outlined is-fullwidth" data-clipboard-text="{self.subject}">Subject:</button></div><div class="column">{self.subject}</div></div><div class="columns"><div class="column is-one-fifth"><button class="btnCopy button is-primary is-outlined is-fullwidth" data-clipboard-text="{self.message}">Message:</button></div><div class="column" style="white-space: pre-line;">{self.message}</div></div></div></div></div>"""

    def __repr__(self):
        return f'<CM_EMail to: {self.to} - cc: {self.cc} - subject: {self.subject}>'
    

class CM_Page:
    def __init__(self, page_title=''):
        self.html_template = '<!DOCTYPE html><html class="has-background-light"><head><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><title></title><meta name="description" content=""><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto"><style>body{font-family:Roboto,serif}.vtrans-blue{background-color:#01467a}div.icon-text{display:inline-flex}</style><script src="https://unpkg.com/clipboard@2/dist/clipboard.min.js"></script></head><body><div class="hero"><div class="hero-body vtrans-blue"><h1 class="title has-text-white">{page_title}</h1></div></div><div class="container">{content}</div><footer class="footer vtrans-blue"><div class="content has-text-white has-text-centered"><div class="icon-text"><span>All Done!</span><span class="icon"><ion-icon name="happy-outline" size="large"></ion-icon></span></div></div></footer><script>new ClipboardJS(".btnCopy")</script><script type="module" src="https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.esm.js"></script><script nomodule src="https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.js"></script></body></html>'.replace('{page_title}', page_title)
        self._contents = []

    def add(self, item):
        self._contents.append(item)
    
    def get_html(self):
        content_to_add = ''
        for item in self._contents:
            content_to_add += item.get_html()

        return self.html_template.replace('{content}', content_to_add)


if __name__ == '__main__':
    email = CM_EMail('daniel.fourquet@gmail.com', ['kari.anne.evans@gmail.com', 'nadia.rose.fourquet@gmail.com'])
    page = CM_Page()
    page.add(email)
    print(page.get_html())