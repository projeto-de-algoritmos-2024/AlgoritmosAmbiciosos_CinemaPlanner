# Greed_CinemaPlanner

**Número da Lista**: 3<br>
**Conteúdo da Disciplina**: Algoritmos Ambiciosos<br>

## Alunos
|Matrícula | Aluno |
| -- | -- |
| 16/0007739  |  Guilherme Marques Rosa |

## Sobre 
O projeto é uma ferramenta de linha de comando que visa auxiliar no planejamento de horários de salas de cinema de acordo com os filmes em cartaz.

## Screenshots
**Vídeo da Execução**: [Acessar.](https://youtu.be/NlgDaX4ePLI)

## Instalação 
**Linguagem**: Python<br>
**TMDB Api**: O projeto utiliza a API do The Movies Database, então é necessário criar uma conta e um token de acesso de acordo com a [Documentação](https://developer.themoviedb.org/docs/getting-started)<br>

**Observação**: Ao criar uma aplicação na plataforma, não utilize a API Key, utilize o Acess Token JWT que é apresentado logo abaixo.

O gerenciador de projeto utilizado é o `poetry`.

Entre no diretório do projeto:
```bash
cd cinema-planner
```

Instale as dependências:
```bash
poetry install
```

Entre no shell do poetry:
```bash
poetry shell
```
## Uso 

Os passos de execução são:

- **Configurar o Token de Acesso**: `cinema config set-token`
- **Buscar a lista de filmes na API**: `cinema movies fetch`
- **Gerar os horários dos filmes**: `cinema movies schedule`
- **Gerar o plano de salar e exportar**: `cinema movies plan -o <caminho_de_saida.pdf>`

