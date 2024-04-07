import mysql.connector
import pandas as pd
from datetime import datetime
from datetime import date

#estabelecendo conexão com servidor do banco de dados, é interessante usar como função para usar depois denovo
try:
    conexão = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        passwd=''
                    )
    print("Sucesso na conexão com o servidor")
except:
    print(f"Erro na conexão com o servidor")
#função para usar o banco
def use_bd(nomebd):
        cursor = conexão.cursor()
        try:
            cursor.execute(f'use {nomebd}')
            print(f"Usando banco {nomebd}...")
            cria_tabelas()
        except:
            print(f"Erro ao tentar usar o banco")
            cria_bd(nomebd)
#função para criar banco de dados caso ela não exista

def cria_bd(nomebd):
        cursor = conexão.cursor()
        try:
            cursor.execute(f'create database if not exists {nomebd}')
            print(f'Criado banco {nomebd}')
            use_bd(nomebd)
        except:
            print('Erro na criação do banco')

#função para criar tabela caso ela não exista
def cria_tabelas():
        cursor = conexão.cursor()
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS tb_pessoa (cpf_pessoa VARCHAR(15) UNIQUE NOT NULL, nome VARCHAR(100) UNIQUE NOT NULL, data_nascimento DATE, sexo ENUM('m','f'), usuario VARCHAR(15) NOT NULL UNIQUE, senha VARCHAR(10) NOT NULL, PRIMARY KEY(cpf_pessoa));")

            cursor.execute("CREATE TABLE IF NOT EXISTS tb_endereco(cod_endereco INT NOT NULL AUTO_INCREMENT, país VARCHAR(10) NOT NULL, cidade VARCHAR(10) NOT NULL, rua VARCHAR(20) NOT NULL, numero INT NOT NULL, complemento VARCHAR(10), codigo_pessoa VARCHAR(15) UNIQUE NOT NULL, PRIMARY KEY(cod_endereco), FOREIGN KEY (codigo_pessoa) REFERENCES tb_pessoa(cpf_pessoa) ON DELETE RESTRICT);")

            cursor.execute("CREATE TABLE IF NOT EXISTS tb_telefone(cod_telefone INT NOT NULL AUTO_INCREMENT UNIQUE, numero VARCHAR(20) NOT NULL, codigo_pessoa VARCHAR(15) NOT NULL, PRIMARY KEY(cod_telefone), FOREIGN KEY(codigo_pessoa) REFERENCES tb_pessoa(cpf_pessoa) ON DELETE RESTRICT);")

            cursor.execute("CREATE TABLE IF NOT EXISTS tb_func(codigo_pessoa VARCHAR(15) UNIQUE NOT NULL, tipo_func VARCHAR(15) NOT NULL, pis_pasep VARCHAR(15) UNIQUE NOT NULL, PRIMARY KEY(codigo_pessoa), FOREIGN KEY(codigo_pessoa) REFERENCES tb_pessoa(cpf_pessoa) ON DELETE RESTRICT);")

            cursor.execute("CREATE TABLE IF NOT EXISTS tb_cliente(codigo_pessoa VARCHAR(15) UNIQUE NOT NULL, cartao_credito VARCHAR(15) UNIQUE NOT NULL, PRIMARY KEY(codigo_pessoa), FOREIGN KEY(codigo_pessoa) REFERENCES tb_pessoa(cpf_pessoa) ON DELETE RESTRICT);")

            cursor.execute("CREATE TABLE IF NOT EXISTS tb_quarto(cod_quarto INT NOT NULL AUTO_INCREMENT UNIQUE, estado ENUM('disponível','indisponível') NOT NULL, capacidade INT NOT NULL, preco FLOAT NOT NULL, PRIMARY KEY(cod_quarto), INDEX idx_estado (estado));")

            cursor.execute("CREATE TABLE IF NOT EXISTS tb_reserva(cod_reserva INT NOT NULL UNIQUE AUTO_INCREMENT, check_in DATE NOT NULL, check_out DATE NOT NULL, codigo_cliente VARCHAR(15) NOT NULL, codigo_quarto INT NOT NULL, PRIMARY KEY(cod_reserva), Foreign Key(codigo_quarto)REFERENCES tb_quarto(cod_quarto) ON DELETE RESTRICT, FOREIGN KEY(codigo_cliente) REFERENCES tb_cliente(codigo_pessoa) ON DELETE RESTRICT, INDEX idx_cliente_check (codigo_cliente, check_out, check_in));")

            cursor.execute("CREATE TABLE IF NOT EXISTS tb_reserva_func(codigo_reserva INT NOT NULL, codigo_func VARCHAR(15) NOT NULL, PRIMARY KEY(codigo_reserva, codigo_func), FOREIGN KEY(codigo_reserva) REFERENCES tb_reserva(cod_reserva) ON DELETE RESTRICT, FOREIGN KEY(codigo_func) REFERENCES tb_func(codigo_pessoa) ON DELETE RESTRICT);")

            cursor.execute("CREATE TABLE IF NOT EXISTS tb_servico(cod_servico INT NOT NULL AUTO_INCREMENT UNIQUE, nome VARCHAR(10) NOT NULL, preco INT NOT NULL, PRIMARY KEY(cod_servico));")

            cursor.execute("CREATE TABLE IF NOT EXISTS tb_servico_quarto(codigo_servico INT NOT NULL, codigo_quarto INT NOT NULL, PRIMARY KEY(codigo_quarto, codigo_servico), FOREIGN KEY (codigo_servico) REFERENCES tb_servico(cod_servico) ON DELETE RESTRICT, FOREIGN KEY (codigo_quarto) REFERENCES tb_quarto(cod_quarto) ON DELETE RESTRICT);")

            cursor.execute("CREATE TABLE IF NOT EXISTS tb_pagamento(cod_pagamento INT NOT NULL AUTO_INCREMENT UNIQUE, metodo ENUM('pix', 'debito', 'credito', 'boleto', 'cedula') NOT NULL, data DATE NOT NULL, codigo_reserva INT NOT NULL, preco_total INT NOT NULL, PRIMARY KEY(cod_pagamento), FOREIGN KEY (codigo_reserva) REFERENCES tb_reserva(cod_reserva) ON DELETE RESTRICT);")

            cursor.execute("CREATE TABLE IF NOT EXISTS tb_avaliacao(cod_avaliacao INT NOT NULL AUTO_INCREMENT UNIQUE, classificacao ENUM('ruim', 'bom', 'ótimo') NOT NULL, comentario TEXT, codigo_reserva INT NOT NULL, PRIMARY KEY(cod_avaliacao), FOREIGN KEY (codigo_reserva) REFERENCES tb_reserva(cod_reserva) ON DELETE RESTRICT);")     
        except:
            print("Erro ao tentar criar tabela.")

