from html.entities import name2codepoint
from html.parser import HTMLParser

class LiveHTMLParser(HTMLParser):
    def locate_votes():
        pass

    def handle_starttag(self, tag, attrs):
        if(tag == "section"):
            if([attr[1]=='grades' for attr in attrs]):
                self.handle_data()

    def handle_endtag(self, tag):
        pass
        # print("Encountered an end tag :", tag)

    def handle_data(self, data):
        
        # return data
        print("Encountered some data  :", data)

    def handle_comment(self, data):
        pass
        # print("Comment  :", data)

    def handle_entityref(self, name):
        pass
        # c = chr(name2codepoint[name])
        # print("Named ent:", c)

    def handle_charref(self, name):
        pass
        # if name.startswith('x'):
        #     c = chr(int(name[1:], 16))
        # else:
        #     c = chr(int(name))
        # print("Num ent  :", c)

    def handle_decl(self, data):
        pass
        # print("Decl     :", data)