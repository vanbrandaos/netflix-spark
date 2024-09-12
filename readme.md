## netflix-spark

Este repositório é um projeto com o objetivo de utilizar o Spark para processamentos de dados com *potencial* de BigData.

Idealmente, pensamos em trabalhar com uma experiencia de *batch*, onde há uma certa frequencia programada para execução dos **jobs**.

Em um fluxo de trabalho, tem-se, para ingestão de dados, a leitura do CSV com dados brutos armazenados no HDFS. Submete-se uma tarefa ao Spark que processa esses dados e condensa em formato conveniente, basicamente fazendo tarefas de agrupamento. O job usa da lib `gcs-connector-hadoop3`, um [conector do Google Cloud Storage](#https://cloud.google.com/dataproc/docs/concepts/connectors/cloud-storage?hl=pt-br), para armazenar diretamente na cloud os dados processados do catálogo.

Ao final, uma aplicação *web* está pronta para ler esses dados do *bucket* e organizar em um dashboard.

**Para armazenar as informacoes no bucket, e necessario ter as chaves privadas (e, consequentemente, permissoes de escrita), motivo pelo qual o trecho esta comentado e o diretorio de secrets omitido. Caso vá utilizar este projeto como base, lembre-se de inserir suas chaves da gcp no diretório `secrets`.*

```shell
mv [dir]/sa-private-key.json [project-dir]/secrets/spark-gcloud-key.json
chmod a+r spark-gcloud-key.json
```

### Infraestrutura e dependências do Projeto

As principais dependencias do projeto são o `Hadoop` e `Spark`. Para fácil solução, usamos essas ferramentas via Docker. O projeto tem um `docker-compose` que disponibiliza:

- 1 instância da aplicação *web* do projeto.
- 1 instância customizada do Hadoop versao 3.2.1 (somente para HDFS)
- 1 instância customizada do Spark versao 3.5.2 para modo master 
- 1 instância customizada do Spark versao 3.5.2 para modo worker


### Instruções para Execução

**Importante: execute todas as instruções da raiz do projeto**

Para que a execucao do programa tenha sucesso, e necessario construir/baixar as imagens docker dependencias (externas):

```shell
cd netflix-spark
docker compose up -d
```

Ao iniciar todas as dependencias em container, precisamos inicializar nosso filesystem e incluir o arquivo insumo do processamento (que ja e incluido como volume no container hadoop):

```shell
docker exec hadoop sh -c "hdfs dfs -mkdir -p /user/hduser/data && hdfs dfs -put /csv/netflix_titles.csv /user/hduser/data" 
```
**incluindo csv no HDFS a partir do diretorio volume.*

Após a inclusao do csv para processamento é possível submeter o job: 

```shell
docker exec spark-master spark-submit --master spark://spark-master:7077 /opt/bitnami/spark/jobs/netflix_catalog_processor.py
```
**O job é preparado como um volume no container master do Spark.*

## Interfaces Web:

- [localhost:9870](http://localhost:9870/) - Interface Web do namenode (Haddop)
- [localhost:8080](http://localhost:8080/) - Interface Web Master (Spark)
- [localhost:8081](http://localhost:8081/) - Interface Web Worker (Spark)
- [localhost:3000](http://localhost:3000/) - Aplicação Web (Dashboard)

## Desenvolvedores

- [Thiago Lofuto](#https://github.com/thiagolotufo)
- [Vanessa Brandão](#https://github.com/vanbrandaos)

## Referências

- https://cloud.google.com/dataproc/docs/concepts/connectors/cloud-storage?hl=pt-br
- https://medium.com/@guillermovc/setting-up-hadoop-with-docker-and-using-mapreduce-framework-c1cd125d4f7b
- https://spark.apache.org/docs/latest/configuration.html#runtime-environment
- https://github.com/GoogleCloudDataproc/hadoop-connectors/blob/master/gcs/INSTALL.md