# função para inserir dados no banco
def add_cliente(cpf,nome,data_nasc,sexo,usuário,senha, cartao):
    cursor =  conexão.cursor()
    try:
        cursor.execute(f'insert into tb_pessoa values ("{cpf}","{nome}","{data_nasc}","{sexo[0]}","{usuário}","{senha}")')
        cursor.execute(f'insert into tb_cliente values ("{cpf}","{cartao}")')
        conexão.commit()
    except:
          print("Erro ao inserir os dados")
          

def add_tel(telefone, cpf):
        try:
            cursor = conexão.cursor()
            cursor.execute(f'insert into tb_telefone values (default,"{telefone}", "{cpf}")')
        except:
            print("Erro ao inserir telefone")

def add_endereco(país, cidade, rua,numero, complemento,cpf):
        cursor = conexão.cursor()
        try:
            cursor.execute(f'insert into tb_endereco values (default,"{país}","{cidade}","{rua}","{numero}","{complemento}","{cpf}")')
        except:
             print("Erro ao inserir endereço")

def login(usu,senha):
    cursor=conexão.cursor()
    try:
        cursor.execute(f'select tb_pessoa.usuario, tb_pessoa.senha from tb_pessoa join tb_cliente on cpf_pessoa = codigo_pessoa')
        tabela_cliente = cursor.fetchall()
        for e in tabela_cliente:
             if usu == e[0] and senha == e[1]:
                return True, "Cliente"
        
        cursor.execute(f'select tb_pessoa.usuario, tb_pessoa.senha from tb_pessoa join tb_func on cpf_pessoa = codigo_pessoa')
        tabela_func = cursor.fetchall()
        for i in tabela_func:
             if usu == e[0] and senha == e[1]:
                return True, "Funcionário"
             
        return False, "Não Encontrado"
             
    except:
        print("Erro")
     

