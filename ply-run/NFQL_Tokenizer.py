__author__ = 'd'
import sys
import ply.lex as lex
from xml.dom import minidom
import re


class Tokenizer:
    def __init__(self):
        Tokenizer.xml_data(self)
        self.tokens += list(self.reserved.values())


    names = []
    regexes=[]
    reserved = {
        'filter': 'filterKeyword',
        'in': 'inKeyword',
        'notin': 'notinKeyword',
        'OR': 'ORKeyword',
        'NOT': 'NOTKeyword',
        'bitOR': 'bitORKeyword',
        'bitAND': 'bitANDKeyword',
    }
    literals = "+-*/(){},."
    entities = {}

    @staticmethod
    def xml_data(self):
        xmldoc = minidom.parse('ipfix.xml')
        node = xmldoc.documentElement
        records = xmldoc.getElementsByTagName('record')
        #print itemlist[0].attributes['name'].value
        for record in records:
            nameObj = record.getElementsByTagName('name')
            dataTypeObj = record.getElementsByTagName('dataType')
            dataType = ""
            for data in dataTypeObj:
                dataType = data.childNodes[0].nodeValue
                break
            for name in nameObj:
                try:
                    nameText = name.childNodes[0].nodeValue
                    if nameText.find(' ') == -1 and str(dataType):
                        #print(nameText)
                        self.reserved[nameText.replace('\n', '')] = str(nameText).replace('\n', '')
                        #self.reserved[nameText.replace('\n', '')] = "id"
                        self.entities[str(nameText.replace('\n', ''))] = dataType.replace('\n', '')
                        self.regexes.append(re.compile(nameText.replace('\n', '')))
                        #reserved[nameText.]
                        self.names.append(nameText.replace('\n', ''))
                except IndexError:
                    pass



    def t_LTEQ(self, t):
        r'<='
        t.value = 'LTEQ'
        return t


    def t_GTEQ(self, t):
        r'>='
        t.value = 'GTEQ'
        return t


    def t_ML(self, t):
        r'<<'
        t.value = 'ML'
        return t


    def t_MG(self, t):
        r'>>'
        t.value = 'MG'
        return t


    def t_LT(self, t):
        r'<'
        t.value = 'LT'
        return t


    def t_EQ(self, t):
        r'='
        t.value = 'EQ'
        return t


    def t_GT(self, t):
        r'>'
        t.value = 'GT'
        return t


    #xml_data()
    #alist = list(reserved.values())
    tokens = ['GT', 'EQ', 'LT', 'LTEQ', 'GTEQ',
              'id', 'string', 'IPv4', 'IPv6','newline', 'int', 'MAC',
              'ML', 'MG'] + list(reserved.values())


    def t_IPv4(self, t):
        #r'(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\p{N}\p{L}]+)?'
        r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
        return t


    def t_IPv6(self, t):
        #r"""((:|[0-9a-fA-F]{0,4}):)([0-9a-fA-F]{0,4}:){0,5}((([0-9a-fA-F]{0,4}:)?(:|[0-9a-fA-F]{0,4}))|(((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\.){3}
        #(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])))(%[\p{N}\p{L}]+)?"""
        r"""
        (?:(?:(?:[A-F0-9]{1,4}:){6}|(?=(?:[A-F0-9]{0,4}:){0,6}(?:[0-9]{1,3}\.){3}
        [0-9]{1,3}(?![:.\w]))(([0-9A-F]{1,4}:){0,5}|:)((:[0-9A-F]{1,4}){1,5}:|:))
        (?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|
        [01]?[0-9][0-9]?)|(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}|
        (?=(?:[A-F0-9]{0,4}:){0,7}[A-F0-9]{0,4}(?![:.\w]))
        (([0-9A-F]{1,4}:){1,7}|:)((:[0-9A-F]{1,4}){1,7}|:))(?![:.\w])
        """
        return t


    def t_int(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %d", t.value)
            t.value = 0
            raise
        return t


    def t_MAC(self, t):
        r'([a-fA-F0-9]{2}[:\-]){5}[a-fA-F0-9]{2}'
        return t
    #def t_ent(self,t):
        #r'[a-zA-Z_][a-zA-Z_0-9]*'
        #if any(regex.match(t.value) for regex in self.regexes):
        #    pass
        #else:
            #raise SyntaxError
        #    t.type = self.reserved.get(t.value,'id')
        #return t

    def t_id(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        # matches also keywords, so be careful
        #print(list(self.reserved.values()))
        #self.reserved.get(t.value)
        if any(regex.match(t.value) for regex in self.regexes):
            pass
        else:
            #raise SyntaxError
            t.type = self.reserved.get(t.value, 'id')
        return t

        #t.type = self.reserved.get(t.value,'id')    # Check for reserved words

        #return t


    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t

    def t_comment(self, t):
        r"[ ]*\043[^\n]*" # \043 is '#'
        pass

    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def build(self, **kwargs):
        #self.xml_data()
        self.lexer = lex.lex(module=self, **kwargs)
        return self.lexer


if __name__ == "__main__":
    lexer = Tokenizer().build()
    lex.runmain(lexer)
