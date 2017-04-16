#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest import main
from pycorreios.correios import Correios


class CorreiosTest(unittest.TestCase):

    def test_frete(self):

    
        result = Correios().frete(Correios.SEDEX, '09840240', '09820650',
                                 1, 1, 18, 9, 13.5, 0)
        valor = float(result['Valor'].replace(',','.'))
        self.assertTrue(not result['MsgErro'])
        self.assertTrue(valor > 0)


    def test_frete_servicos(self):
        servicos = ','.join(str(i) for i in [Correios.SEDEX, Correios.PAC])
        result = Correios().frete(servicos, '09840240', '09820650',
                                 1, 1, 18, 9, 13.5, 0)
        results = result['Servicos']
        self.assertTrue(len(results)>1)
        for servico in results:
            self.assertTrue(not servico['MsgErro'])


    def test_cep(self):

        keys = ['tipo_logradouro','bairro','cidade','uf','logradouro']

        valor = Correios().cep('03971010')
        self.assertEqual(set(keys), set(valor.keys()))
        
        
    def test_encomenda(self):
        valor = Correios().encomenda('PN569489984BR')[0]
        self.assertEqual(valor['status'], 'Entrega Efetuada')

if __name__ == '__main__':
    main()