def mostrar_quarto():
    cursor=conexão.cursor()
    query = """
        SELECT 
            q.cod_quarto, 
            q.capacidade, 
            q.estado,
            q.preco
            
        FROM 
            tb_quarto q
        WHERE 
            estado = 'disponível'
    """
    try:
        cursor.execute(query)

        # Buscar os resultados e criar um DataFrame
        tabela_quartos = cursor.fetchall()
        resultado = pd.DataFrame(data=tabela_quartos, columns=["ID", "CAPACIDADE", "ESTADO", "PREÇO"])

        # Exibir o DataFrame
        print(resultado.to_string(index=False))

    except:
        print("Erro ao mostrar tabela")

#mostrar quartos disponíveis e seus serviços adicionais
def mostrar_quarto_serviço():
    cursor=conexão.cursor()
    query = """
      SELECT 
            q.cod_quarto, 
            q.capacidade, 
            q.estado,
            q.preco,
			(SELECT GROUP_CONCAT(nome SEPARATOR ', ')
		 FROM tb_servico
		 WHERE cod_servico IN (SELECT codigo_servico 
							   FROM tb_servico_quarto 
							   WHERE codigo_quarto = q.cod_quarto)) AS serviços
        FROM 
            tb_quarto q
        WHERE 
            estado = 'disponível' and q.cod_quarto in (select sq.codigo_quarto from tb_servico_quarto sq where sq.codigo_servico in (select s.cod_servico from tb_servico s)) """
    try:
        cursor.execute(query)

        # Buscar os resultados e criar um DataFrame
        tabela_quartos_serviço = cursor.fetchall()
        resultado = pd.DataFrame(data=tabela_quartos_serviço, columns=["ID", "CAPACIDADE", "ESTADO", "PREÇO","SERVIÇOS"])

        # Exibir o DataFrame
        print(resultado.to_string(index=False))

    except:
        print("Erro ao mostrar tabela")

def fazer_reserva(quarto, cpf, checkin, checkout):
    
    cursor=conexão.cursor()
    query = """
        SELECT 
            q.cod_quarto    
        FROM 
            tb_quarto q
        WHERE 
            estado = 'disponível'
    """
  
    try:
        cursor.execute(query)

        # Buscar os resultados e criar um DataFrame
        tabela_quar = cursor.fetchall()
        disponível =  False
        for c in tabela_quar:
                if c[0]==quarto:
                    disponível = True
                    break
        if disponível == False or checkin>checkout or checkin<date.today():
            print("Quarto indisponível para reserva")
        else:
            cursor.execute(f"select r.check_in, r.check_out from tb_reserva r where r.codigo_quarto = {quarto}")
            dt_quartos = cursor.fetchall()
            pode = True
            for e in dt_quartos:
                if checkin <= e[1] and checkin >= e[0]:
                    pode = False
                if checkout <= e[1] and checkout >= e[0]:
                    pode = False
                
            if pode == True:
                cursor.execute(f'INSERT INTO tb_reserva VALUES (default,"{checkin}","{checkout}","{cpf}","{quarto}")')
                conexão.commit()
            else:
                 print("Esse quarto está reservado durante esse período")
    except:
         print("Erro")
    

