## netflix-spark

Este repositorio tem o conteudo e todas as dependencias para o funcionamento de um programa que processa dados de um CSV usando o Spark, armazenando o resultado em um Bucket. 

*Para armazenar as informacoes no bucket, e necessario ter as chaves privadas (e, consequentemente, permissoes de escrita), motivo pelo qual o trecho esta omitido.

Para suprir as dependencias do programa, incluiu-se dockerfiles e um arquivo orquestrador para que se tenha:

- uma instancia de Hadoop versao 3.2.1 para HDFS
- uma instancia de Spark versao 3.5.2 para modo master 
- uma instancia de Spark versao 3.5.2 para modo worker

Para que a execucao do programa tenha sucesso, e necessario construir/baixar as imagens docker dependencias (externas):

```shell
cd netflix-spark
docker compose up -d
```

Ao iniciar todas as dependencias em container, precisamos inicializar nosso filesystem e incluir o arquivo insumo do processamento (que ja e incluido como volume no container hadoop):

```shell
cd netflix-spark
docker exec hadoop sh -c "hdfs dfs -mkdir -p /user/hduser/data && hdfs dfs -put /csv/netflix_titles.csv /user/hduser/data" #compondo estrutura de diretorios e incluindo csv
#docker exec -it hadoop bash
#hdfs dfs -mkdir -p /user/hduser/data
#hdfs dfs -put /csv/netflix_titles.csv /user/hduser/data
```

Apos a inclusao do csv para processamento, podemos executar o programa que submete os jobs, sendo necessario criar um ambiente virtual Python e instalar as dependencias do projeto: 

```shell
cd netflix-spark
python -m venv netflix-spark-env
source netflix-spark-env/bin/activate.fish #ou arquivo activate com extensao do seu shell
pip install -r requirements.txt
```

Execute com:

```shell
python src/process_data.py
```

Interfaces Web:

- [localhost:9870](http://localhost:9870/) - Interface Web do namenode (Haddop)
- [spark-master:8080](http://spark-master:8080/) - Interface Web Master (Spark)
- [spark-master:8081](http://spark-master:8081/) - Interface Web Worker (Spark)