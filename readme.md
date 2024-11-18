座学テキストは[コチラ](./VectorEssestials.pdf)

# CosmosDBでのベクトル検索 実践編 <BR> (Azure Cosmos DB for NoSQL)

  ## Cosmos DB for NoSQLのベクトルデータの取り扱い

- ベクトルデータ関連機能
  - ベクトルインデックス
    - ベクトルインデックスがある場合、ベクトルデータの検索が高速になる。
    - ベクトルインデックスがなければ全検索(ブルートフォース)で検索する。
  - ベクトルインデックスの種類  
    - Flat
    - Quantized Flat
    - DiskANNl

  - ベクトルインデックスの作成
    - インデックスポリシー
    - ベクトル埋め込みポリシー

  - ベクトル検索クエリの発行
    - SQLライククエリで実現
      - 検索対象のベクトル配列と、データの中でベクトルインデックスがはられている項目名を指定する
      - TOP Nで上位いくつまでを指定
    ```SQL
    SELECT TOP 2 c.id, c.name, c.num, 
    VectorDistance(c.vectors, @vector) AS similarity,
    c.text
    FROM c
    ORDER BY VectorDistance(c.vectors, @vector)
    ```

    `VectorDistance(比較先ベクトル項目(N件),比較元ベクトル(1件))`

- Cosmos DB for NoSQLでベクトル検索を使うための準備



- CosmosDB for NoSQLでのベクトルデータの管理
  1. コンテナーに対してベクトルインデックスを設定する
    - *ベクトル関連設定はコンテナー作成時のみ*なので注意
  3. テキストデータを準備する
  4. テキスト部分をEmbedding APIを適用してベクトルに変換する
  5. 変換したデータをベクトルとしてMongoDB vCoreに登録する

- ベクトル検索の実施
  1. 検索対象となるテキストを得る
  1. テキストをEmbedding APIを適用してベクトルに変換する
  1. 変換したベクトルとパラメータを設定して検索する

### ベクトルデータの格納

- 環境準備
  - Azure OpenAI Serviceの準備
    - `text-embedding-ada-002`をデプロイしておく(可能であればデプロイ名は"embedding01"に)
    <IMG SRC="https://github.com/tahayaka-microsoft/CosmosDB_Vectors/assets/OpenAI_Embedding_Deploy.png" width=400>
    
    - Azure OpenAI Serviceの"キーとエンドポイント"から`キー1`と`エンドポイント`の値を控えておく
    <IMG SRC="https://github.com/tahayaka-microsoft/CosmosDB_Vectors/assets/OpenAI_Keys.png" width=400>
    
  - Pythonライブラリの導入
    - `azure-cosmos`,`openai`,`langchain`を必要に応じて`pip install`を用いてインストールする
    - IDE(VSCode,Spyder,Jupyter)を利用する場合は`nest_asyncio`をインストールする
  - テストデータのダウンロードと解凍
    - 任意の場所にて以下を実行する
      ```sh
      wget https://github.com/tahayaka-microsoft/CosmosDB_Vectors_NoSQL/raw/main/assets/test1000.tar
      tar -xvf test1000.tar
      ```
      `test1000`ディレクトリのパスを記録する(サンプルアプリの書き換えに利用する) `pwd`等を用いる

- サンプルアプリ(01_vectorize.py)
  - 以下の環境変数を設定する。
    - OPENAI_URI
    - OPENAI_KEY
    - COSMOSDB_URI
    - COSMOSDB_KEY

  - main()ループのglob.globのディレクトリ名称(85行目の`'/home/xxxx/test1000/*.txt'`)を`test1000`ディレクトリのパスに変更する。
  - `python 01_vectorize.py`で実行する


### ベクトル検索の実行

- サンプルアプリ(02_search.py)
  - `python 02_search.py`で実行する
  - 検索したいテキストを入力する