def hist_reserva(cpf):
    
    cursor =  conexão.cursor()
    try:
        cursor.execute(f'SELECT r.cod_reserva, r.check_in, r.check_out, q.cod_quarto, q.capacidade, q.preco, r.codigo_cliente FROM tb_reserva r JOIN tb_quarto q ON r.codigo_quarto = q.cod_quarto where r.codigo_cliente = "{cpf}"')
        hist = cursor.fetchall()
        resultado = pd.DataFrame(data=hist, columns=["Nº RESERVA", "CHECKIN", "CHECKOUT", "ID QUARTO","CAPACIDADE","PREÇO","CPF"])
        print(resultado.to_string(index=False))
    except:
        print("ERRO para mostrar histórico")

def atualiza_tel(cpf,telefone):
        cursor = conexão.cursor()
        cursor.execute(f'update tb_telefone set numero= "{telefone}" where codigo_pessoa = {cpf}')
        conexão.commit()

def atualiza_end(cpf,país, cidade, rua,numero, complemento):
        cursor = conexão.cursor()
        cursor.execute(f'update tb_endereco set país= "{país}", cidade= "{cidade}", rua= "{rua}", numero= "{numero}", complemento="{complemento}" where codigo_pessoa = {cpf}')
        conexão.commit()

def avaliar_reserva(classificação,comentário,reserva):
    cursor =  conexão.cursor()
    try:
        cursor.execute(f'select r.cod_reserva from tb_reserva r')
        reservas = cursor.fetchall()
        existe = False
        for r in reservas:
                if reserva == r[0]:
                    existe = True
                    break
        if existe == False:
            print("Reserva não encontrada")
        else:
            cursor.execute(f'INSERT INTO tb_avaliacao VALUES (default,"{classificação}","{comentário}","{reserva}")') 
            conexão.commit()
    except:
         print("ERRO ao fazer avaliação")

def remove_reserva(reserva, cpf):
    cursor = conexão.cursor()
    try:
        cursor.execute(f'select r.cod_reserva, r.check_in, r.check_out from tb_reserva r where r.codigo_cliente = "{cpf}"')
        reservas = cursor.fetchall()
        data_atual = date.today()
        for e in reservas:
            if(int(e[0])==reserva):
                if e[1] <= data_atual and e[2] >=data_atual:
                    print("não pode excluir reserva em andamento")
                else:
                    cursor.execute(f'DELETE FROM tb_reserva WHERE tb_reserva.cod_reserva = "{int(e[0])}"')
                    conexão.commit()
                    print("Reserva excluída")
    except:
          print('Erro ao tentar deletar a reserva.')

def atualiza_cliente(cpf,nome,data_nasc,sexo,usuário,senha, cartao):
    cursor =  conexão.cursor()
    try:
        cursor.execute(f'update tb_cliente set cartao_credito = "{cartao}" where codigo_pessoa = {cpf}')
        conexão.commit()
        cursor.execute(f'update tb_pessoa set nome = "{nome}", data_nascimento= "{data_nasc}", sexo= "{sexo}",usuario= "{usuário}", senha="{senha}" where cpf_pessoa = {cpf}')
        conexão.commit()
        
    except:
          print("Erro ao atualizar os dados")

def reservas_quarto(quarto):
    cursor =  conexão.cursor()
    try:
        cursor.execute(f'select r.cod_reserva, r.check_in, r.check_out from tb_reserva r where r.codigo_quarto = "{quarto}" order by r.check_in limit 10')
        r_quarto = cursor.fetchall()
        resultado = pd.DataFrame(data=r_quarto, columns=["Nº RESERVA", "CHECKIN", "CHECKOUT"])
        print(resultado.to_string(index=False))
    except:
        print("ERRO ao mostrar reservas do quarto")
#código a ser executado
use_bd("projeto_hotel")

