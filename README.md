# Maximização de Influência com AG

### Instalando as dependências:

```
pip install -r requirements.txt
```

### Informações sobre o conjunto de dados:

| Network          |    Type    | # Nodes |  # Edges  | Average degree | Density |
|------------------|:----------:|--------:|----------:|---------------:|--------:|
| karate           | undirected |      34 |        78 |        4.58824 | 0.13904 |
| mis              | undirected |      77 |       254 |        6.59740 | 0.08681 |
| soc-hamsterster  | undirected |    2000 |     16097 |       16.09700 | 0.00805 |
| CA-GrQc          | undirected |    4158 |     13422 |        6.45599 | 0.00155 |
| wiki-vote        |  directed  |    7066 |    103663 |       29.34135 | 0.00208 |
| CA-AstroPh       | undirected |   17903 |    196972 |       22.00436 | 0.00123 |
| CA-CondMat       | undirected |   21363 |     91286 |        8.54618 | 0.00040 |
| soc-epinions     |  directed  |   75877 |    508836 |       13.41213 | 0.00009 |
| soc-slashdot0902 |  directed  |   82168 |    870161 |       21.18005 | 0.00013 |

### Ordem de execução:
    1. preprocess.py
    2. calculate_centralities.py
    3. generate_seeds.py

#### **_1. preprocess.py_**

__Como executar__:

```
python preprocess.py -n <caminho_do_arquivo> -o <formato_de_saida>
```
 
1. Extrai a componente gigante da rede (GCC).

2. Remove arestas duplicadas e self-loops.

3. Particiona a GCC em comunidades.

4. Adiciona para cada vértice o atributo ```partition```, correspondente à sua respectiva comunidade.

5. Gera um arquivo no mesmo diretório da rede original (```.pkl``` ou ```.gml```).

__Obs:__
1. Para arquivos que não especificam a direção de arestas (edgelist), usar o parâmetro -d para redes direcionadas.

    Exemplo: ```python preprocess.py -n wiki-vote.edgelist -d```
     
2. Para redes em que a direção das arestas deve ser invertida, usar o parâmetro -r.
    
    Exemplo: ```python preprocess.py -n wiki-vote.edgelist -d -r``` 
3. O formato ```.pkl``` é um binário compactado enquanto que o ```.gml``` é texto puro. O formato padrão de saída é ```.pkl```.
Opcionalmente é possível definir o formato de saída para ```.gml``` usando a opção ```-o```.

    Exemplo:
        ```python preprocess.py -n karate.edgelist -o gml```

#### **_2. calculate_centralities.py_**

__Como executar__:

```
python calculate_centralities.py -n <caminho_do_arquivo>
```

- calcula as centralidades (degree, betweenness, pagerank, closeness, eigenvector, coreness)
- escala os valores das centralidades no intervalo ```(0, 1)```
- salva as centralidades obtidas (formato ```.pkl```) dentro do diretório ```centralities```


#### **_3. generate_seeds.py_**

__Como executar__:

```
python generate_seeds.py -n <caminho_do_arquivo>
```

- calcula as centralidades (degree, betweenness, pagerank, closeness, eigenvector, coreness)
- escala os valores de cada centralidade no intervalo [0, 1]
- salva as centralidades obtidas (pickle) dentro do diretório ```centralities```






