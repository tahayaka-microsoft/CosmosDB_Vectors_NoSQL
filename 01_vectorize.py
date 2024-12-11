import os
import glob
import time

import asyncio
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
from openai import AzureOpenAI

from langchain.text_splitter import RecursiveCharacterTextSplitter

# Azure Cosmos DB 設定
cosmos_account_uri = os.environ['COSMOSDB_URI']  # Replace with your Cosmos DB URI
cosmos_account_key = os.environ['COSMOSDB_KEY']  # Replace with your Cosmos DB key
db_name = "db1"  # Set your database name
collection_name = "coll_holtest"  # Set your container name

# Azure OpenAI 設定
model_name = 'text-embedding-ada-002'  # Name of the model deployed in OpenAI Studio

# Azure OpenAI client 初期化
openai_client = AzureOpenAI(
    api_key=os.environ['OPENAI_KEY'],  # Replace with your OpenAI API key
    api_version="2023-12-01-preview",
    azure_endpoint=os.environ['OPENAI_URI']  # Replace with your OpenAI endpoint
)

# Cosmos DB client 初期化
cosmos_client = CosmosClient(cosmos_account_uri, cosmos_account_key)

# ファイルを読み込み、埋め込みを取得して Cosmos DB に保存する関数
async def store_embedding(cnt, filename, container):
    with open(filename, 'r', encoding='utf8') as data:
        text = data.read().replace('\n', '')

    splitter = RecursiveCharacterTextSplitter(chunk_size=5000)
    chunks = splitter.split_text(text)

    for num, chunk in enumerate(chunks):
        try:
            vectors = openai_client.embeddings.create(model=model_name, input=chunk).data[0].embedding
        except Exception as e:
            print(f"Error when calling embeddings.create():[{e}]")
            continue  # エラーがあっても次にいく

        document = {
            "id": f"{os.path.basename(filename)}-{num}",
            "name": filename,
            "num": num,
            "vectors": vectors,
            "text": chunk
        }

        await container.create_item(body=document)
        print(f"{cnt} : {filename} - Chunk[{num+1}/{len(chunks)}] Inserted ")

# メインループ
async def main():
    # データベース初期化
    database = cosmos_client.get_database_client(db_name)

    # コンテナーがある場合いったん削除
    try:
        await database.delete_container(container=collection_name)
        print(f"Container '{collection_name}' deleted.")
    except Exception as e:
        print(f"Container '{collection_name}' does not exist or could not be deleted: {e}")

    # Vector Index等を使用してインデックスポリシーを定義
    indexing_policy = {
        "indexingMode": "consistent",
        "automatic": True,
        "includedPaths": [
            {
                "path": "/*"
            }
        ],
        "excludedPaths": [
            {
                "path": "/\"_etag\"/?"
            }
        ],
        "vectorIndexes": [
            {
                "path": "/vectors",
                "type": "quantizedFlat"
            }
        ]
    }
    
    # ベクトル埋め込みポリシーを定義
    vector_embedding_policy = {
        "vectorEmbeddings": [
            {
                "path":"/vectors",
                "dataType":"float32",
                "distanceFunction":"cosine",
                "dimensions":1536
            }
        ]
    }

    # インデックスポリシーを指定してコンテナを作成
    container = await database.create_container(
        id=collection_name,
        partition_key=PartitionKey(path="/id"),
        indexing_policy=indexing_policy,
        vector_embedding_policy=vector_embedding_policy
    )
    print(f"Container '{collection_name}' created with DiskANN index.")

    # ファイルを処理して埋め込みを保存
    files = glob.glob('/home/xxxx/test1000/*.txt') # Set your /home path in the CloudShell
    files.sort()
    files = files[0:100]  # Only 100 files

    cnt = 0
    for file in files:
        cnt += 1
        await store_embedding(cnt, file, container)

    time.sleep(5)

    await cosmos_client.close()

if __name__ == '__main__':
    asyncio.run(main())