print("=-=-"*10)
print("Sistema Hotel")
print("=-=-"*10)
while True:
     print("\nMENU INICIAL")
     print("1- Fazer login")
     print("2- Cadastrar hóspede")
     print("3- Sair")
     escolha = int(input("Digite sua escolha:"))
     if escolha == 3:
        conexão.close()
        print("Finalizado sistema!")
        break
     elif escolha == 2:
          cpf_cliente = input("cpf: ")
          add_cliente(cpf_cliente,input("nome: "),datetime.strptime(input("data nascimento: "), '%Y-%m-%d').date(),input("sexo: "), input("usuário: "), input("senha: "), input("cartão crédito: "))
          esc_end = input("Deseja adicionar endereço?[s/n]")
          if esc_end[0] == "s":
                add_endereco(cpf_cliente,input("país: "), input("cidade: "), input("rua: "), int(input("número: ")),input("complemento: "))
          esc_tel =  input("Deseja adicionar telefone?[s/n]")
          if esc_tel[0] == "s":
                add_tel(cpf_cliente, input("número telefone: "))
     elif escolha == 1:
          resultado, tipo = login(input("Usuário: "),input("Senha: "))
          if resultado == True and tipo=="Cliente":
               print("logando cliente...")
               while True:
                    print("\nMENU CLIENTE")
                    print("\n1-Quartos disponíveis\n2-Histórico de reservas\n3-Atualizar Cadastro\n4-Logoff")
                    escolha_cliente = int(input("Digite sua escolha: "))
                    if escolha_cliente == 1:
                         mostrar_quarto()
                         while True:
                            print("\n1-mostrar quartos com serviços adicionais\n2-fazer uma reserva\n3-ver reservas de um quarto\n4-voltar")
                            escolha_quarto = int(input("Digite sua escolha: "))
                            if escolha_quarto == 1:
                                mostrar_quarto_serviço()
                            elif escolha_quarto == 2:
                                fazer_reserva(int(input("Id quarto: ")), input("Cpf: "), datetime.strptime(input("Data checkin: "), '%Y-%m-%d').date(), datetime.strptime(input("Data checkout: "), '%Y-%m-%d').date())
                            elif escolha_quarto == 3:
                                reservas_quarto(int(input("Id Quarto:")))
                            elif escolha_quarto == 4:
                                break
                            else:
                                print("Opção inválida")
                    elif escolha_cliente == 2:
                         hist_reserva(input("Cpf: "))
                         while True:
                              print("\n1-Avaliar reserva\n2-Remover reserva\n3-Voltar")
                              resultado_hist = int(input("Digite sua escolha: "))
                              if resultado_hist == 1:
                                   avaliar_reserva(input("Classificação: "),input("Comentário: "),int(input("Nº reserva: ")))
                              elif resultado_hist == 2:
                                   remove_reserva(int(input("Id reserva: ")), input("Cpf: "))
                              elif resultado_hist == 3:
                                   break
                              else:
                                   print("Opção inválida")
                    elif escolha_cliente == 3:
                         print("Antes de atualizar o cadastro confirme seu cpf")
                         cpf = input("cpf: ") 
                         print("\nATUALIZAÇÃO")
                         atualiza_cliente(cpf,input("novo nome: "),datetime.strptime(input("nova data nascimento: "), '%Y-%m-%d').date(),input("novo sexo: "), input("novo usuário: "), input("nova senha: "),input("novo cartão crédito: "))
                         esc_end = input("Deseja atualizar endereço? [s/n]")
                         if esc_end[0]=="s":
                              atualiza_end(cpf, input("novo país: "), input("nova cidade: "), input("nova rua: "), int(input("novo número: ")),input("novo complemento: "))
                         esc_tel = input("Deseja atualizar telefone?[s/n]")
                         if esc_tel[0]=="s":
                              atualiza_tel(cpf,input("novo número telefone: "))
                    elif escolha_cliente == 4:
                         print("deslogando...")
                         break
                    else:
                         print("Erro foi digitado uma opção inválida")
          elif resultado == True and tipo=="Funcionário":
               print("logando funcionário...")
               #aqui menus que o funcionário terá acessoa como adiciona,deletar, atualizar, consultar (reserva,quarto,func,cliente,serviço)
          else:
               print("Senha ou usuário incorretos.")
     else:
          print("Opção inválida digitada.")
     

