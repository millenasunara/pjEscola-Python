import os
import socketserver
from http.server import SimpleHTTPRequestHandler
import hashlib
from urllib.parse import parse_qs, urlparse
from database import conectar

conexao = conectar()
class MyHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try:
            f = open(os.path.join(path, 'cadastroAtividade.html'), 'r')
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f.read().encode('utf-8'))
            f.close()
            return None
        except FileNotFoundError:
            pass

        return super().list_directory(path)


    """def usuario_existente(self, login, senha):
        with open('dados.login.txt', 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    stored_login, stored_senha_hash, stored_nome = line.strip().split(';')
                    if login == stored_login:
                        senha_hash = hashlib.sha256(senha.encode('UTF-8')).hexdigest()
                        print("Achei o usuário")
                        return senha_hash == stored_senha_hash
        return False"""

    def usuario_existente(self, login, senha):
        print(login)
        print(senha)
        cursor = conexao.cursor()

        cursor.execute("SELECT senha FROM dados_login WHERE login = %s", (login,))
        resultado = cursor.fetchone()
        cursor.close()


        #cursor = conexao.cursor()

        print("Estou aqui")
        #cursor.execute("SELECT senha FROM dados_login WHERE login = %s", (login,))
        # cursor.execute("SELECT * FROM dados_login")
        #resultado = cursor.fetchone()
        # cursor.close()
        #resultado = ''
        print("Resultado usuario existente depois do close:", resultado)
        if resultado:
            #senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
            return True #senha_hash == resultado[0]

        return False

    def turma_existente(self, descricao):
        cursor = conexao.cursor()
        cursor.execute("SELECT descricao FROM turmas WHERE descricao = %s", (descricao,))
        resultado = cursor.fetchone()
        cursor.close()

        return resultado is not None

    def atividade_existente(self, codigo, descricao):
        cursor = conexao.cursor()
        cursor.execute("SELECT descricao FROM atividades WHERE id_atividade = %s AND descricao = %s", (codigo, descricao,))
        resultado = cursor.fetchone()
        cursor.close()

        return resultado is not None

    """def cadastrar_turma(self, descricao):
        print("Entrei no cadastrar turma")
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO turmas (descricao) VALUES (%s)", (descricao, ))
        print("Entrei no cadastrar turma2")
        conexao.commit()
        cursor.close()"""

    def cadastrar_atividade(self, codigo, descricao):
        print("Entrei no cadastrar atividade")
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO atividades (id_atividade, descricao) VALUES (%s, %s)", (codigo, descricao))
        print("Entrei no cadastrar atividade2")
        conexao.commit()
        cursor.close()

    def adicionar_usuario(self, login, senha, nome):
        cursor = conexao.cursor()
        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
        cursor.execute("INSERT INTO dados_login (login, senha, nome) VALUES (%s, %s, %s)", (login, senha_hash, nome))

        conexao.commit()
        cursor.close()

    def adicionar_turma_professor(self, descricao, id_professor):
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO turmas (descricao) VALUES (%s)", (descricao,))
        cursor.execute("SELECT id_turma FROM turmas WHERE descricao = %s", (descricao,))
        resultado = cursor.fetchone()
        cursor.execute("INSERT INTO turmas_professor (id_turma, id_professor) VALUES (%s, %s)", (resultado[0], id_professor))
        conexao.commit()
        cursor.close()

    def carrega_turmas_professor(self, login):
        cursor = conexao.cursor()
        cursor.execute("SELECT id_professor, nome FROM dados_login WHERE login = %s", (login,))
        resultado = cursor.fetchone()
        cursor.close()
        id_professor = resultado[0]
        print(f"carregar turmas professor{id_professor}")
        cursor = conexao.cursor()
        cursor.execute("SELECT turmas.id_turma, turmas.descricao FROM turmas_professor INNER JOIN turmas ON turmas_professor.id_turma = turmas.id_turma WHERE turmas_professor.id_professor = %s",(id_professor,))
        turmas = cursor.fetchall()
        cursor.close()

        linhas_tabela = ""
        for turma in turmas:
            id_turma = turma[0]
            descricao_turma = turma[1]
            link_atividade = "<img src='icnatividade2.png'/>"
            linha = "<tr><td style='text-align:center'>{}</td><td style='text-align:center'>{}</td></tr>".format(descricao_turma, link_atividade)
            linhas_tabela += linha

        with open(os.path.join(os.getcwd(), 'cadastroTurma.html'), 'r', encoding='utf-8') as cad_turma_file:
            content = cad_turma_file.read()
            print(f"Aquiiiiiii{id_professor}")

            content = content.replace('{nome_professor}', resultado[1])
            content = content.replace('{id_professor}', str(id_professor))
            content = content.replace('{login}', str(login))

        content = content.replace('<!--Tabela com linhas zebradas -->', linhas_tabela)
        self.send_response(200)
        self.send_header("Content-type","text/html; charset=utf-8")
        self.end_headers()

        self.wfile.write(content.encode('utf-8'))

    def remover_ultima_linha(self, arquivo):
        print("adicionar remover ultima linha")
        with open(arquivo, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        with open(arquivo, 'w', encoding='utf-8') as file:
            file.writelines(lines[:-1])


    def do_GET(self):
        if self.path == '/login2':
            print("getlogin")
            try:
                with open(os.path.join(os.getcwd(), 'login2.html'), 'r') as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_error(404, "File not Found")
        elif self.path == '/login_failed':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'login2.html'), 'r', encoding='utf-8') as login_file:
                content = login_file.read()
            mensagem = 'Login e/ou senha incorreta. Tente novamente.'
            content = content.replace('<!-- Mensagem de erro será inserida aqui -->',
                                      f'<div class="error-message">{mensagem}</div>')

        elif self.path.startswith('/cadastroTurma'):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)
            descricao = form_data.get('descricao', [''])[0]

            if self.turma_existente(descricao):
                self.send_response(302)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.send_header('Location', '/turma_existente.html')
                self.end_headers()
                return

            self.cadastrar_turma(descricao)
            self.send_response(302)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header('Location', '/sucesso_cadastro_turma.html')
            self.end_headers()

        elif self.path.startswith('/cadastroAtividade'):
            print("cadastroAtividade")
            try:
                with open(os.path.join(os.getcwd(), 'cadastroAtividade.html'), 'r') as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_error(404, "File not Found")


        elif self.path.startswith('/cadastro'):
                print("cadastro de usuário")
                query_params = parse_qs(urlparse(self.path).query)
                login = query_params.get('login', [''])[0]
                senha = query_params.get('senha', [''])[0]

                welcome_message = f'Olá {login}, seja bem-vindo! Percebemos que você é novo por aqui. Complete seu cadastro'

                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()

                with open(os.path.join(os.getcwd(), 'cadastro.html'), 'r', encoding='utf-8') as cadastroUser_file:
                    content = cadastroUser_file.read()

                content = content.replace('{login}', login)
                content = content.replace('{senha}', senha)
                content = content.replace('{welcome_message}', welcome_message)

                self.wfile.write(content.encode('utf-8'))

                return

        else:
            super().do_GET()


    def do_POST(self):
        if self.path == '/enviar_login2':
            content_length = int(self.headers['content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            login = form_data.get('email', [''])[0]
            senha = form_data.get('senha', [''])[0]

            #print(f'loginUsuário existente {login}{senha}')

            if self.usuario_existente(login, senha):

                self.carrega_turmas_professor(login)

                print("Estou no if")
                #print(f'loginUsuário existente {login}{senha}')
                # self.send_response(200)
                # self.send_header("Content-type", "text/html; charset=utf-8")
                # self.end_headers()
                #
                # with open(os.path.join(os.getcwd(), 'cadastroTurma.html'), 'r', encoding='utf-8') as cadastro_file:
                #     content = cadastro_file.read()
                #
                # self.wfile.write(content.encode('utf-8'))
                print("Entrei aqui")
            else:
                print("Estou no else")
                #Verifica se usuario ja esta cadastrado. Caso não esteja foi caso de login errado
                cursor = conexao.cursor()
                cursor.execute("SELECT login FROM dados_login WHERE login = %s", (login,))
                resultado = cursor.fetchone()
                cursor.close()
                if resultado:
                    self.send_response(302)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Location', '/login_failed')
                    self.end_headers()
                    return
                else:
                    #self.adicionar_usuario(login, senha, nome='None')
                    self.send_response(302)
                    self.send_header('Location', f'/cadastro.html?login={login}&senha={senha}')
                    self.end_headers()
                    return

        elif self.path.startswith('/confirmar_cadastroAtividade'):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            descricao = form_data.get('descricao', [''])[0]
            codigo = form_data.get('codigo', [''])[0]

            print(f'{descricao}{codigo}')

            self.cadastrar_atividade(codigo, descricao)
            if self.atividade_existente(codigo, descricao):
                print("Estou no if de atividade existente")
                # print(f'loginUsuário existente {login}{senha}')
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()

                with open(os.path.join(os.getcwd(), 'sucessoAtividade.html'), 'r',
                          encoding='utf-8') as cadastro_file:
                    content = cadastro_file.read()

                self.wfile.write(content.encode('utf-8'))
                print("Entrei aqui atividade")
            else:
                print("Estou no else de cadastro de atividade existente")
                # Verifica se usuario ja esta cadastrado. Caso não esteja foi caso de login errado
                cursor = conexao.cursor()
                cursor.execute("SELECT id_atividade FROM atividades WHERE descricao = %s", (descricao,))
                resultado = cursor.fetchone()
                cursor.close()
                if resultado:
                    self.send_response(302)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Location', '/login_failed')
                    self.end_headers()
                    return

                else:
                    self.send_response(302)
                    self.send_header('Location', f'/sucessoAtividade.html')
                    self.end_headers()
                    return

        elif self.path.startswith('/cadastroTurma'):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            descricao = form_data.get('descricao', [''])[0]
            id_professor = form_data.get('id_professor', [''])[0]
            login = form_data.get('login',[''])[0]

            print(f">>>>>>>Cad_turma, dados do formulário {descricao}{id_professor}{login}")

            #self.cadastrar_turma(descricao)
            print(f"Cadastrar turma {descricao}")

            if self.turma_existente(descricao):

                print("Estou no if de turma existente")
                # print(f'loginUsuário existente {login}{senha}')
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()

                with open(os.path.join(os.getcwd(), 'sucesso_cadastro_turma.html'), 'r', encoding='utf-8') as cadastro_file:
                    content = cadastro_file.read()

                self.wfile.write(content.encode('utf-8'))
                print("Entrei aqui")
            else:
                self.adicionar_turma_professor(descricao, id_professor)
                #self.carrega_turmas_professor(login)
                print(f"adicionar turma_professir{descricao}{id_professor}")
                print(f"{login}")
                print("Estou no else de cadastro de turma existente")
                #Verifica se usuario ja esta cadastrado. Caso não esteja foi caso de login errado
                cursor = conexao.cursor()
                cursor.execute("SELECT id_turma FROM turmas WHERE descricao = %s", (descricao,))
                resultado = cursor.fetchone()
                cursor.close()
                if resultado:
                    self.send_response(302)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Location', 'sucesso_cadastro_turma.html')
                    self.end_headers()
                    return

                else:
                    self.send_response(302)
                    self.send_header('Location', '/login_failed')
                    self.end_headers()
                    return

            """self.send_response(302)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header('Location', '/sucesso_cadastro_turma.html')
            self.end_headers()"""

        elif self.path.startswith('/confirmar_cadastro'):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            login = form_data.get('email', [''])[0]
            senha = form_data.get('senha', [''])[0]
            nome = form_data.get('nome', [''])[0]

            #chamo a funcao de adicionar usuario
            self.adicionar_usuario(login, senha, nome)


            """senha_hash = hashlib.sha256(senha.encode('UTF-8')).hexdigest()"""

            """if self.usuario_existente(login, senha):
                with open('dados.login.txt', 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                with open('dados.login.txt', 'w', encoding='utf-8') as file:
                    for line in lines:
                        stored_login, stored_senha, stored_nome = line.strip().split(';')
                        if login == stored_login and senha_hash == stored_senha:
                            line = f"{login};{senha_hash};{nome}\n"
                        file.write(line)"""
            # imprimo que o registro foi armazenado com sucesso
            self.send_response(302)
            self.send_header('Location', '/login2.html')
            self.end_headers()
            """else:
                self.remover_ultima_linha('dados.login.txt')
                self.send_response(302)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write("A senha não confere. Retome o procedimento".encode('utf-8'))"""


        else:
            super(MyHandler, self).do_POST()

endereco_ip = "0.0.0.0"
porta = 8000

with socketserver.TCPServer((endereco_ip, porta), MyHandler) as httpd:
    print(f"Servidor iniciando em http://localhost:{porta}")
    httpd.serve_forever()

