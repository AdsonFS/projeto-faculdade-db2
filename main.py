from pymongo import MongoClient
import random

class MongoCRUD:
    def __init__(self, db_name, collection_name, uri="mongodb://localhost:27017"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def create(self, data):
        return self.collection.insert_one(data).inserted_id

    def read(self, query=None):
        if query is None:
            query = {}
        return list(self.collection.find(query))

    def update(self, query, new_values):
        return self.collection.update_many(query, {"$set": new_values}).modified_count

    def delete(self, query):
        return self.collection.delete_many(query).deleted_count

class Torneio:
    def __init__(self, nome, crud):
        self.nome = nome
        self.crud = crud
        self.torneio_data = {"nome": self.nome, "jogadores": [], "partidas": []}
        self.crud.create(self.torneio_data)

    def adicionar_jogador(self, nome):
        jogador = {"nome": nome, "pontuacao": 0}
        self.torneio_data["jogadores"].append(jogador)
        self.atualizar_torneio()

    def gerar_emparceiramentos(self):
        jogadores = self.torneio_data["jogadores"]
        random.shuffle(jogadores)
        emparceiramentos = []
        for i in range(0, len(jogadores), 2):
            if i + 1 < len(jogadores):
                partida = {
                    "jogador1": jogadores[i]["nome"],
                    "jogador2": jogadores[i + 1]["nome"],
                    "resultado": None
                }
                emparceiramentos.append(partida)
        self.torneio_data["partidas"].extend(emparceiramentos)
        self.atualizar_torneio()

    def registrar_resultado(self, jogador1, jogador2, resultado):
        for partida in self.torneio_data["partidas"]:
            if partida["jogador1"] == jogador1 and partida["jogador2"] == jogador2:
                partida["resultado"] = resultado
                if resultado == "jogador1":
                    self.atualizar_pontuacao(jogador1, 1)
                elif resultado == "jogador2":
                    self.atualizar_pontuacao(jogador2, 1)
                elif resultado == "empate":
                    self.atualizar_pontuacao(jogador1, 0.5)
                    self.atualizar_pontuacao(jogador2, 0.5)
                break
        self.atualizar_torneio()

    def atualizar_pontuacao(self, jogador, pontos):
        for j in self.torneio_data["jogadores"]:
            if j["nome"] == jogador:
                j["pontuacao"] += pontos

    def atualizar_torneio(self):
        self.crud.update({"nome": self.nome}, self.torneio_data)

    def obter_estado_torneio(self):
        estado = self.crud.read({"nome": self.nome})[0]
        print("Estado atual do torneio:")
        print(f"Jogadores:")
        for jogador in estado["jogadores"]:
            print(f"{jogador['nome']}: {jogador['pontuacao']}")
        print("\nPartidas:")
        for partida in estado["partidas"]:
            print(f"{partida['jogador1']} x {partida['jogador2']}: {partida['resultado']}")
    
    def iniciar_torneio(self):
        self.crud.delete({"nome": self.nome})
        self.torneio_data = {"nome": self.nome, "jogadores": [], "partidas": []}
        self.crud.create(self.torneio_data)

# Exemplo de uso
crud = MongoCRUD("torneios_db", "torneios")
torneio = Torneio("Torneio Xadrez", crud)

while True:
    print("\033c")
    print("\nMenu do Torneio de Xadrez")
    print("1. Iniciar novo torneio")        # delete + create
    print("2. Adicionar jogadores")         # update
    print("3. Gerar emparceiramentos")      # update
    print("4. Registrar resultado")         # update
    print("5. Exibir estado do torneio")    # read
    print("6. Sair")

    opcao = input("Escolha uma opcao: ")

    if opcao == "1":
        torneio.iniciar_torneio()
        print("Torneio iniciado com sucesso.")

    elif opcao == "2":
        nome_jogadores = input("Digite o nome dos jogadores: ")
        for nome_jogador in nome_jogadores.split(","):
            torneio.adicionar_jogador(nome_jogador)
        print(f"Jogadores adicionados com sucesso.")

    elif opcao == "3":
        torneio.gerar_emparceiramentos()
        print("Emparceiramentos gerados com sucesso.")

    elif opcao == "4":
        jogador1 = input("Digite o nome do jogador 1: ")
        jogador2 = input("Digite o nome do jogador 2: ")
        resultado = input("Digite o resultado (jogador1, jogador2, empate): ")
        torneio.registrar_resultado(jogador1, jogador2, resultado)
        print("Resultado registrado com sucesso.")

    elif opcao == "5":
        estado = torneio.obter_estado_torneio()

    elif opcao == "6":
        print("Saindo do programa.")
        break

    else:
        print("Opcao invalida. Tente novamente.")

    print("\n" + "-"*30 + "\n\n")
    input("Pressione Enter para continuar...")

