# bibliotecas nativas
from tkinter import *
from datetime import *
import pymsgbox as pymb
from tkinter import messagebox
from tkinter import simpledialog


import csv
import pandas as pd
import os
import tempfile

#from decimal import Decimal #pesquisar depois como usar, testei na tela de pedido e não funcionou

#biblioteca nativa para manipulaçã de banco de dados SQLite


#biblioteca do projeto
from comandos import Comandos

class Relatorios(Comandos):
    """classe para os relatorios e consultas na tela, pdf ou excel"""


    def tela_rel_vend(self):
        """relatório de vendas com margem bruta ponderada"""
        # mostrar valor e quantidade por produto
        # mostrar margem % e bruta financeira

        senha_coletada = str(pymb._passwordTkinter(title='Acesso ao usuário', text='Digite a senha do ADMINISTRADOR'))
        self.conecta_bd()
        self.cursor.execute(""" SELECT senha FROM usuarios WHERE usuario = "ADMINISTRADOR" """)
        senha_adm = self.cursor.fetchone()
        self.desconecta_bd()
        senha_adm = str(senha_adm[0])

        if senha_coletada != senha_adm:
            messagebox.showinfo(title='Atenção!', message='Senha não confere.')
        else:

            """tela do relatório"""
            self.tl_rel_fat = Toplevel(self.raiz)
            self.tl_rel_fat.title('Relatório de Vendas')
            self.tl_rel_fat.geometry('1000x650+280+30')
            #self.tl_rel_fat.minsize(width=600, height=600)
            self.tl_rel_fat.resizable(True, True)

            """widgets para parâmetros"""
            self.qd_param = Frame(self.tl_rel_fat)

            self.rt_dt_inicio = Label(self.qd_param,text='Data início')
            self.rt_dt_fim = Label(self.qd_param,text='Data fim')

            self.ent_dt_inicio = Entry(self.qd_param, width=10)
            self.ent_dt_fim = Entry(self.qd_param, width=10)

            data_formatada = date.today().strftime('%d/%m/%Y')
            self.ent_dt_inicio.insert(0,data_formatada)
            self.ent_dt_fim.insert(0,data_formatada)

            self.bt_param = Button(self.qd_param,text='Filtrar',fg='white', bd=1.5, bg='#3333FF',command=self.relat_vend_teste)

            """empacotamentos"""
            self.qd_param.place(width=280, height=70, relx=0.28, rely=0.01)

            self.rt_dt_inicio.place(relx=0, rely=0)
            self.rt_dt_fim.place(relx=0.4, rely=0)
            self.ent_dt_inicio.focus()

            self.ent_dt_inicio.place(relx=0, rely=0.35)
            self.ent_dt_fim.place(relx=0.4, rely=0.35)

            self.bt_param.place(relx=0.75,rely=0.25)

            """quadro e caixa de texto para o relatório"""
            self.qd_rel_fat = LabelFrame(self.tl_rel_fat, text='Venda e margem bruta ponderada')
            self.txt_rel_fat = Text(self.qd_rel_fat, bg='white',padx=7,pady=10)

            self.qd_rel_fat.place(relwidth=0.95, relheight=0.85, relx=0.01,rely=0.1)
            self.txt_rel_fat.place(relwidth=0.95, relheight=0.95, relx=0.02, rely=0.02)

    

    def relat_vend(self):
        """calcula o valor, a quantidade e a margem bruta dos produtos vendidos no período selecionado"""

        data_inicio = self.ent_dt_inicio.get()
        data_fim = self.ent_dt_fim.get()

        #variáveis para o total final do rodapé
        total_fat = float()
        total_mb = float()
        total_qtd = int()
        total_custo = float()

        """
        #apenas para registrar outra forma de escrever com as variáveis

        comando_sql2 = "SELECT produto, SUM(valor_total) FROM movimento WHERE tipo=('Saída')AND data >= '%s' AND data <= '%s' GROUP BY produto ORDER BY produto ASC;" %(data_inicio, data_fim)
        comando_sql3 = "SELECT produto, SUM(quantidade), SUM(valor_total) FROM movimento WHERE tipo=('Saída') AND data >= ('"+data_inicio+"') AND data <= ('"+data_fim+"') GROUP BY produto ORDER BY produto ASC;"
        """

        #pesquisa banco de dados de acordo com a solicitação do usuário
        comando_sql = """SELECT movimento.produto, SUM(quantidade), SUM(valor_total),
                            SUM(mrg_brt), produtos.fator_conv, SUM(custo)
                            FROM movimento
                            INNER JOIN produtos ON cod_produto = codigo
                            WHERE tipo= ? AND data >= ? AND data <= ?
                            GROUP BY movimento.produto
                            ORDER BY SUM(valor_total) DESC;
                      """

        self.conecta_bd()

        self.cursor.execute(comando_sql,('Saída',data_inicio,data_fim))
        dados = self.cursor.fetchall()
        self.desconecta_bd()

        self.txt_rel_fat.delete('1.0',END)
        self.txt_rel_fat.insert(1.0,'VENDA DE '+data_inicio+' A '+data_fim+3*'\n')
        self.txt_rel_fat.insert(2.0,40*'=')

        colunas = ('Produto'+28*' '+'|Quantidade'+6*' '
                    +'|Valor Total'+7*' '+'|Margem Bruta'+6*' '+'|% MB'+2*'\n')

        self.txt_rel_fat.insert(END,colunas)

        for registro in dados:

            margem_bruta = round(registro[3],2)
            valor_total = registro[2]
            custo_total = registro[5]
            per_mb = round((margem_bruta/custo_total)*100,2)

            #atribui à strings os valores para inserir no textbox
            col_prod = str(registro[0])
            col_qtd = str(registro[1])
            col_vl_t = '%.2f'%registro[2]

            #parâmetros para espaços
            tam_txt_prod = len(registro[0])
            tam_txt_qtd = len(str(registro[1]))
            tam_txt_vl_t = len(str(registro[2]))
            tam_txt_mb_t = len(str(margem_bruta))

            espaco1 = str((35-tam_txt_prod)*' ')
            espaco2 = str((15-tam_txt_qtd)*' ')
            espaco3 = str((13-tam_txt_vl_t)*' ')
            espaco4 = str((14-tam_txt_mb_t)*' ')

            texto = col_prod+espaco1+'| '+col_qtd+espaco2+'| R$ '+col_vl_t+espaco3+'| R$ '+str(margem_bruta)+espaco4+'| '+str(per_mb)+'%'+'\n'

            self.txt_rel_fat.insert(INSERT,texto)

            #soma o total do faturamento, qtd, margem bruta e total MB, e % MB
            total_fat += registro[2]
            total_custo += registro[5]
            total_qtd += registro[1]
            total_mb += margem_bruta
            mb_pond = round(100*(total_mb/total_custo),2)

        self.txt_rel_fat.insert(END,'\nRESUMO\n  Total de venda -> R$ %.2f'%(total_fat))
        self.txt_rel_fat.insert(END,'\n  Total da margem bruta -> R$ '+str(round(total_mb,2)))
        self.txt_rel_fat.insert(END,'\n  Margem bruta ponderada -> '+str(mb_pond)+'%')
        self.txt_rel_fat.insert(END,'\n\n=== Margem bruta calculada sobre o custo ===')

        """
        salvar_rel = messagebox.askyesno(title='Relatório de vendas',
                        message='Relatório gerado.\nDeseja salvar em arquivo?', parent=self.tl_rel_fat)

        if salvar_rel == True:
            pass
        else:
            pass
        """

    def exporta_xlsx(self):
        """ exporta a tabela MOVIMENTO e/ou PRODUTOS para xlsx """

        senha_coletada = str(pymb._passwordTkinter(title='Acesso ao usuário', text='Digite a senha do ADMINISTRADOR'))
        self.conecta_bd()
        self.cursor.execute(""" SELECT senha FROM usuarios WHERE usuario = "ADMINISTRADOR" """)
        senha_adm = self.cursor.fetchone()
        self.desconecta_bd()
        senha_adm = str(senha_adm[0])

        if senha_coletada != senha_adm:
            messagebox.showinfo(title='Atenção!', message='Senha não confere.')
        else:
            messagebox.showinfo(title='Atenção!', message='Baixar arquivos PRODUTOS e MOVIMENTO')

            self.conecta_bd()

            sql_cab_mov = """PRAGMA table_info(movimento)"""
            self.cursor.execute(sql_cab_mov)
            retorno_cab_mov = self.cursor.fetchall()
            cab_mov = []

            for i in retorno_cab_mov:
                cab_mov.append(i[1])

            sql_cab_prod = """PRAGMA table_info(produtos)"""
            self.cursor.execute(sql_cab_prod)
            retorno_cab_prod = self.cursor.fetchall()
            cab_prod = []

            for i in retorno_cab_prod:
                cab_prod.append(i[1])


            sql_tab_mov = 'SELECT * FROM movimento'
            self.cursor.execute(sql_tab_mov)
            tab_mov = self.cursor.fetchall()

            sql_tab_prod = 'SELECT * FROM produtos'
            self.cursor.execute(sql_tab_prod)
            tab_prod = self.cursor.fetchall()

            self.desconecta_bd()

            df_tab_mov = pd.DataFrame(tab_mov, columns=cab_mov)
            df_tab_prod = pd.DataFrame(tab_prod, columns=cab_prod)


            df_tab_mov.to_excel('movimento.xlsx')
            df_tab_prod.to_excel('produtos.xlsx')

            
            messagebox.showinfo(title='Download!', message='Arquivos xlsx baixados!')


    def exporta_csv(self):
        """ exporta a tabela MOVIMENTO e/ou PRODUTOS para csv """

        senha_coletada = str(pymb._passwordTkinter(title='Acesso ao usuário', text='Digite a senha do ADMINISTRADOR'))
        self.conecta_bd()
        self.cursor.execute(""" SELECT senha FROM usuarios WHERE usuario = "ADMINISTRADOR" """)
        senha_adm = self.cursor.fetchone()
        self.desconecta_bd()
        senha_adm = str(senha_adm[0])

        if senha_coletada != senha_adm:
            messagebox.showinfo(title='Atenção!', message='Senha não confere.')
        else:
            messagebox.showinfo(title='Atenção!', message='Baixar arquivo com os movimentos de saída e entrada')
            
            self.conecta_bd()
            
            consulta_cabecalho = """PRAGMA table_info(movimento)"""
            consulta_tabela = """ SELECT * FROM movimento """
            
            self.cursor.execute(consulta_cabecalho)
            retorno_cabecalho = self.cursor.fetchall()
            cabecalho = []

            self.cursor.execute(consulta_tabela)
            retorno_dados = self.cursor.fetchall()

            self.desconecta_bd()
            
            for i in retorno_cabecalho:
                cabecalho.append(i[1])

            arquivo = 'movimento.csv'
            
            with open(arquivo,'w',newline='') as arquivo_csv:
                movimento = csv.writer(arquivo_csv, delimiter=',', dialect='excel')
                movimento.writerow(cabecalho)

                for l in retorno_dados:
                    movimento.writerow(l)

            messagebox.showinfo(title='Exportação de arquivo', message='Arquivo movimento.csv exportado!')

    def relat_vend_teste(self):
        """ teste para relatorio de vendas para solucionar problema de data """

        #datas string para cabeçalho
        data_i = self.ent_dt_inicio.get()
        data_f = self.ent_dt_fim.get()

        #datas string transformadas em data/hora
        data_inicio = datetime.strptime(self.ent_dt_inicio.get(),'%d/%m/%Y')
        data_fim =  datetime.strptime(self.ent_dt_fim.get(),'%d/%m/%Y')

        #datas/hora transformada em data
        data_inicio_form = datetime.strftime(data_inicio,'%Y-%m-%d')
        data_fim_form = datetime.strftime(data_fim,'%Y-%m-%d')

               
        #variáveis para o total final do rodapé
        total_fat = float()
        total_mb = float()
        total_qtd = int()
        total_custo = float()

        """
        #apenas para registrar outra forma de escrever com as variáveis

        comando_sql2 = "SELECT produto, SUM(valor_total) FROM movimento WHERE tipo=('Saída')AND data >= '%s' AND data <= '%s' GROUP BY produto ORDER BY produto ASC;" %(data_inicio, data_fim)
        comando_sql3 = "SELECT produto, SUM(quantidade), SUM(valor_total) FROM movimento WHERE tipo=('Saída') AND data >= ('"+data_inicio+"') AND data <= ('"+data_fim+"') GROUP BY produto ORDER BY produto ASC;"
        """

        #pesquisa banco de dados de acordo com a solicitação do usuário
        comando_sql = """SELECT movimento.produto, SUM(quantidade), SUM(valor_total),
                            SUM(mrg_brt), produtos.fator_conv, SUM(custo)
                            FROM movimento
                            INNER JOIN produtos ON cod_produto = codigo
                            WHERE tipo = '%s' AND date(substr(data,7,4) || '-' || substr(data,4,2) || '-' || substr(data,1,2))
                            BETWEEN '%s' AND '%s' 
                            GROUP BY movimento.produto
                            ORDER BY SUM(valor_total) DESC;
                      """

        self.conecta_bd()

        self.cursor.execute(comando_sql%('Saída',data_inicio_form, data_fim_form))
        dados = self.cursor.fetchall()
        self.desconecta_bd()

        self.txt_rel_fat.delete('1.0',END)
        self.txt_rel_fat.insert(1.0,'VENDA DE '+data_i+' A '+data_f+3*'\n')
        self.txt_rel_fat.insert(2.0,40*'=')

        colunas = ('Produto'+28*' '+'|Quantidade'+6*' '
                    +'|Valor Total'+7*' '+'|Margem Bruta'+6*' '+'|% MB'+2*'\n')

        self.txt_rel_fat.insert(END,colunas)

        for registro in dados:

            margem_bruta = round(registro[3],2)
            valor_total = registro[2]
            custo_total = registro[5]
            per_mb = round((margem_bruta/custo_total)*100,2)

            #atribui à strings os valores para inserir no textbox
            col_prod = str(registro[0])
            col_qtd = str(registro[1])
            col_vl_t = '%.2f'%registro[2]

            #parâmetros para espaços
            tam_txt_prod = len(registro[0])
            tam_txt_qtd = len(str(registro[1]))
            tam_txt_vl_t = len(str(registro[2]))
            tam_txt_mb_t = len(str(margem_bruta))

            espaco1 = str((35-tam_txt_prod)*' ')
            espaco2 = str((15-tam_txt_qtd)*' ')
            espaco3 = str((13-tam_txt_vl_t)*' ')
            espaco4 = str((14-tam_txt_mb_t)*' ')

            texto = col_prod+espaco1+'| '+col_qtd+espaco2+'| R$ '+col_vl_t+espaco3+'| R$ '+str(margem_bruta)+espaco4+'| '+str(per_mb)+'%'+'\n'

            self.txt_rel_fat.insert(INSERT,texto)

            #soma o total do faturamento, qtd, margem bruta e total MB, e % MB
            total_fat += registro[2]
            total_custo += registro[5]
            total_qtd += registro[1]
            total_mb += margem_bruta
            mb_pond = round(100*(total_mb/total_custo),2)

        self.txt_rel_fat.insert(END,'\nRESUMO\n  Total de venda -> R$ %.2f'%(total_fat))
        self.txt_rel_fat.insert(END,'\n  Total da margem bruta -> R$ '+str(round(total_mb,2)))
        self.txt_rel_fat.insert(END,'\n  Margem bruta ponderada -> '+str(mb_pond)+'%')
        self.txt_rel_fat.insert(END,'\n\n=== Margem bruta calculada sobre o custo ===')

        """
        salvar_rel = messagebox.askyesno(title='Relatório de vendas',
                        message='Relatório gerado.\nDeseja salvar em arquivo?', parent=self.tl_rel_fat)

        if salvar_rel == True:
            pass
        else:
            pass
        """
    
    def cupom_nfiscal(self):

        # input para endereço de entrega
        end_entrega = simpledialog.askstring(title="Entrega", prompt="Endereço de entrega")

        # variáveis 
        vl_pedido = 0.0
        data_atual = date.today()
        data_hora = datetime.now()
        data_formatada = data_hora.strftime('%d/%m/%Y %H:%M:%S')
        data = data_formatada

        frm_pagto_lp = self.comb_frm_pagto_lp.get()
        lista = self.lista_prod
       
        empresa = "ROTA BEBIDAS DISTRIBUIDORA"
        end_empresa = "Av. Min. Euríco Sales de Águiar, 158"
        bairro_empresa = "Campo Grande, Cariacica"
        tel_empresa = "TEL.: (27) 99779-8617"
        
        arq_temp = tempfile.mktemp(".txt")

        with open(arq_temp, "w") as arquivo:
            
            # cabeçalho
            arquivo.write("*"*45+"\n")
            arquivo.write(empresa+"\n")
            arquivo.write(end_empresa+"\n")
            arquivo.write(bairro_empresa+"\n")
            arquivo.write(tel_empresa+"\n")
            arquivo.write("*"*45+"\n\n")

            #informações da venda
            arquivo.write("Venda dia "+data+"\n")
            arquivo.write("Forma Pagto: "+frm_pagto_lp+"\n\n")

            # campos de cabeçalho
            arquivo.write("="*45+"\n")
            arquivo.write("PROD\t\t\t\tQTD\tTOTAL\n\n")

            for reg, item in enumerate(lista):
                prod, qtd, preco, vl_total, cod = item                
                vl_pedido += vl_total

                vl_total_f = "{:.2f}".format(vl_total)                

                tam_txt_prod = len(prod)
                if tam_txt_prod > 30:
                    tam_txt_prod = 30
                
                espaco1 = str(" "*(32-tam_txt_prod))

                arquivo.write(prod[:30]+espaco1+str(qtd)+"\t"+vl_total_f+"\n")
            
            vl_pedido_f = "{:.2f}".format(vl_pedido)
            arquivo.write("="*45+"\n")
            arquivo.write("Valor total -> "+vl_pedido_f+"\n\n")
            arquivo.write("*"*45+"\n\n")
            arquivo.write("ENDEREÇO DE ENTREGA: \n"+end_entrega)
            
        os.startfile(arq_temp,"print")

    