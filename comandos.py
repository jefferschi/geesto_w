# bibliotecas nativas
from tkinter import *
from tkinter import messagebox
from datetime import *
import pymsgbox as pymb
import os
# from decimal import Decimal #pesquisar depois como usar, testei na tela de pedido e não funcionou


#biblioteca nativa para manipulaçã de banco de dados SQLite
import sqlite3

#configurações padrão, criar posteriormente uma classe para estes padrões
bt_lar = 60 #largura botoes
bt_alt = 30 #altura botoes
bt_bd = 3 #borda interna  botoes

bt_bg = '#33FF99' #background botões - cor dos botões
bt_fg = '#3A373A' #frontground (cor da fonte) - mesma cor fundo


tl_bg = '#3A373A' #background das telas , inclusive janela principal

lista_prod = []  

class Comandos():

    """comandos dos botões e funções de rotina"""

    def conecta_bd(self):
        """conecta no banco de dados"""
        self.conn = sqlite3.connect('estoque.db')
        self.cursor = self.conn.cursor() #habilita escrever em sql
    
    def desconecta_bd(self):
        """desconecta do banco de dados"""
        self.conn.close()
   
    def cria_tabelas(self):

        """cria tabelas produto, categoria, movimento, usuarios, forma_pagto caso não existam.       
        cria tabela dentro do banco de dados por meio do sql. As aspas triplas em execute, serve para que, 
        caso necessário, use aspas dupla ou comum dentro do código sql"""

        # senha do parceiro para criar as tabelas
        senha_parceiro = 'Irunamo'
        
        # confere se o arquivo existe
        arquivo = 'estoque.db'
        if(os.path.exists(arquivo)):
            pass
        else:
            # se não existir, pedir senha para criar
            senha_digitada = str(pymb._passwordTkinter(title='Criação das tabelas', text='Digite a senha do Parceiro'))
            if senha_digitada != senha_parceiro:
                messagebox.showinfo(title='Atenção!', message='Senha não confere.')
                quit()
            else:

                self.conecta_bd()

                #tabela usuarios
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usuarios (
                        usuario TEXT PRIMARY KEY UNIQUE,
                        senha CHAR
                        );        
                """)
                
                #cria usuário ADMINISTRADOR 
                self.cursor.execute(""" 
                    SELECT usuario FROM usuarios WHERE usuario = "ADMINISTRADOR"
                """)
                checagem = self.cursor.fetchall()

                if len(checagem) == 0:
                    self.cursor.execute(""" 
                        INSERT INTO usuarios (usuario, senha) VALUES ("ADMINISTRADOR","Master[]")
                    """)
                    self.conn.commit()
                    

                #tabela categorias
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categorias (
                        codigo TEXT PRIMARY KEY UNIQUE,
                        categoria CHAR
                    );
                """)
                
                #tabela produtos
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS produtos (
                        codigo TEXT PRIMARY KEY UNIQUE, 
                        cod_barras CHAR(20) UNIQUE ,
                        produto VARCHAR(50) NOT NULL,
                        categoria CHAR,
                        ativo INT,
                        estoque INT,
                        preco_compra REAL,
                        preco_venda REAL,
                        fator_conv INT         
                    );
                """)

                #tabela movimento
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS movimento (
                        num_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                        tipo CHAR(10) NOT NULL,
                        cod_produto TEXT NOT NULL,
                        produto VARCHAR(50),
                        quantidade INT NOT NULL,
                        data DATE NOT NULL,
                        observacao CHAR(100),
                        preco_unit REAL,
                        valor_total REAL,
                        FOREIGN KEY (cod_produto) REFERENCES produtos(codigo)
                    );
                """)

                #tabela forma_pagto
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS formas_pagto (
                        codigo TEXT UNIQUE,
                        forma_pagto TEXT PRIMARY KEY UNIQUE,
                        taxa REAL
                    );
                """)

                #inclui campos forma_pagto, custo, valor_taxa, mrg_brt na tabela movimento       
                try:
                    self.cursor.execute("""
                        ALTER TABLE movimento ADD COLUMN forma_pagto TEXT
                    """)
                except:
                    pass

                try:
                    self.cursor.execute("""
                        ALTER TABLE movimento ADD COLUMN custo REAL
                    """)
                except:
                    pass
                try:
                    self.cursor.execute("""
                        ALTER TABLE movimento ADD COLUMN valor_taxa REAL
                    """)
                except:
                    pass
                
                try:
                    self.cursor.execute("""
                        ALTER TABLE movimento ADD COLUMN mrg_brt REAL
                    """)
                except:
                    pass
                
                self.conn.commit() # no sql ele valida essa informação no banco de dados
                
                self.desconecta_bd()

    # funções para (des)habilitar campos da tela movimento
    def desabilita_campos(self):
        self.ent_data.config(state=DISABLED)
        self.ent_estoque.config(state=DISABLED)

    def habilita_campos(self):
        self.ent_data.config(state=NORMAL)
        self.ent_estoque.config(state=NORMAL)


    # funções para tela e dados de categoria categoria
    def limpa_ent_categ(self):
        self.ent_cod_categ.delete(0, END)
        self.ent_desc_categ.delete(0, END)

    def nova_categoria(self):
        """insere nova categoria no banco de dados"""
        
        #pega as entradas
        self.codigo_cat = self.ent_cod_categ.get()
        self.desc_categoria = self.ent_desc_categ.get()
               
      
        if self.codigo_cat == '' or self.desc_categoria == '':
            messagebox.showinfo('Atenção!',message='Preencha os campos', parent=self.tl_categ)
        else:

            try:    
                self.conecta_bd()       
                #self.cursor.execute("INSERT INTO categorias (categoria) VALUES ('"+self.categoria+"')")
                self.cursor.execute("INSERT INTO categorias (codigo, categoria) VALUES ('"+self.codigo_cat+"','"+self.desc_categoria+"')")
                self.conn.commit()
                self.atualiza_categ()
                self.limpa_ent_categ()
                messagebox.showinfo('Mensagem!',message='Categoria cadastrada!', parent=self.tl_categ)
                self.desconecta_bd()  
            except:
              
               messagebox.showerror(title='Atenção!',message='Código já existente',parent=self.tl_categ)
                
            #atualização da combobox categoria da tela produtos
            self.conecta_bd()
            self.dados = self.cursor.execute(""" SELECT DISTINCT(categoria) as categoria FROM categorias""")
            self.lista_combo = [r for r, in self.dados]
            self.comb_categoria.configure(values=self.lista_combo)
            self.desconecta_bd()


    def atualiza_categ(self):
        self.lt_categ.delete(*self.lt_categ.get_children()) #entender essa linha e ver alternativas
        self.conecta_bd()
        lista_nova = self.cursor.execute(""" SELECT codigo, categoria FROM categorias ORDER BY categoria ASC; """)

        for i in lista_nova:
            self.lt_categ.insert('',END, values=i)

        self.desconecta_bd()

    def selec_categoria(self,event):
        """função chamada quando ocorre evento de duploc clique na treeview categoria"""
        self.limpa_ent_categ()
        self.lt_categ.selection()

        for n in self.lt_categ.selection():
            col1, col2 = self.lt_categ.item(n, 'values')
            self.ent_cod_categ.insert(END, col1)
            self.ent_desc_categ.insert(END,col2)

    def apaga_categoria(self):
        self.codigo_cat = self.ent_cod_categ.get()
        self.desc_categoria = self.ent_desc_categ.get()
        self.conecta_bd()
        
        if self.codigo_cat == '':
            messagebox.showinfo(title='Atenção', message='Para apagar, selecione clicando duas vezes sobre uma categoria',parent=self.tl_categ)            
        else:
            self.cursor.execute(" DELETE FROM categorias WHERE codigo = ('"+self.codigo_cat+"')")
            self.conn.commit()
            self.desconecta_bd()
            self.limpa_ent_categ()
            self.atualiza_categ()
            messagebox.showinfo(title='Mensagem', message='Registro apagado!',parent=self.tl_categ)

    def altera_categoria(self):
        self.codigo_cat = self.ent_cod_categ.get()
        self.desc_categoria = self.ent_desc_categ.get()
        self.conecta_bd()

        self.cursor.execute(""" UPDATE categorias SET categoria = ? WHERE codigo = ? """, (self.desc_categoria, self.codigo_cat)) 
        self.conn.commit()
        self.desconecta_bd()
        self.atualiza_categ()
        self.limpa_ent_categ()
        messagebox.showinfo(title='Informação', message='Categoria alterada!',parent=self.tl_categ)

    # funções para a tela de produto
    def limpa_ent_prod(self):
        self.ent_cod_prod.delete(0, END)
        self.ent_cod_barra_p.delete(0, END)
        self.ent_produto_p.delete(0, END)
        self.comb_categoria.delete(0, END)
        self.ent_pr_compra_p.delete(0,END)
        self.ent_pr_venda_p.delete(0,END)
        self.ent_ft_conv_p.delete(0,END)

        #self.atualiza_prod()

    def novo_produto(self):
        """insere novo produto o banco de dados"""
        
        #pega as entradas
        self.cod_barras = self.ent_cod_barra_p.get()
        self.codigo = self.ent_cod_prod.get()
        self.produto = self.ent_produto_p.get()
        if self.codigo =='' or self.cod_barras=='' or self.produto =='':
            self.desconecta_bd()
            messagebox.showinfo('Atenção!', message='Preencha os campos obrigatórios', parent=self.tl_prod)
        else:

            try:
                    
                self.pr_venda = float(self.ent_pr_venda_p.get().replace(',','.'))
                self.pr_compra = float(self.ent_pr_compra_p.get().replace(',','.'))
                self.ft_conv = self.ent_ft_conv_p.get()
                self.categoria = self.comb_categoria.get()
                self.ativo = self.v_ativo.get()
                self.estoque = int()

                self.conecta_bd()
            
               
                self.cursor.execute(""" INSERT INTO produtos (codigo, cod_barras, produto, categoria, ativo, estoque,
                            preco_compra, preco_venda, fator_conv)
                            VALUES (?,?,?,?,?,?,?,?,?)""", (self.codigo, self.cod_barras, self.produto, self.categoria, 
                            self.ativo,self.estoque,self.pr_compra,self.pr_venda,self.ft_conv))
                self.conn.commit()
                self.desconecta_bd()
                self.atualiza_prod()
                self.limpa_ent_prod()
                messagebox.showinfo('Mensagem!', message='Produto cadastrado!', parent=self.tl_prod)

            except:
              
               messagebox.showerror(title='Atenção!',message='Código de barras e/ou do produto já existente(s)', parent=self.tl_prod)
            
    def atualiza_prod(self):
        """atualiza a lista treeview da tela produtos sem filtro"""
        self.lt_prod.delete(*self.lt_prod.get_children())
        self.conecta_bd()
        lista_nova = self.cursor.execute(""" SELECT produto, categoria, estoque, codigo, cod_barras, preco_compra, 
        preco_venda, fator_conv, ativo FROM produtos ORDER BY produto ASC; """)

        for i in lista_nova:
            self.lt_prod.insert('',END, values=i)

        self.desconecta_bd()
    
    def busca_desc_prod(self):
        """busca na lista de produto da tela de produtos, os resultados a partir da descrição do produto após clicar em buscar"""
        
        self.ent_produto_p.insert(index=0, string='%')
        self.ent_produto_p.insert(END,string='%')#colocar % no final do texto para buscar aproximado
        produto = self.ent_produto_p.get()
        self.ent_produto_p.delete(0,END)
        

        if produto == '%%':
            messagebox.showinfo(title='Mensagem', message='Preencha o nome do produto', parent=self.tl_prod)
            self.atualiza_prod()
        else:
            self.lt_prod.delete(*self.lt_prod.get_children())
            self.conecta_bd()

            self.cursor.execute("""SELECT produto, categoria, estoque, codigo, cod_barras, preco_compra, preco_venda, fator_conv, ativo 
                        FROM produtos WHERE produto LIKE '%s' ORDER BY produto ASC""" % produto)

            lista_prod = self.cursor.fetchall()

            for i in lista_prod:
                self.lt_prod.insert('',END,values=i)

            self.desconecta_bd()

    # funções a partir da tela de movimento
    def busca_prod_mov(self):

        """atualiza a treeview de busca e pega os dados do produto selecionado"""
        self.lt_busca.delete(*self.lt_busca.get_children())
        self.ent_produto.insert(index=0,string='%')
        self.ent_produto.insert(END,'%') #colocar % no final do texto para buscar aproximado
        produto = self.ent_produto.get()
        self.ent_produto.delete(0,END)

        self.conecta_bd()

        self.cursor.execute("""SELECT produto, categoria, estoque, preco_venda, codigo, cod_barras, ativo FROM produtos
            WHERE produto LIKE '%s' ORDER BY produto ASC""" % produto)

        lista_prod = self.cursor.fetchall()
        

        for i in lista_prod:
            self.lt_busca.insert('',END,values=i)

        self.desconecta_bd()


    def cancela_movimento(self, event):
        """seleciona o movimento para cancelá-lo"""
        
        self.limpa_ent_mov()
        self.lt_movimento.selection()

        
        for n in self.lt_movimento.selection():
            data, prod, qtd, mov, frm_pagto, preco, valor_total, obs, cod, nreg = self.lt_movimento.item(n, 'values')
            self.nreg = nreg
            self.cod = cod
            self.qtd = int(qtd)
            self.prod = prod
            self.mov = str(mov)
        
        #verifica se registro já foi cancelado
        if self.mov.find('/') > 0:
            messagebox.showinfo(title='Atenção!', message='Registro já cancelado.')
        else:
            self.mov = self.mov+'/CANC'

            #busca estoque do produto
            self.conecta_bd()
            self.cursor.execute(" SELECT estoque FROM produtos WHERE codigo = ('"+self.cod+"')")
            estoque = self.cursor.fetchone()
            self.estoque = int(estoque[0])
            self.desconecta_bd()
            
        
            #confirma se usuário quer cancelar o registro
            mensagem = ('Deseja cancelar o registro de '+mov+'? Essa ação impacta no movimento e no estoque.'+
                        '\n\nRegistro nº'+self.nreg+'\nProduto '+self.prod+'\nQuantidade '+str(self.qtd))

            resposta = messagebox.askyesno(title='ATENÇÃO!', message=mensagem)

            if resposta == True:

                #confirma usuário
                senha_coletada = str(pymb._passwordTkinter(title='Acesso ao usuário', text='Digite a senha do ADMINISTRADOR'))
                self.conecta_bd()
                self.cursor.execute(""" SELECT senha FROM usuarios WHERE usuario = "ADMINISTRADOR" """)
                senha_adm = self.cursor.fetchone()
                self.desconecta_bd()
                senha_adm = str(senha_adm[0])

                #calcula o estoque se usuário for aceito
                if senha_coletada == senha_adm:
                    
                    #atualiza texto do tipo de movimento
                    self.conecta_bd()
                    self.cursor.execute(""" UPDATE movimento SET tipo = ? WHERE num_registro = ? """, (self.mov, self.nreg))
                    self.conn.commit()
                    self.desconecta_bd()


                    #atualiza o estoque conforme o tipo do movimento
                    if mov == 'Entrada':
                        self.calcula_estoque(self.estoque,self.qtd*-1,self.cod)
                    elif mov == 'Saída':
                        self.calcula_estoque(self.estoque,self.qtd,self.cod)
                    messagebox.showinfo(title='Confirmação!', message='Registro cancelado.')
                    self.ent_cod_barra.config(state=NORMAL)

                    self.atualiza_mov()
                else:
                    messagebox.showinfo(title='Atenção!', message='Senha não confere.') 
                
            
    def selec_prod_mov(self, event):
        """seleciona o produto a partir da busca feita na tela movimento"""
        self.limpa_ent_mov()
        
        self.lt_busca.selection()

        data_atual = date.today()
        data_formatada = data_atual.strftime('%d/%m/%Y')

        for n in self.lt_busca.selection():
            col1, col2, col3, col4, col5, col6, col7 = self.lt_busca.item(n,'values')

            self.ent_produto.insert(END,col1)
            self.ent_estoque.insert(END,col3)
            self.ent_preco.insert(END,col4)
            self.ent_cod.insert(END,col5)
            self.ent_cod_barra.insert(END,col6)
            self.ent_data.insert(0,data_formatada)
            self.ent_qtd.insert(0,'1')
            self.comb_frm_pagto.insert(0,'DINHEIRO')

        
        self.tl_bsc_mov.destroy()
        self.desabilita_campos()
        self.ent_qtd.focus()
    

        
        
    def selec_produto(self, event):
        """exibe os dados do produto selecionado com 
        duplo clique na treeview a partir da tela de produtos"""
        
        self.limpa_ent_prod()
        self.lt_prod.selection()
        

        for n in self.lt_prod.selection():
            prod, cat, col3, cod, barra, pr_compra, pr_venda, fc, col9 = self.lt_prod.item(n, 'values')
            self.ent_produto_p.insert(END, prod)
            self.comb_categoria.insert(END,cat)
            self.ent_cod_prod.insert(END, cod)
            self.ent_cod_barra_p.insert(END,barra)
            self.ent_pr_compra_p.insert(END,pr_compra)
            self.ent_pr_venda_p.insert(END,pr_venda)
            self.ent_ft_conv_p.insert(END,fc)
            #self.check_ativo.setvar(self.v_ativo,'1') - tentar colocar o campo de acordo com o banco de dados
            
        
    def altera_produto(self):
        self.codigo = self.ent_cod_prod.get()
        
        self.conecta_bd()
        
        #conferir se código já existe na tabela
        self.cursor.execute(" SELECT codigo FROM produtos WHERE codigo = ('"+self.codigo+"')")
        consulta = self.cursor.fetchall()
        existe_codigo = len(consulta)

        if existe_codigo == 0 or existe_codigo == '':
            messagebox.showinfo(title='Atenção!', message='Produto não existe', parent=self.tl_prod)
        else:

            self.cod_barras = self.ent_cod_barra_p.get()
            
            self.produto = self.ent_produto_p.get()
            self.categoria = self.comb_categoria.get()
            self.pr_compra = float(self.ent_pr_compra_p.get().replace(',','.'))
            self.pr_venda = float(self.ent_pr_venda_p.get().replace(',','.'))
            self.fc = self.ent_ft_conv_p.get()

            self.ativo = self.v_ativo.get()

            self.cursor.execute(""" UPDATE produtos SET cod_barras = ?, produto = ?, categoria = ?, preco_compra = ?, preco_venda = ?,
                                fator_conv = ?,ativo = ? WHERE codigo = ? """, (self.cod_barras, self.produto, self.categoria, 
                                self.pr_compra, self.pr_venda, self.fc, self.ativo, self.codigo))

            self.conn.commit()
            self.desconecta_bd()
            self.atualiza_prod()
            self.limpa_ent_prod()
            messagebox.showinfo(title='Informação', message='Registro alterado!', parent=self.tl_prod)

    def calcula_estoque(self,estoque,qtd,codigo):
        self.estoque = int(estoque)
        self.qtd = int(qtd)
        self.cod = codigo
        self.estoque += int(self.qtd)
        
        self.conecta_bd()
        self.cursor.execute(""" UPDATE produtos SET estoque = ? WHERE codigo = ? """, (self.estoque, self.cod))
        self.conn.commit()

        self.desconecta_bd()


    def limpa_ent_mov(self):
        self.habilita_campos()
        self.ent_produto.delete(0, END)
        self.ent_qtd.delete(0, END)
        self.ent_data.delete(0, END)
        self.comb_frm_pagto.delete(0, END)
        self.ent_estoque.delete(0, END)
        self.ent_cod.delete(0, END)
        self.ent_obs.delete(0, END)
        self.ent_cod_barra.delete(0, END)
        self.ent_preco.delete(0,END)

        self.ent_cod_barra.focus()  

    

    def chama_cod(self,event):
        """chama os campos de produto na tela movimento a partir da inclusão do código do produto"""

        #armazena os valores para recolocá-los após limpeza dos campos       
        cod_prod_mov = self.ent_cod.get()
        movimento = self.tipo_mov.get()

        self.limpa_ent_mov()
        self.ent_cod.insert(END,cod_prod_mov)
        self.ent_qtd.focus()

        self.conecta_bd()

        if movimento ==2:
            self.cursor.execute(" SELECT cod_barras, produto, estoque, preco_venda FROM produtos WHERE codigo = ('"+cod_prod_mov+"')")
        elif movimento ==1:
            self.cursor.execute(" SELECT cod_barras, produto, estoque, preco_compra FROM produtos WHERE codigo = ('"+cod_prod_mov+"')")

        busca_prod = self.cursor.fetchall()
        existe_dados = len(busca_prod) #verifica se existe o código do produto após dar tab

        self.desconecta_bd()

        if existe_dados == 0:
            messagebox.showinfo(title='Mensagem', message='Código não cadastrado')
            self.limpa_ent_mov()
            self.ent_cod.focus()

        else:
            data_atual = date.today()
            data_formatada = data_atual.strftime('%d/%m/%Y')

            #coloca os valores do produto e dos demais campos nas entrys
            for registro in busca_prod:
                (cod_barras, produto, estoque, preco) = registro
                self.ent_cod_barra.insert(0, cod_barras)  #pode-se colocar END no lugar de 0
                self.ent_produto.insert(0, produto)
                self.ent_estoque.insert(0, estoque)
                self.ent_preco.insert(0,preco)
                self.ent_data.insert(0,data_formatada)
                self.ent_qtd.insert(0,'1')
                self.comb_frm_pagto.insert(0,'DINHEIRO')

        self.desabilita_campos()

    def chama_cod_barra(self, event):
        """chama os campos de produto na tela movimento a partir da inclusão do código de barras"""        
        cod_barras_mov = self.ent_cod_barra.get()
        movimento = self.tipo_mov.get()
        
        self.limpa_ent_mov()
        self.ent_cod_barra.insert(END, cod_barras_mov)
        self.ent_qtd.focus()

        

        self.conecta_bd()

        if movimento == 2:
            self.cursor.execute(" SELECT codigo, produto, estoque, preco_venda FROM produtos WHERE cod_barras = ('"+cod_barras_mov+"')")
        elif movimento == 1:
            self.cursor.execute(" SELECT codigo, produto, estoque, preco_compra FROM produtos WHERE cod_barras = ('"+cod_barras_mov+"')")

        busca_prod = self.cursor.fetchall()
        existe_dados = len(busca_prod) #verifica se existe o código de barras após dar tab

        self.desconecta_bd()

        if existe_dados == 0:
            messagebox.showinfo(title='Mensagem', message='Código não cadastrado')
            self.limpa_ent_mov()
            self.ent_cod_barra.focus()
           
        else:
            data_atual = date.today()
            data_formatada = data_atual.strftime('%d/%m/%Y')

            #coloca os valores do produto e dos demais campos nas entrys
            for registro in busca_prod:
                (codigo, produto, estoque, preco) = registro
                self.ent_cod.insert(0, codigo)  #pode-se colocar END no lugar de 0
                self.ent_produto.insert(0, produto)
                self.ent_estoque.insert(0, estoque)
                self.ent_preco.insert(0,preco)
                self.ent_data.insert(0,data_formatada)
                self.ent_qtd.insert(0,'1')
                self.comb_frm_pagto.insert(0,'DINHEIRO')

        self.desabilita_campos()

        
    
    def chama_preco(self):
        """altera o preço entre entrada e saída ao selecionar o tipo de movimento"""
        cod_barra = self.ent_cod_barra.get()
        movimento = self.tipo_mov.get()

        if cod_barra != "":
            self.ent_preco.delete(0,END)

            self.conecta_bd()

            if movimento == 2:
                self.cursor.execute(" SELECT preco_venda FROM produtos WHERE cod_barras = ('"+cod_barra+"')")
            elif movimento == 1:
                self.cursor.execute(" SELECT preco_compra FROM produtos WHERE cod_barras = ('"+cod_barra+"')")

            preco = self.cursor.fetchall()
            
            self.ent_preco.insert(0,preco)
            
            self.desconecta_bd()

    def atualiza_mov(self):
        """ atualiza a lista treeview da tela movimento"""
        self.lt_movimento.delete(*self.lt_movimento.get_children())

        data_filtro = self.data_filtro_mov.get()
        
        self.conecta_bd()
        lista_nova = self.cursor.execute(" SELECT data, produto, quantidade, tipo, forma_pagto, preco_unit, valor_total,observacao, cod_produto, num_registro FROM movimento WHERE data = ('"+data_filtro+"') ORDER BY num_registro DESC;")

        for i in lista_nova:
            self.lt_movimento.insert('',END, values=i)

        self.desconecta_bd()

    

    def novo_movimento(self):
        
        self.cod = self.ent_cod.get()
        self.frm_pagto = self.comb_frm_pagto.get()
        
        if self.cod == '' or self.frm_pagto == '':
            messagebox.showinfo('Atenção!', message='Preencha os campos')
            self.ent_cod_barra.focus() 
       
        else: 
            #pegar as entradas
            self.produto = self.ent_produto.get()
            self.qtd = int(self.ent_qtd.get())
            self.data = self.ent_data.get()
            self.frm_pagto = self.comb_frm_pagto.get()
            self.estoque = int(self.ent_estoque.get())
            self.preco = float(self.ent_preco.get().replace(',','.'))
            self.obs = self.ent_obs.get()
            self.mov_num = self.tipo_mov.get()

            #converte valor do movimento para texto conforme dicionário
            self.mov_tex = self.dic_mov[self.mov_num]
            
            #cria e calcula a variável valor total
            self.valor_total = self.qtd * self.preco

            self.conecta_bd()
            
            """nova parte para buscar novos campos em alter table"""

            #encontra a taxa sobre o movimento de acordo com a forma de pagto
            self.cursor.execute("SELECT taxa FROM formas_pagto WHERE formas_pagto.forma_pagto = ('"+self.frm_pagto+"')")
            dados = self.cursor.fetchone()

            taxa = float(dados[0])
            
            """
            dados = self.cursor.fetchall()
            for taxa in dados:
                taxa = float(taxa[0])
            """
            self.valor_taxa = round(self.valor_total*(taxa/100),2)
            

            #encontra o preço de compra do produto e adiciona no campo custo da tabela movimento            
            self.cursor.execute(" SELECT preco_compra FROM produtos WHERE codigo = ('"+self.cod+"')")
            dados = self.cursor.fetchone()
            self.custo = float(dados[0])
            self.custo_total = round(self.custo*self.qtd,2)
            
            """
            dados = self.cursor.fetchall()
            for custo in dados:
                self.custo = float(custo[0])*self.qtd
            """
            
            self.mrg_brt = round(self.valor_total - (self.custo_total + self.valor_taxa),2)

            self.cursor.execute(""" INSERT INTO movimento (tipo, cod_produto, produto, quantidade, data, preco_unit, valor_total,
                        observacao, forma_pagto, valor_taxa, custo, mrg_brt) VALUES (?,?,?,?,?,?,?,?,?,?,?,?) """, 
                        (self.mov_tex, self.cod, self.produto,self.qtd,self.data,self.preco, self.valor_total, self.obs, 
                        self.frm_pagto, self.valor_taxa, self.custo_total, self.mrg_brt))
                        
            self.conn.commit()
            self.desconecta_bd()
            self.atualiza_mov()
            self.limpa_ent_mov()
            
            #verifica o movimento para atualizar a variável e calcular o estoque 
            if self.mov_num == 2:            
                self.qtd *= -1
            """
            else:
                self.qtd = self.qtd
            """
            self.calcula_estoque(self.estoque,self.qtd,self.cod) 
            
            messagebox.showinfo('Mensagem!', message='Movimento registrado!')
            self.ent_cod_barra.focus()  

            #self.tipo_mov = IntVar(self.raiz,value=2) #retorna para saída o tipo de movimento
            
            self.habilita_campos()

    def nova_frm_pagto(self):
        """insere forma de pagamento no banco de dados"""

        #pega as entradas
        self.codigo_frm_pagto = self.ent_cod_forma.get()
        self.desc_frm_pagto = self.ent_desc_forma.get()
        self.taxa = self.ent_taxa.get()


        if self.codigo_frm_pagto == '' or self.desc_frm_pagto =='' or self.taxa =='':
            messagebox.showinfo('Atenção!', message='Preencha todos os campos', parent=self.tl_frm_pagto)
        else:
            try:
                self.conecta_bd()
                cmd_sql = """INSERT INTO formas_pagto (codigo, forma_pagto, taxa) VALUES (?,?,?)"""
                self.cursor.execute(cmd_sql,(self.codigo_frm_pagto,self.desc_frm_pagto,self.taxa))
                self.conn.commit()

                #atualização dos dados para a combobox forma pagamento da tela movimento
                self.dados = self.cursor.execute(""" SELECT DISTINCT(forma_pagto) as forma_pagto FROM formas_pagto""")
                self.lista_combo = [r for r, in self.dados]
                self.comb_frm_pagto.configure(values=self.lista_combo)
                
                self.desconecta_bd()
                self.atualiza_frm_pagto()
                self.limpa_ent_frm_pagto()
                messagebox.showinfo('Mensagem!',message='Forma de pagamento cadastrada!', parent=self.tl_frm_pagto)
            except:
                messagebox.showwarning('Alerta!',message='Codigo ou descrição já existente',parent=self.tl_frm_pagto)
            
            
                

    def atualiza_frm_pagto(self):
        self.lt_forma.delete(*self.lt_forma.get_children())
        self.conecta_bd()
        lista_nova = self.cursor.execute(""" SELECT codigo, forma_pagto, taxa FROM formas_pagto ORDER BY forma_pagto ASC; """)
        
        for i in lista_nova:
                self.lt_forma.insert('',END, values=i)

        self.desconecta_bd()

    def limpa_ent_frm_pagto(self):
        self.ent_cod_forma.delete(0,END)
        self.ent_desc_forma.delete(0,END)
        self.ent_taxa.delete(0,END)

    def atualiza_usuario(self):
        self.lt_usuario.delete(*self.lt_usuario.get_children()) #entender essa linha e ver alternativas
        self.conecta_bd()
        lista_nova = self.cursor.execute(""" SELECT usuario FROM usuarios ORDER BY usuario ASC; """)

        for i in lista_nova:
            self.lt_usuario.insert('',END, values=i)

        self.desconecta_bd()
    
    def selec_usuario(self,event):
        """função chamada quando ocorre evento de duplo clique na treeview usuario"""
        self.limpa_ent_usuarios()
        self.lt_usuario.selection()

        for n in self.lt_usuario.selection():
            col1 = self.lt_usuario.item(n, 'values')
            self.ent_usuario.insert(END, col1)

        self.ent_usuario.config(state=DISABLED)        


    def limpa_ent_usuarios(self):
        self.ent_usuario.delete(0,END)
        self.ent_senha.delete(0,END)
        self.ent_senha_rep.delete(0,END)

    def altera_senha_usuario(self):
        self.usuario = self.ent_usuario.get()
        self.senha = self.ent_senha.get()
        self.senha_rep = self.ent_senha_rep.get()
        
        if self.senha != self.senha_rep or self.senha == '':
            messagebox.showinfo(title='Atenção', message='Senhas diferentes ou está(ão) em branco', parent=self.tl_usuario)
        else:

            self.conecta_bd()

            self.cursor.execute(""" UPDATE usuarios SET senha = ? WHERE usuario = ? """, (self.senha, self.usuario)) 
            self.conn.commit()
            self.desconecta_bd()
            self.atualiza_usuario()
            self.limpa_ent_usuarios()
            messagebox.showinfo(title='Informação', message='Senha alterada!', parent=self.tl_usuario)
    
    def altera_frm_pagto(self):
        self.codigo =  self.ent_cod_forma.get()
        self.frm_pagto = self.ent_desc_forma.get()
        self.taxa = self.ent_taxa.get()
        
        self.conecta_bd()

        self.cursor.execute(""" UPDATE formas_pagto SET forma_pagto = ?, taxa = ? WHERE codigo = ? """, (self.frm_pagto, self.taxa, self.codigo)) 
        self.conn.commit()
        self.desconecta_bd()
        self.atualiza_frm_pagto()
        self.limpa_ent_frm_pagto()
        messagebox.showinfo(title='Informação', message='Forma de pagto alterada!', parent=self.tl_frm_pagto)
    
    def selec_frm_pagto(self,event):
        """função chamada quando ocorre evento de duploc clique na treeview forma de pagamento"""
        self.limpa_ent_frm_pagto()
        self.lt_forma.selection()

        for n in self.lt_forma.selection():
            col1, col2, col3 = self.lt_forma.item(n, 'values')
            self.ent_cod_forma.insert(END, col1)
            self.ent_desc_forma.insert(END,col2)
            self.ent_taxa.insert(END,col3)

 
        
    def ordena_lt_prod(self):
        """atualiza a lista treeview da tela produtos a partir do radiobutton de ordenação"""
        #colocar depois apenas a função atualiza_prod com esses parâmentros para servir para todas as ocasiões
        self.lt_prod.delete(*self.lt_prod.get_children())

        self.ordem = self.ordem_prod.get()
        self.dic = self.dic_ordem_prod[self.ordem]

        
        self.conecta_bd()
        if self.dic == 'codigo':
            lista_nova = self.cursor.execute(""" SELECT produto, categoria, estoque, codigo, cod_barras, preco_compra, 
                preco_venda, fator_conv, ativo FROM produtos ORDER BY codigo ASC; """ )
                
            for i in lista_nova:
                self.lt_prod.insert('',END, values=i)
        
        elif self.dic == 'produto':
            lista_nova = self.cursor.execute(""" SELECT produto, categoria, estoque, codigo, cod_barras, preco_compra, 
                    preco_venda, fator_conv, ativo FROM produtos ORDER BY produto ASC; """ )
                   
            for i in lista_nova:
                self.lt_prod.insert('',END, values=i)

        self.desconecta_bd()

    def chama_evento(self):
        self.raiz.event_generate("<Return>")
    

    def chama_cod_barra_lp(self, event):
        """chama os campos de produto na tela lista de pedido a partir da inclusão do código de barras"""        
        
        cod_barras_lp = self.ent_cod_barra_lp.get()
        movimento = self.tipo_mov.get()
        
        self.limpa_ent_tl_pedido()
        self.ent_cod_barra_lp.insert(END, cod_barras_lp)
        self.ent_qtd_lp.focus()


        self.conecta_bd()

        if movimento == 2:
            self.cursor.execute(" SELECT codigo, produto, preco_venda FROM produtos WHERE cod_barras = ('"+cod_barras_lp+"')")
        elif movimento == 1:
            self.cursor.execute(" SELECT codigo, produto, preco_compra FROM produtos WHERE cod_barras = ('"+cod_barras_lp+"')")

        busca_prod = self.cursor.fetchall()
        existe_dados = len(busca_prod) #verifica se existe o código de barras após dar tab

        self.desconecta_bd()

        if existe_dados == 0:
            messagebox.showinfo(title='Mensagem', message='Código não cadastrado', parent=self.tl_lt_pedido)
            self.limpa_ent_tl_pedido()
            self.ent_cod_barra_lp.focus()
           
        else:
            data_atual = date.today()
            data_formatada = data_atual.strftime('%d/%m/%Y')

            #coloca os valores do produto e dos demais campos nas entrys
            for registro in busca_prod:
                (codigo, produto, preco) = registro
                self.ent_cod_lp.insert(0, codigo)  #pode-se colocar END no lugar de 0
                self.ent_produto_lp.insert(0, produto)
                self.ent_preco_lp.insert(0,preco)
                self.ent_qtd_lp.insert(0,'1')

    def chama_cod_lp(self,event):
        """chama os campos de produto na tela do pedido a partir da inclusão do código do produto"""
        
        #armazena os valores para recolocá-los após limpeza dos campos       
        cod_prod_lp = self.ent_cod_lp.get()
        movimento = self.tipo_mov.get()

        self.limpa_ent_tl_pedido()
        self.ent_cod_lp.insert(END,cod_prod_lp)
        self.ent_qtd_lp.focus()

        self.conecta_bd()

        if movimento ==2:
            self.cursor.execute(" SELECT cod_barras, produto, preco_venda FROM produtos WHERE codigo = ('"+cod_prod_lp+"')")
        elif movimento ==1:
            self.cursor.execute(" SELECT cod_barras, produto, preco_compra FROM produtos WHERE codigo = ('"+cod_prod_lp+"')")

        busca_prod = self.cursor.fetchall()
        existe_dados = len(busca_prod) #verifica se existe o código do produto após dar tab

        self.desconecta_bd()

        if existe_dados == 0:
            messagebox.showinfo(title='Mensagem', message='Código não cadastrado', parent=self.tl_lt_pedido)
            self.limpa_ent_tl_pedido()
            self.ent_cod_lp.focus()

        else:
            data_atual = date.today()
            data_formatada = data_atual.strftime('%d/%m/%Y')

            #coloca os valores do produto e dos demais campos nas entrys
            for registro in busca_prod:
                (cod_barras, produto, preco) = registro
                self.ent_cod_barra_lp.insert(0, cod_barras)  #pode-se colocar END no lugar de 0
                self.ent_produto_lp.insert(0, produto)
                self.ent_preco_lp.insert(0,preco)
                self.ent_qtd_lp.insert(0,'1')


    def limpa_ent_tl_pedido(self):
        
        self.ent_produto_lp.delete(0, END)
        self.ent_qtd_lp.delete(0, END)
        self.ent_cod_lp.delete(0, END)
        self.ent_cod_barra_lp.delete(0, END)
        self.ent_preco_lp.delete(0,END)

        self.ent_cod_barra_lp.focus()
    
    def busca_prod_lp(self):

        """atualiza a treeview de busca e pega os dados do produto selecionado para a lista de pedido"""
        self.lt_busca_lp.delete(*self.lt_busca_lp.get_children())
        self.ent_produto_lp.insert(index=0,string='%')
        self.ent_produto_lp.insert(END,'%') #colocar % no final do texto para buscar aproximado
        produto = self.ent_produto_lp.get()
        self.ent_produto_lp.delete(0,END)

        self.conecta_bd()

        self.cursor.execute("""SELECT produto, categoria, estoque, preco_venda, codigo, cod_barras, ativo FROM produtos
            WHERE produto LIKE '%s' ORDER BY produto ASC""" % produto)

        lista_prod = self.cursor.fetchall()
        

        for i in lista_prod:
            self.lt_busca_lp.insert('',END,values=i)

        self.desconecta_bd()
    
    def selec_prod_lp(self, event):
        """seleciona o produto a partir da busca feita na tela lista de pedido"""
        self.limpa_ent_tl_pedido()
        
        self.lt_busca_lp.selection()

        data_atual = date.today()
        data_formatada = data_atual.strftime('%d/%m/%Y')

        for n in self.lt_busca_lp.selection():
            col1, col2, col3, col4, col5, col6, col7 = self.lt_busca_lp.item(n,'values')

            self.ent_produto_lp.insert(END,col1)
            #self.ent_estoque.insert(END,col3)
            self.ent_preco_lp.insert(END,col4)
            self.ent_cod_lp.insert(END,col5)
            self.ent_cod_barra_lp.insert(END,col6)
            #self.ent_data.insert(0,data_formatada)
            self.ent_qtd_lp.insert(0,'1')
            #self.comb_frm_pagto.insert(0,'DINHEIRO')

        
        self.tl_bsc_lp.destroy()
        self.ent_qtd_lp.focus()

    def adiciona_item_lp(self):
        """adiciona itens à lista de pedidos, para dar o total, antes de salvar um a um em registros"""

        self.lista_prod = lista_prod
        codigo = self.ent_cod_lp.get()
        if codigo == '':
            messagebox.showinfo('Atenção!', message='Preencha os campos')
            self.ent_cod_barra_lp.focus() 
       
        else:
           
            #pegar as entradas
            produto = self.ent_produto_lp.get()
            quantidade = int(self.ent_qtd_lp.get())
            preco = float(self.ent_preco_lp.get().replace(',','.'))

            #cria e calcula a variável valor total do item
            valor_total = round(quantidade * round(preco,2),2)
            
            prod_lp = (produto, quantidade, preco, valor_total, codigo)   
            self.lista_prod.append(prod_lp)

            
            self.atualiza_lp()
            self.limpa_ent_tl_pedido()
            
            #messagebox.showinfo('Mensagem!', message='Produto adicionado!', parent=self.tl_lt_pedido)
            self.ent_cod_barra_lp.focus()  

    def atualiza_lp(self):
        """ atualiza a lista treeview da tela lista do pedido"""
        self.lt_pedido.delete(*self.lt_pedido.get_children())

        lista_nova = self.lista_prod

        for i in lista_nova:
            self.lt_pedido.insert('',END, values=i)
        
        self.total_ped = round(float(),2)

        for t in self.lista_prod:
                self.total_ped += round(t[3],2)

        #rótulos para informar o valor total do pedido        
        
        Label(self.qd_tl_lt_pedido,text='Total do Pedido:', 
            font=("Arial",15)).place(relx=0.2, rely=0.9)
        self.rt_total_ped = Label(self.qd_tl_lt_pedido,text='R$ %.2f'%self.total_ped,
              font=("Arial",15))
        self.rt_total_ped.place(relx=0.45, rely=0.9)
       

    def remove_item_lp(self, event):
        """seleciona o item da lista de pedido para removê-lo"""
        
        self.limpa_ent_tl_pedido()
        self.rt_total_ped.destroy()

        for col in self.lt_pedido.selection():
            prod, qtd, preco, valor_total, cod = self.lt_pedido.item(col, 'values')
        
        for i, item in enumerate(self.lista_prod):
            if item[4] == cod:
                self.lista_prod.pop(i)
                break
        
        self.atualiza_lp()
    
    def novo_movimento_lp(self):
        """inclui novos movimentos a partir da lista de pedido"""
        
        data_atual = date.today()
        data_formatada = data_atual.strftime('%d/%m/%Y')
        data = data_formatada

        obs=''

        frm_pagto_lp = self.comb_frm_pagto_lp.get()
        mov_num = self.tipo_mov.get()
        
        #converte valor do movimento para texto conforme dicionário
        mov_tex = self.dic_mov[mov_num]
        
        self.conecta_bd()
        
        """nova parte para buscar novos campos em alter table"""

        #encontra a taxa sobre o movimento de acordo com a forma de pagto
        self.cursor.execute("SELECT taxa FROM formas_pagto WHERE formas_pagto.forma_pagto = ('"+frm_pagto_lp+"')")
        dados = self.cursor.fetchone()

        taxa = float(dados[0])
        
        for reg, item in enumerate(self.lista_prod):
            self.conecta_bd()
            
            prod, qtd, preco, vl_total, cod = item
            vl_taxa = round(vl_total*(taxa/100),2)
            
            #encontra o preço de compra do produto e adiciona no campo custo da tabela movimento            
            self.cursor.execute(" SELECT preco_compra FROM produtos WHERE codigo = ('"+cod+"')")
            dados = self.cursor.fetchone()
            custo = float(dados[0])
            custo_total = round(custo*qtd,2)
            mrg_brt = round(vl_total - (custo_total + vl_taxa),2)

            self.cursor.execute(""" INSERT INTO movimento (tipo, cod_produto, produto, quantidade, data, preco_unit, valor_total,
                        observacao, forma_pagto, valor_taxa, custo, mrg_brt) VALUES (?,?,?,?,?,?,?,?,?,?,?,?) """, 
                        (mov_tex, cod, prod, qtd, data, preco, vl_total, obs, 
                        frm_pagto_lp, vl_taxa, custo_total, mrg_brt))
                        
            self.conn.commit()

            # movimenta o estoque
            # pega o estoque atual do produto
            self.cursor.execute("SELECT estoque FROM produtos WHERE codigo = ('"+cod+"')")
            dados_est = self.cursor.fetchone()
            estoque_atual = int(dados_est[0])
            
            # verifica o movimento entrada ou saída
            if mov_num == 2:
                qtd *= -1
            
            self.calcula_estoque(estoque_atual,qtd,cod) 

        self.desconecta_bd()
        #self.lista_prod.clear() #esta função está ligada ao evento de fechar a tela de pedido, portanto seria redundante.
        self.tl_lt_pedido.destroy()
        self.atualiza_mov()
        messagebox.showinfo('Mensagem!', message='Movimento registrado!')
