# bibliotecas nativas
from tkinter import *
from tkinter import ttk
from datetime import *
import pymsgbox as pymb
import tkinter as tk
from tkinter import messagebox



#biblioteca do projeto
from relatorios import Relatorios
from comandos import Comandos


#variáveis globais de configurações - posteriormente substiruir pelo método style
bt_lar = 60 #largura botoes
bt_alt = 30 #altura botoes
bt_bd = 3 #borda interna  botoes

bt_bg = '#33FF99' #background botao salvar (verde)
bt_fg = '#3A373A' #frontground (cor da fonte) - mesma cor fundo


tl_bg = '#3A373A' #background das telas , inclusive janela principal


class Aplicativo(Relatorios):

    def __init__(self):
        self.cria_tabelas()
        self.raiz = Tk()
        self.janela()
        self.quadros()
        self.lista()
        self.botoes()
        self.menu_principal()
        self.dados_movimento()
        #self.atualiza_mov()

        self.raiz.mainloop() #verificar se pode ficar com self


    def janela(self):
        self.raiz.title('Gestão de Estoque - Rota Bebidas')
        self.raiz.geometry("{0}x{0}+0+0".format(self.raiz.winfo_screenwidth(), self.raiz.winfo_screenmmheight()))
        # self.raiz.geometry('1000x600+150+50')
        #self.raiz.overrideredirect(True) # trava a tela
        self.raiz.resizable(True,True)

        #self.raiz.config(bg=tl_bg)
        #self.raiz.minsize(width=1000, height=600)
        self.raiz.iconphoto(True, tk.PhotoImage(file='img/icone.png'))
        

    def menu_principal(self):

        self.menu_barra = Menu(self.raiz)
        self.raiz.config(menu=self.menu_barra) #configurando a tela principal para este menu

        self.menu_cad = Menu(self.menu_barra, tearoff=0)
        self.menu_rel = Menu(self.menu_barra, tearoff=0)
        self.menu_sobre = Menu(self.menu_barra, tearoff=0)

        self.menu_barra.add_cascade(label='Cadastro', menu=self.menu_cad, underline=0)
        self.menu_barra.add_cascade(label='Relatórios',menu=self.menu_rel, underline=0)
        self.menu_barra.add_cascade(label='Sobre', menu=self.menu_sobre, underline=1)

        #submenus Cadastro
        self.menu_cad.add_command(label='Produto',command=self.tela_produtos, underline=0)
        self.menu_cad.add_command(label='Categoria',command=self.tela_categorias,underline=0)
        self.menu_cad.add_command(label='Forma Pagto',command=self.tela_forma_pagto,underline=0)
        self.menu_cad.add_separator()
        self.menu_cad.add_command(label='Usuários',command=self.confirma_usuario, underline=0)
        self.menu_cad.add_separator()
        self.menu_cad.add_command(label='Sair',command=self.raiz.quit, underline=0)

        #submenus Relatórios
        self.menu_rel.add_command(label='Vendas', command=self.tela_rel_vend,underline=0)
        self.menu_rel.add_command(label='Baixar Excel', command=self.exporta_xlsx,underline=0)


        #submenus Sobre - colocar a versão


    def quadros(self):

        #quadro para os dados de entrada do movimento
        self.qd_dados = Frame(self.raiz, bd=3)
        self.qd_dados.place(height=165, width=740, relx=0.23, rely=0.01)

        self.qd_tipo_mov = Frame(self.raiz, bd=3)
        self.qd_tipo_mov.place(height=50, width=230, relx=0.01, rely=0.12)

        #quadro para a lista do movimento
        self.qd_movimento = LabelFrame(self.raiz, text='Movimento',bd=3)
        self.qd_movimento.place(relheight=0.68, relwidth=0.95, relx=0.02, rely=0.3)

        self.lf_filtro_mov = LabelFrame(self.raiz,text='Filtro do Movimento', width=180, height=90)
        self.lf_filtro_mov.place(relx=0.85,rely=0.1)


    def lista(self):

        self.barra_lt_mov = Scrollbar(self.qd_movimento)

        self.lt_movimento = ttk.Treeview(self.qd_movimento,
                            columns=('col1','col2','col3','col4','col5','col6','col7','col8','col9','col10'),
                           yscrollcommand=self.barra_lt_mov.set, show='headings') #.set atribui a scroll à lista

        self.barra_lt_mov.config(command=self.lt_movimento.yview) #configura a barra de rolagem para a lista de movimento


        self.lt_movimento.heading('#0', text='')
        self.lt_movimento.heading('#1', text='Data')
        self.lt_movimento.heading('#2', text='Produto')
        self.lt_movimento.heading('#3', text='Quant.')
        self.lt_movimento.heading('#4', text='Movimento')
        self.lt_movimento.heading('#5', text='Forma Pagto')
        self.lt_movimento.heading('#6', text='Preço')
        self.lt_movimento.heading('#7', text='Valor Total')
        self.lt_movimento.heading('#8', text='Observação')
        self.lt_movimento.heading('#9', text='Código')
        self.lt_movimento.heading('#10', text='Nº Registro')

        self.lt_movimento.column('#0', width=1)
        self.lt_movimento.column('#1', width=50)
        self.lt_movimento.column('#2', width=100)
        self.lt_movimento.column('#3', width=20, anchor=CENTER)
        self.lt_movimento.column('#4', width=30)
        self.lt_movimento.column('#5', width=50)
        self.lt_movimento.column('#6', width=50, anchor=SE)
        self.lt_movimento.column('#7', width=50, anchor=SE)
        self.lt_movimento.column('#8', width=100)
        self.lt_movimento.column('#9', width=10, anchor=SE)
        self.lt_movimento.column('#10', width=15, anchor=SE)



        #empacotamento da lista e barra de rolagem
        self.lt_movimento.place(relwidth=0.96, relheight=0.95, relx=0.01, rely=0.03)

        self.barra_lt_mov.pack(side=RIGHT, fill=Y)

        self.lt_movimento.bind("<Double-1>", self.cancela_movimento) #chama a função selec_movimento a partir de um duplo clique no registro
        

    def botoes(self):
        """
           botões da tela principal
        """
        self.bt_novo = Button(self.raiz,text='Salvar',fg=bt_fg, bg=bt_bg, bd=1.5, command=self.novo_movimento)
        self.bt_limpar = Button(self.raiz,text='Limpar',fg=bt_fg, bg='yellow', bd=1.5, command=self.limpa_ent_mov)
        self.bt_buscar = Button(self.raiz, text='Buscar',fg='white', bg='#3333FF', bd=1.5, command=self.chama_evento) #, chama_evento aciona tela_busca_mov: busca por nome do produto em uma nova tela

        self.bt_novo.place(relx=0.03, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_limpar.place(relx=0.1, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_buscar.place(relx=0.17, rely=0.2,width=bt_lar, height=bt_alt,)

        # botão para chamar a lista de pedido
        self.bt_lt_pedido = Button(self.raiz,text='Lista', bd=1.5, command=self.tela_lista_pedido)
        self.bt_lt_pedido.place(relx=0.85, rely=0.02)

    
    def dados_movimento(self):
        """rotulos e entradas para a tela principal de movimento de estoque"""

        #rotulos
        self.rt_cod_barra = Label(self.raiz,text='Código de barras') #está fora do quadro, está na raiz

        self.rt_produto = Label(self.qd_dados,text='Produto')
        self.rt_qtd = Label(self.qd_dados,text='Quantidade')
        self.rt_data = Label(self.qd_dados,text="Data")
        self.rt_frm_pagto = Label(self.qd_dados, text='Forma de Pagto')
        self.rt_estoque = Label(self.qd_dados, text='Estoque')
        self.rt_preco = Label(self.qd_dados, text='Preço')
        self.rt_cod = Label(self.qd_dados,text='Código do Produto')
        self.rt_obs = Label(self.qd_dados,text='Observação')

        #entradas
        self.ent_cod_barra = Entry(self.raiz, width=17) #está fora do quadro, está na raiz
        self.ent_produto = Entry(self.qd_dados, width=70)
        self.ent_cod = Entry(self.qd_dados, width=17)
        self.ent_qtd = Entry(self.qd_dados, width=12)
        #self.ent_nregistro = Entry(self.qd_dados, width=15,bg=tl_bg)
        self.ent_preco = Entry(self.qd_dados, width=10)
        self.ent_obs = Entry(self.qd_dados, width=77)
        self.ent_data = Entry(self.qd_dados, width=11)
        self.ent_estoque = Entry(self.qd_dados, width=10)

        #empacotamento rotulos e entradas
        self.rt_cod_barra.place(relx=0.03, rely=0.045) #está fora do quadro, está na raiz
        self.ent_cod_barra.place(relx=0.03, rely=0.0751)
        self.ent_cod_barra.focus()

        self.rt_produto.place(relx=0,rely=0.11)
        self.ent_produto.place(relx=0, rely=0.22)

        self.rt_qtd.place(relx=0.84,rely=0.11)
        self.ent_qtd.place(relx=0.84, rely=0.22)

        self.rt_cod.place(relx=0, rely=0.45)
        self.ent_cod.place(relx=0, rely=0.58)

        #self.rt_nregistro.place(relx=0.2, rely=0.45)
        #self.ent_nregistro.place(relx=0.2, rely=0.58)

        self.rt_estoque.place(relx=0.5, rely=0.45)
        self.ent_estoque.place(relx=0.5, rely=0.58)

        self.rt_preco.place(relx=0.69, rely=0.45)
        self.ent_preco.place(relx=0.69, rely=0.58)

        self.rt_data.place(relx=0.85, rely=0.45)
        self.ent_data.place(relx=0.85, rely=0.58)

        self.rt_obs.place(relx=0, rely=0.81)
        self.ent_obs.place(relx=0.13, rely=0.81)

        #radiobutton para opção de tipo de movimento - entrada ou saída

        self.tipo_mov = IntVar(self.qd_tipo_mov,value=2) #ver melhor o uso do radiobutton
        self.dic_mov = {1:'Entrada',2:'Saída'}

        self.rb_mov_ent = Radiobutton(self.qd_tipo_mov, text='Entrada', variable=self.tipo_mov,
                            command=self.chama_preco, value=1)
        self.rb_mov_saida = Radiobutton(self.qd_tipo_mov, text='Saída', variable=self.tipo_mov,
                            command=self.chama_preco, value=2)


        #empacotamento dos radiobutton
        self.rb_mov_ent.place(relx=0.025,rely=0.13)
        self.rb_mov_saida.place(relx=0.5,rely=0.13)

        #atualização dos dados para a combobox forma pagamento da tela movimento
        self.conecta_bd()
        self.dados = self.cursor.execute(""" SELECT DISTINCT(forma_pagto) as forma_pagto FROM formas_pagto""")
        self.lista_combo = [r for r, in self.dados]
        self.desconecta_bd()

        #cria combobox forma de pagamento
        self.comb_frm_pagto = ttk.Combobox(self.qd_dados,width=20,values=self.lista_combo)
        self.rt_frm_pagto.place(relx=0.22, rely=0.45)
        self.comb_frm_pagto.place(relx=0.22, rely=0.58)

        # campos para filtro de data do movimento
        data_formatada = date.today().strftime('%d/%m/%Y')

        Label(self.lf_filtro_mov,text='Data Mov').place(relx=0.01, rely=0.01)
        
        self.data_filtro_mov = Entry(self.lf_filtro_mov, width=11)

        self.data_filtro_mov.insert(0,data_formatada)
        self.data_filtro_mov.place(relx=0.41, rely=0.01)
        
        self.bt_filtro_mov = Button(self.lf_filtro_mov, text='Filtrar', bd=1.5, command=self.atualiza_mov)
        self.bt_filtro_mov.place(relx=0.25, rely=0.46)


        #chama funções de busca a partir das teclas Enter (principal e do teclado numérico) para cod barra, codigo e descrição
        
        self.ent_cod_barra.bind("<Return>",self.chama_cod_barra)
        
        self.ent_cod.bind('<Return>',self.chama_cod)
        self.ent_cod.bind('<KP_Enter>',self.chama_cod)

        self.ent_produto.bind('<Return>',self.tela_busca_mov)

        self.habilita_campos()

        #self.lt_forma.bind("<Double-1>", self.selec_frm_pagto) #criar a função selec_frm_pagto a partir de um duplo clique no registro

    def tela_produtos(self):
        """tela para cadastro de produtos"""

        #atualização da combobox categoria da tela produtos
        self.conecta_bd()

        self.dados = self.cursor.execute(""" SELECT DISTINCT(categoria) as categoria FROM categorias""")
        self.lista_combo = [r for r, in self.dados]

        self.desconecta_bd()

        """configurações da tela"""
        self.tl_prod = Toplevel(self.raiz)
        self.tl_prod.title('Cadastro de Produtos')
        self.tl_prod.geometry('700x650+400+30')
        #self.tl_prod.config(bg=tl_bg)
        #self.tl_prod.minsize(width=600, height=600)
        self.tl_prod.resizable(True, True)

        #variável para o check button campo Ativo igual a 1 ou 0
        self.v_ativo = IntVar(self.tl_prod,1)

        #self.dic_ativo = {1:'Ativo',0:'Inativo'}

        #rotulos, entradas, checkbutton e combobox de produtos
        self.rt_cod = Label(self.tl_prod,text='Código do Produto')
        self.rt_produto = Label(self.tl_prod,text='Produto')
        self.rt_cod_barra = Label(self.tl_prod,text='Código de barras')
        self.rt_pr_compra = Label(self.tl_prod,text='Preço de compra')
        self.rt_pr_venda = Label(self.tl_prod,text='Preço de venda')
        self.rt_ft_conv = Label(self.tl_prod,text='Fator conv.')
        self.rt_categoria = Label(self.tl_prod, text='Categoria')


        self.ent_cod_prod = Entry(self.tl_prod, width=17)
        self.ent_produto_p = Entry(self.tl_prod, width=74)
        self.ent_cod_barra_p = Entry(self.tl_prod, width=17)
        self.ent_pr_compra_p = Entry(self.tl_prod, width=10,)
        self.ent_pr_venda_p = Entry(self.tl_prod, width=10)
        self.ent_ft_conv_p = Entry(self.tl_prod, width=5)


        self.comb_categoria = ttk.Combobox(self.tl_prod,width=15,values=self.lista_combo)

        self.check_ativo = Checkbutton(self.tl_prod,text='Ativo',
                            variable=self.v_ativo, onvalue=1, offvalue=0)

        #radiobutton e labelframe para ordenar as colunas codigo e descrição

        self.qd_ord_prod = LabelFrame(self.tl_prod,text=' Ordenar por ',width=200, height=50)

        self.qd_ord_prod.place(x=320, rely=0.2)

        self.ordem_prod = IntVar(self.qd_ord_prod,value=2) #ver melhor o uso do radiobutton
        self.dic_ordem_prod = {1:'codigo',2:'produto'}

        self.rb_ord_cod = Radiobutton(self.qd_ord_prod, text='Código', variable=self.ordem_prod,
                            command=self.ordena_lt_prod, value=1)

        self.rb_ord_desc = Radiobutton(self.qd_ord_prod, text='Descrição', variable=self.ordem_prod,
                            command=self.ordena_lt_prod, value=2)

        self.ordem_prod = self.ordem_prod

        #empacotamento dos radiobutton
        self.rb_ord_cod.place(relx=0,rely=0)
        self.rb_ord_desc.place(relx=0.5,rely=0)

        #empacotamento rotulos, entradas, combobox, checkbox
        self.rt_cod.place(x=10, y=10)
        self.ent_cod_prod.place(x=10, y=30)
        self.ent_cod_prod.focus()


        self.rt_produto.place(x=220, y=10)
        self.ent_produto_p.place(x=220, y=30)

        self.rt_cod_barra.place(x=10, y=70)
        self.ent_cod_barra_p.place(x=10,y=90)

        self.rt_pr_compra.place(x=180,y=70)
        self.ent_pr_compra_p.place(x=180,y=90)

        self.rt_pr_venda.place(x=320,y=70)
        self.ent_pr_venda_p.place(x=320,y=90)

        self.rt_ft_conv.place(x=450,y=70)
        self.ent_ft_conv_p.place(x=450,y=90)

        self.rt_categoria.place(x=550, y=70)
        self.comb_categoria.place(x=550,y=90)
        self.check_ativo.place(x=548,y=125)

        #quadro, lista, barra rolagem
        self.qd_prod = Frame(self.tl_prod, highlightthickness=3)

        self.barra_lt_prod = Scrollbar(self.qd_prod)

        self.lt_prod = ttk.Treeview(self.qd_prod, columns=('prod','cat','est','cod','barra','compra','venda','fc','ativo'),
                        yscrollcommand=self.barra_lt_prod.set, show='headings')


        self.barra_lt_prod.config(command=self.lt_prod.yview)

        self.lt_prod.heading('#0', text='')
        self.lt_prod.heading('#1', text='Produto')
        self.lt_prod.heading('#2', text='Categoria')
        self.lt_prod.heading('#3', text='Estoque')
        self.lt_prod.heading('#4', text='Código')
        self.lt_prod.heading('#5', text='Cód. Barras')
        self.lt_prod.heading('#6', text='Pr. Compra')
        self.lt_prod.heading('#7', text='Pr. Venda')
        self.lt_prod.heading('#8', text='FC')
        self.lt_prod.heading('#9', text='Ativo')

        self.lt_prod.column('#0', width=1)
        self.lt_prod.column('#1', width=100)
        self.lt_prod.column('#2', width=50)
        self.lt_prod.column('#3', width=15)
        self.lt_prod.column('#4', width=15)
        self.lt_prod.column('#5', width=15)
        self.lt_prod.column('#6', width=15)
        self.lt_prod.column('#7', width=15)
        self.lt_prod.column('#8', width=5)
        self.lt_prod.column('#9', width=8)


        #empacotamento quadro, lista e barra rolagem
        self.qd_prod.place(relwidth=0.96, relheight=0.73, relx=0.01, rely=0.27)
        self.lt_prod.place(relwidth=0.96, relheight=0.95, relx=0.01, rely=0.03)
        self.barra_lt_prod.pack(side=RIGHT, fill=Y)


        #botões
        self.bt_novo = Button(self.tl_prod,text='Novo',fg=bt_fg, bd=1.5, bg=bt_bg, command=self.novo_produto)
        self.bt_alterar = Button(self.tl_prod,text='Alterar',fg=bt_fg, bd=1.5, bg='#9999FF', command=self.altera_produto)
        self.bt_limpar = Button(self.tl_prod,text='Limpar',fg=bt_fg, bd=1.5, bg='yellow', command=self.limpa_ent_prod)
        self.bt_buscar = Button(self.tl_prod, text='Buscar',fg='white', bd=1.5, bg='#3333FF', command=self.busca_desc_prod) #,command=self.busca_desc_prod)

        self.bt_novo.place(x=10, rely=0.21,width=bt_lar, height=bt_alt)
        self.bt_alterar.place(x=80, rely=0.21,width=bt_lar, height=bt_alt)
        self.bt_limpar.place(x=150, rely=0.21,width=bt_lar, height=bt_alt)
        self.bt_buscar.place(x=220, rely=0.21,width=bt_lar, height=bt_alt)

        self.atualiza_prod()

        self.lt_prod.bind("<Double-1>", self.selec_produto) #chama a função selec_produto a partir de um duplo clique no registro

        #self.ent_produto_p.bind("<Return>",self.busca_desc_prod)


    def tela_categorias(self):
        """tela para cadastro de categorias de produtos"""
        self.tl_categ = Toplevel(self.raiz)
        self.tl_categ.title('Cadastro de Categorias')
        self.tl_categ.geometry('400x500+450+30')
        #self.tl_categ.config(bg=tl_bg)
        #self.tl_categ.minsize(width=400, height=200)
        self.tl_categ.resizable(False, False)



        #rotulos, entradas, botoes (colocar botao apagar)
        self.rt_cod = Label(self.tl_categ,text='Código')
        self.rt_categ = Label(self.tl_categ, text='Categoria')

        self.ent_cod_categ = Entry(self.tl_categ, width=10)
        self.ent_desc_categ = Entry(self.tl_categ, width=23)


        #empacotamento rotulos, entradas e botoes
        self.rt_cod.place(x=10, y=10)
        self.ent_cod_categ.place(x=10, y=30)
        self.ent_cod_categ.focus()

        self.rt_categ.place(x=200, y=10)
        self.ent_desc_categ.place(x=200,y=30)


        #botões
        self.bt_novo = Button(self.tl_categ,text='Novo',fg=bt_fg, bd=1.5, bg=bt_bg, command=self.nova_categoria)
        self.bt_alterar = Button(self.tl_categ,text='Alterar',fg=bt_fg, bd=1.5, bg='#9999FF', command=self.altera_categoria)
        self.bt_limpar = Button(self.tl_categ,text='Limpar',fg=bt_fg, bd=1.5, bg='yellow', command=self.limpa_ent_categ)
        self.bt_apagar = Button(self.tl_categ, text='Apagar',fg='white', bd=1.5, bg='red',command=self.apaga_categoria)
        self.bt_buscar = Button(self.tl_categ, text='Buscar',fg='white', bd=1.5, bg='#3333FF')

        self.bt_novo.place(relx=0.03, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_alterar.place(relx=0.2, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_limpar.place(relx=0.37, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_apagar.place(relx=0.54, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_buscar.place(relx=0.25, rely=0.05,width=bt_lar, height=bt_alt)


        #quadro, lista e barra de rolagem
        self.qd_categ = Frame(self.tl_categ, highlightthickness=3)

        self.barra_lt_categ = Scrollbar(self.qd_categ)

        self.lt_categ = ttk.Treeview(self.qd_categ,columns=('col1','col2'),
                        yscrollcommand=self.barra_lt_categ.set,show='headings')

        self.barra_lt_categ.config(command=self.lt_categ.yview)

        self.lt_categ.heading('#0', text='')
        self.lt_categ.heading('#1', text='Código')
        self.lt_categ.heading('#2', text='Categoria')

        self.lt_categ.column('#0', width=1)
        self.lt_categ.column('#1', width=5)
        self.lt_categ.column('#2', width=200)

        #empacotamento quadro, lista e barra rolagem
        self.qd_categ.place(height=350, width=390, relx=0.01, rely=0.29)
        self.lt_categ.place(relwidth=0.93, relheight=0.95, relx=0.01, rely=0.03)
        self.barra_lt_categ.pack(side=RIGHT, fill=Y)

        self.atualiza_categ()

        self.lt_categ.bind("<Double-1>", self.selec_categoria) #chama a função selec_categoria a partir de um duplo clique no registro

    def tela_busca_mov(self,event):
        """tela para buscar os produtos cadastrados a partir de movimento """
        self.tl_bsc_mov = Toplevel(self.raiz)
        self.tl_bsc_mov.title('Buscar produto')
        self.tl_bsc_mov.geometry('700x650+400+30')
        #self.tl_bsc_mov.config(bg=tl_bg)
        #self.tl_bsc_mov.minsize(width=600, height=600)
        self.tl_bsc_mov.resizable(False, False)

        """ quadro, lista e barra de rolagem"""
        self.qd_bsc_mov = Frame(self.tl_bsc_mov, highlightthickness=3)

        self.barra_lt_busca = Scrollbar(self.qd_bsc_mov)

        self.lt_busca = ttk.Treeview(self.qd_bsc_mov,columns=('col1','col2','col3','col4','col5','col6','col7'),
                        yscrollcommand=self.barra_lt_busca.set, show='headings')

        self.barra_lt_busca.config(command=self.lt_busca.yview)

        self.lt_busca.heading('#0', text='')
        self.lt_busca.heading('#1', text='Produto')
        self.lt_busca.heading('#2', text='Categoria')
        self.lt_busca.heading('#3', text='Estoque')
        self.lt_busca.heading('#4', text='Preço Venda')
        self.lt_busca.heading('#5', text='Código')
        self.lt_busca.heading('#6', text='Código Barras')
        self.lt_busca.heading('#7', text='Ativo')

        self.lt_busca.column('#0', width=1)
        self.lt_busca.column('#1', width=200)
        self.lt_busca.column('#2', width=100)
        self.lt_busca.column('#3', width=30)
        self.lt_busca.column('#4', width=30)
        self.lt_busca.column('#5', width=30)
        self.lt_busca.column('#6', width=30)
        self.lt_busca.column('#7', width=10)

        #empacotamento quadro, lista e barra rolagem
        self.qd_bsc_mov.place(height=470, width=680, relx=0.01, rely=0.25)
        self.lt_busca.place(relwidth=0.96, relheight=0.95, relx=0.01, rely=0.03)
        self.barra_lt_busca.pack(side=RIGHT, fill=Y)
     
        self.busca_prod_mov()

        self.lt_busca.focus(self.lt_busca.get_children()[0])
        
        
        self.lt_busca.bind('<Double-1>', self.selec_prod_mov)

    def tela_forma_pagto(self):
        """tela para cadastro de forma de pagamento"""

        self.tl_frm_pagto = Toplevel(self.raiz)
        self.tl_frm_pagto.title('Cadastro de Forma de Pagamento')
        self.tl_frm_pagto.geometry('400x500+450+30')
        #self.tl_frm_pagto.config(bg=tl_bg)
        #self.tl_frm_pagto.minsize(width=400, height=200)
        self.tl_frm_pagto.resizable(False, False)


        #rotulos, entradas, botoes (colocar botao apagar)
        self.rt_cod = Label(self.tl_frm_pagto,text='Código')
        self.rt_forma_pagto = Label(self.tl_frm_pagto, text='Forma de Pagto')
        self.rt_taxa = Label(self.tl_frm_pagto, text='% Taxa')

        self.ent_cod_forma = Entry(self.tl_frm_pagto, width=10)
        self.ent_desc_forma = Entry(self.tl_frm_pagto, width=23)
        self.ent_taxa = Entry(self.tl_frm_pagto, width=10)
        self.ent_taxa.insert(0,'0.0')

        #empacotamento rotulos, entradas e botoes
        self.rt_cod.place(x=10, y=10)
        self.ent_cod_forma.place(x=10, y=30)
        self.ent_cod_forma.focus()

        self.rt_forma_pagto.place(x=200, y=10)
        self.ent_desc_forma.place(x=200,y=30)

        self.rt_taxa.place(x=200,y=50)
        self.ent_taxa.place(x=200, y=70)


        #botões
        self.bt_novo = Button(self.tl_frm_pagto,text='Novo',fg=bt_fg, bd=1.5, bg=bt_bg, command=self.nova_frm_pagto)
        self.bt_alterar = Button(self.tl_frm_pagto,text='Alterar',fg=bt_fg, bd=1.5, bg='#9999FF', command=self.altera_frm_pagto)
        self.bt_limpar = Button(self.tl_frm_pagto,text='Limpar',fg=bt_fg, bd=1.5, bg='yellow', command=self.limpa_ent_frm_pagto)
        self.bt_apagar = Button(self.tl_frm_pagto, text='Apagar',fg='white', bd=1.5, bg='red',command=None)
        self.bt_buscar = Button(self.tl_frm_pagto, text='Buscar',fg='white', bd=1.5, bg='#3333FF')

        self.bt_novo.place(relx=0.03, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_alterar.place(relx=0.2, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_limpar.place(relx=0.37, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_apagar.place(relx=0.54, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_buscar.place(relx=0.25, rely=0.05,width=bt_lar, height=bt_alt)


        #quadro, lista e barra de rolagem
        self.qd_frm_pagto = Frame(self.tl_frm_pagto, highlightthickness=3)

        self.barra_lt_forma = Scrollbar(self.qd_frm_pagto)

        self.lt_forma = ttk.Treeview(self.qd_frm_pagto,columns=('col1','col2', 'col3'),
                        yscrollcommand=self.barra_lt_forma.set,show='headings')

        self.barra_lt_forma.config(command=self.lt_forma.yview)

        self.lt_forma.heading('#0', text='')
        self.lt_forma.heading('#1', text='Código')
        self.lt_forma.heading('#2', text='Forma Pagto')
        self.lt_forma.heading('#3', text='% Taxa')


        self.lt_forma.column('#0', width=1)
        self.lt_forma.column('#1', width=5)
        self.lt_forma.column('#2', width=200)
        self.lt_forma.column('#3', width=5)


        #empacotamento quadro, lista e barra rolagem
        self.qd_frm_pagto.place(height=350, width=390, relx=0.01, rely=0.29)
        self.lt_forma.place(relwidth=0.93, relheight=0.95, relx=0.01, rely=0.03)
        self.barra_lt_forma.pack(side=RIGHT, fill=Y)

        self.atualiza_frm_pagto()

        self.lt_forma.bind("<Double-1>", self.selec_frm_pagto) #criar a função selec_frm_pagto a partir de um duplo clique no registro

    def confirma_usuario(self):

            senha_coletada = str(pymb._passwordTkinter(title='Acesso ao usuário', text='Digite a senha do ADMINISTRADOR'))
            self.conecta_bd()
            self.cursor.execute(""" SELECT senha FROM usuarios WHERE usuario = "ADMINISTRADOR" """)
            senha_adm = self.cursor.fetchone()
            self.desconecta_bd()
            senha_adm = str(senha_adm[0])

            if senha_coletada == senha_adm:
                self.tela_usuario()
            else:
                messagebox.showinfo(title='Atenção!', message='Senha não confere.')



    def tela_usuario(self):
        """tela para cadastro de usuários"""

        self.tl_usuario = Toplevel(self.raiz)
        self.tl_usuario.title('Cadastro de Usuários')
        self.tl_usuario.geometry('400x500+450+30')
        #self.tl_usuario.config(bg=tl_bg)
        #self.tl_usuario.minsize(width=400, height=200)
        self.tl_usuario.resizable(False, False)

        #rótulos e entradas
        self.rt_usuario = Label(self.tl_usuario,text='Usuário')
        self.rt_senha = Label(self.tl_usuario,text='Senha')
        self.rt_senha_rep = Label(self.tl_usuario,text='Repita a senha')

        self.ent_usuario = Entry(self.tl_usuario, width=30)
        self.ent_senha = Entry(self.tl_usuario, width=30, show='*')
        self.ent_senha_rep = Entry(self.tl_usuario, width=30, show='*')

        #empacotamentos rotulos e entradas
        self.rt_usuario.place(x=10, y=10)
        self.ent_usuario.place(x=10, y=30)
        self.ent_usuario.focus()

        self.rt_senha.place(x=10, y=60)
        self.ent_senha.place(x=10,y=80)
        self.rt_senha_rep.place(x=10, y=107)
        self.ent_senha_rep.place(x=10,y=127)

        #botões
        self.bt_novo = Button(self.tl_usuario,text='Novo',fg=bt_fg, bd=1.5, bg=bt_bg, command=None)
        self.bt_alterar = Button(self.tl_usuario,text='Alterar',fg=bt_fg, bd=1.5, bg='#9999FF', command=self.altera_senha_usuario)
        self.bt_apagar = Button(self.tl_usuario, text='Apagar',fg='white', bd=1.5, bg='red',command=None)

        self.bt_novo.place(relx=0.7, rely=0.03,width=bt_lar, height=bt_alt)
        self.bt_alterar.place(relx=0.7, rely=0.12,width=bt_lar, height=bt_alt)
        self.bt_apagar.place(relx=0.7, rely=0.21,width=bt_lar, height=bt_alt)

        #quadro, lista e barra de rolagem
        self.qd_usuario = Frame(self.tl_usuario, highlightthickness=3)

        self.barra_lt_usuario = Scrollbar(self.qd_usuario)

        self.lt_usuario = ttk.Treeview(self.qd_usuario,columns=('col1'),
                        yscrollcommand=self.barra_lt_usuario.set,show='headings')

        self.barra_lt_usuario.config(command=self.lt_usuario.yview)

        self.lt_usuario.heading('#0', text='')
        self.lt_usuario.heading('#1', text='Usuário')

        self.lt_usuario.column('#0', width=1)
        self.lt_usuario.column('#1', width=100)

        #empacotamento quadro, lista e barra rolagem
        self.qd_usuario.place(height=350, width=390, relx=0.01, rely=0.31)
        self.lt_usuario.place(relwidth=0.93, relheight=0.95, relx=0.01, rely=0.03)
        self.barra_lt_usuario.pack(side=RIGHT, fill=Y)

        self.atualiza_usuario()

        self.lt_usuario.bind("<Double-1>", self.selec_usuario) #criar a função a partir de um duplo clique no registro


    """ tela para lista de produtos a serem vendidos, possibilitando a venda por pedido, e não somente por produto"""
    def tela_lista_pedido(self):
        
        #perguntar a forma de pagamento antes de concluir o pedido

        self.tl_lt_pedido = Toplevel(self.raiz)
        self.tl_lt_pedido.title('Lista do Pedido')
        self.tl_lt_pedido.geometry('800x700+400+30')
        self.tl_lt_pedido.resizable(False, False)
        
        # quadros para dados do produto e para a lista do produtos
        self.qd_tl_lt_pedido = Frame(self.tl_lt_pedido, bd=3)
        self.qd_tl_lt_pedido.place(height=200, relwidth=0.98, relx=0.01, rely=0.01)

        self.qd_lt_pedido = Frame(self.tl_lt_pedido, bd=3)
        self.qd_lt_pedido.place(relheight=0.7, relwidth=0.98, relx=0.01, rely=0.3)

        
        # rótulos e entradas
        Label(self.qd_tl_lt_pedido,text='Código de barras').place(relx=0.01, rely=0.01)
        self.ent_cod_barra_lp = Entry(self.qd_tl_lt_pedido, width=17)
        self.ent_cod_barra_lp.place(relx=0.01, rely=0.13)
        self.ent_cod_barra_lp.focus()


        Label(self.qd_tl_lt_pedido,text='Produto').place(relx=0.25, rely=0.01)
        self.ent_produto_lp = Entry(self.qd_tl_lt_pedido, width=70)
        self.ent_produto_lp.place(relx=0.25, rely=0.12)
       
        Label(self.qd_tl_lt_pedido,text='Código do Produto').place(relx=0.01, rely=0.25)
        self.ent_cod_lp = Entry(self.qd_tl_lt_pedido, width=17)
        self.ent_cod_lp.place(relx=0.01, rely=0.36)

        Label(self.qd_tl_lt_pedido,text='Quantidade').place(relx=0.25, rely=0.25)
        self.ent_qtd_lp = Entry(self.qd_tl_lt_pedido, width=12)
        self.ent_qtd_lp.place(relx=0.25,rely=0.36)

        Label(self.qd_tl_lt_pedido, text='Preço').place(relx=0.5, rely=0.25)
        self.ent_preco_lp = Entry(self.qd_tl_lt_pedido, width=10)
        self.ent_preco_lp.place(relx=0.5,rely=0.36)

        # botões para lista de produtos
        self.bt_incluir_lp = Button(self.qd_tl_lt_pedido,text='Incluir',fg=bt_fg, bg=bt_bg, bd=1.5, command=self.adiciona_item_lp)
        self.bt_limpar_lp = Button(self.qd_tl_lt_pedido,text='Limpar',fg=bt_fg, bg='yellow', bd=1.5, command=self.limpa_ent_tl_pedido)
        self.bt_buscar_lp = Button(self.qd_tl_lt_pedido, text='Buscar',fg='white', bg='#3333FF', bd=1.5, command=self.chama_evento)

        self.bt_incluir_lp.place(relx=0.7, rely=0.45, width=bt_lar, height=bt_alt)
        self.bt_limpar_lp.place(relx=0.8, rely=0.45,width=bt_lar, height=bt_alt)
        self.bt_buscar_lp.place(relx=0.9, rely=0.45,width=bt_lar, height=bt_alt)


        #atualização dos dados para a combobox forma pagamento da tela lista do pedido
        self.conecta_bd()
        self.dados = self.cursor.execute(""" SELECT DISTINCT(forma_pagto) as forma_pagto FROM formas_pagto""")
        self.lista_combo_lp = [r for r, in self.dados]
        self.desconecta_bd()

        #cria combobox forma de pagamento para lista do pedido
        self.comb_frm_pagto_lp = ttk.Combobox(self.qd_tl_lt_pedido,width=17,values=self.lista_combo_lp)
        Label(self.qd_tl_lt_pedido,text='Forma de Pagto').place(relx=0.01, rely=0.6)
        self.comb_frm_pagto_lp.place(relx=0.01, rely=0.71)
        self.comb_frm_pagto_lp.insert(0,'DINHEIRO')

        # para salvar os itens na tabela movimento
        self.bt_salvar_lp = Button(self.qd_tl_lt_pedido,text='Salvar', bd=1.5, command=self.novo_movimento_lp) 
        self.bt_salvar_lp.place(relx=0.6, rely=0.71,width=bt_lar, height=bt_alt)
        
        # treeview para a lista do pedido
        self.barra_lt_ped = Scrollbar(self.qd_lt_pedido)

        self.lt_pedido = ttk.Treeview(self.qd_lt_pedido,
                            columns=('col1','col2','col3','col4','col5'),
                            yscrollcommand=self.barra_lt_ped.set, show='headings') #.set atribui a scroll à lista

        self.barra_lt_ped.config(command=self.lt_pedido.yview) #configura a barra de rolagem para a lista de peddido


        self.lt_pedido.heading('#0', text='')
        self.lt_pedido.heading('#1', text='Produto')
        self.lt_pedido.heading('#2', text='Quant.')
        self.lt_pedido.heading('#3', text='Preço')
        self.lt_pedido.heading('#4', text='Valor Total')
        self.lt_pedido.heading('#5', text='Código')

        self.lt_pedido.column('#0', width=1)
        self.lt_pedido.column('#1', width=300)
        self.lt_pedido.column('#2', width=20)
        self.lt_pedido.column('#3', width=20)
        self.lt_pedido.column('#4', width=20)
        self.lt_pedido.column('#5', width=20, anchor=CENTER)

        #empacotamento da lista e barra de rolagem
        self.lt_pedido.place(relwidth=0.96, relheight=0.95, relx=0.01, rely=0.03)

        self.barra_lt_ped.pack(side=RIGHT, fill=Y)

        #bind para chamar funcões:
        #busca a partir do cod barra ou cod produto com as teclas enter principal e enter do teclado numerico (KP_Enter)
        self.ent_cod_barra_lp.bind("<Return>",self.chama_cod_barra_lp) # cod barra apenas enter principal, o qual o leitor de cods o aciona
        self.ent_cod_lp.bind('<Return>',self.chama_cod_lp)
        self.ent_cod_lp.bind('<KP_Enter>',self.chama_cod_lp)
        #busca a partir da descrição do produto
        self.ent_produto_lp.bind('<Return>',self.tela_busca_lp)

        
        #remove item da lista
        self.lt_pedido.bind("<Double-1>", self.remove_item_lp) #chama a função remove_item para retirar produto da lista de pedido
        
        #limpa a lista de pedidos quando a janela da tela da lista é fechada
        self.tl_lt_pedido.protocol('WM_DELETE_WINDOW',self.lista_prod.clear())
    
    def tela_busca_lp(self,event):
        """tela para buscar os produtos cadastrados a partir da tela lista de pedido  """
        self.tl_bsc_lp = Toplevel(self.tl_lt_pedido)
        self.tl_bsc_lp.title('Buscar produto')
        self.tl_bsc_lp.geometry('700x650+400+30')
        self.tl_bsc_lp.resizable(False, False)

        """ quadro, lista e barra de rolagem"""
        self.qd_bsc_lp = Frame(self.tl_bsc_lp, highlightthickness=3)

        self.barra_lt_busca_lp = Scrollbar(self.qd_bsc_lp)

        self.lt_busca_lp = ttk.Treeview(self.qd_bsc_lp,columns=('col1','col2','col3','col4','col5','col6','col7'),
                        yscrollcommand=self.barra_lt_busca_lp.set, show='headings')

        self.barra_lt_busca_lp.config(command=self.lt_busca_lp.yview)

        self.lt_busca_lp.heading('#0', text='')
        self.lt_busca_lp.heading('#1', text='Produto')
        self.lt_busca_lp.heading('#2', text='Categoria')
        self.lt_busca_lp.heading('#3', text='Estoque')
        self.lt_busca_lp.heading('#4', text='Preço Venda')
        self.lt_busca_lp.heading('#5', text='Código')
        self.lt_busca_lp.heading('#6', text='Código Barras')
        self.lt_busca_lp.heading('#7', text='Ativo')

        self.lt_busca_lp.column('#0', width=1)
        self.lt_busca_lp.column('#1', width=200)
        self.lt_busca_lp.column('#2', width=100)
        self.lt_busca_lp.column('#3', width=30)
        self.lt_busca_lp.column('#4', width=30)
        self.lt_busca_lp.column('#5', width=30)
        self.lt_busca_lp.column('#6', width=30)
        self.lt_busca_lp.column('#7', width=10)

        #empacotamento quadro, lista e barra rolagem
        self.qd_bsc_lp.place(height=470, width=680, relx=0.01, rely=0.25)
        self.lt_busca_lp.place(relwidth=0.96, relheight=0.95, relx=0.01, rely=0.03)
        self.barra_lt_busca_lp.pack(side=RIGHT, fill=Y)
     
        self.busca_prod_lp()

        self.lt_busca_lp.focus(self.lt_busca_lp.get_children()[0]) # para selecionar o primeiro registro da lista, mas não está funcionando
        
        self.lt_busca_lp.bind('<Double-1>', self.selec_prod_lp)

Aplicativo()
