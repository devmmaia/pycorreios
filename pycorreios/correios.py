# -*- coding: utf-8 -*-
"""
correios.py
----------

Api para usar dados dos Correios
"""

__version__ = '0.2.0'
__author__ = {
    'Thiago Avelino': 'thiagoavelinoster@gmail.com',
    'Dilan Nery': 'dnerylopes@gmail.com',
}

import sys

python_version = sys.version_info[0]
from six.moves import urllib
import re

from xml.dom import minidom

try:
    from bs4 import BeautifulSoup
    

except ImportError:
    try:
        from BeautifulSoup import BeautifulSoup
    except ImportError:
        raise Exception('Você não tem o modulo BeautifulSoup', ImportError)


class Correios(object):

    PAC = 41106
    SEDEX = 40010
    SEDEX_10 = 40215
    SEDEX_HOJE = 40290
    E_SEDEX = 81019
    OTE = 44105
    NORMAL = 41017
    SEDEX_A_COBRAR = 40045

    def __init__(self):
        self.status = 'OK'

    def _getDados(self, tags_name, dom):
        dados = {}

        for tag_name in tags_name:
            try:
                dados[tag_name] = dom.getElementsByTagName(tag_name)[0]
                dados[tag_name] = dados[tag_name].childNodes[0].data
            except:
                dados[tag_name] = ''

        return dados

    # Vários campos viraram obrigatórios para cálculo de frete:
    # http://www.correios.com.br/webServices/PDF/SCPP_manual_implementacao_calculo_remoto_de_precos_e_prazos.pdf (páginas 2 e 3)
    def frete(self, cod, GOCEP, HERECEP, peso, formato,
              comprimento, altura, largura, diametro, mao_propria='N',
              valor_declarado='0', aviso_recebimento='N',
              empresa='', senha='', toback='xml'):

        base_url = "http://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx"

        fields = [
            ('nCdEmpresa', empresa),
            ('sDsSenha', senha),
            ('nCdServico', cod),
            ('sCepOrigem', HERECEP),
            ('sCepDestino', GOCEP),
            ('nVlPeso', peso),
            ('nCdFormato', formato),
            ('nVlComprimento', comprimento),
            ('nVlAltura', altura),
            ('nVlLargura', largura),
            ('nVlDiametro', diametro),
            ('sCdMaoPropria', mao_propria),
            ('nVlValorDeclarado', valor_declarado),
            ('sCdAvisoRecebimento', aviso_recebimento),
            ('StrRetorno', toback),
        ]

        url = base_url + "?" + urllib.parse.urlencode(fields)
        dom = minidom.parse(urllib.request.urlopen(url))

        tags_name = ('MsgErro',
                     'Erro',
                     'Codigo',
                     'Valor',
                     'PrazoEntrega',
                     'ValorMaoPropria',
                     'ValorValorDeclarado',
                     'EntregaDomiciliar',
                     'EntregaSabado',)  

        # consulta de mais de um servico simultaneamente
        qtd_servicos = len(str(cod).split(','))
        
        if (qtd_servicos > 1):
            return self._dom_to_object(dom.firstChild)

        return self._getDados(tags_name, dom)

    def cep(self, numero):
        url = 'http://cep.republicavirtual.com.br/web_cep.php?formato=' \
              'xml&cep=%s' % str(numero)
        dom = minidom.parse(urllib.request.urlopen(url))

        tags_name = ('uf',
                     'cidade',
                     'bairro',
                     'tipo_logradouro',
                     'logradouro',)

        resultado = dom.getElementsByTagName('resultado')[0]
        resultado = int(resultado.childNodes[0].data)
        if resultado != 0:
            return self._getDados(tags_name, dom)
        else:
		    return {}
    
            

    def encomenda(self, numero):
        # Usado como referencia o codigo do Guilherme Chapiewski
        # https://github.com/guilhermechapiewski/correios-api-py

        url = 'http://websro.correios.com.br/sro_bin/txect01$.QueryList?' \
              'P_ITEMCODE=&P_LINGUA=001&P_TESTE=&P_TIPO=001&P_COD_UNI=%s' % \
              str(numero)

        html = urllib.request.urlopen(url).read()
      
        table = re.search(b'<table.*</TABLE>', html, re.S).group(0)

        parsed = BeautifulSoup(table, "html.parser")
        
        dados = []

        for count, tr in enumerate(parsed.findAll('tr')):
            if count > 0 and str(tr).strip() != '':
                if re.match(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}',
                            tr.contents[0].string):

                    dados.append({
                        'data': tr.contents[0].string,
                        'local': tr.contents[1].string,
                        'status': tr.contents[2].font.string
                    })

                else:
                    dados[len(dados) - 1]['detalhes'] = tr.contents[0].string

        return dados


    def _dom_to_object(self, dom):
        result ={}
        child_tags = [child for child in dom.childNodes if isinstance(child,minidom.Element)]
        if not child_tags:
            content = ''.join(txt.data.strip() for txt in dom.childNodes if isinstance(txt,minidom.Text))
            return content       
        else:
            tags = set([tag.tagName for tag in child_tags])
            for tagName in tags:
                elements = dom.getElementsByTagName(tagName)
                if len(elements) > 1:
                    content = []
                    for e in elements:
                        content.append(self._dom_to_object(e))
                        result[dom.tagName] = content
                else:
                    content = self._dom_to_object(elements[0])
                    result[tagName]=content
        return result
