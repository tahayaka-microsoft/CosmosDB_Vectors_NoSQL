import os
import asyncio
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
from openai import AzureOpenAI

# Azure OpenAIの設定
openai_key = os.environ['OPENAI_KEY']  # あなたのOpenAI APIキーに置き換えてください
openai_endpoint = os.environ['OPENAI_URI']  # あなたのOpenAIエンドポイントに置き換えてください
openai_client = AzureOpenAI(
    azure_endpoint=openai_endpoint,
    api_version='2023-12-01-preview',
    api_key=openai_key
)

# Azure Cosmos DBの設定
cosmos_account_uri = os.environ['COSMOSDB_URI']  # あなたのCosmos DB URIに置き換えてください
cosmos_account_key = os.environ['COSMOSDB_KEY']  # あなたのCosmos DBキーに置き換えてください
database_name = 'db1'
container_name = 'coll_holtest'
cosmos_client = CosmosClient(cosmos_account_uri, cosmos_account_key)

async def main():
    # データベースとコンテナの初期化
    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    # コンソールからテキスト入力
    text_input = input("Enter text to search: ")

    # テキストをベクトルに変換
    vector = openai_client.embeddings.create(input=text_input, model='text-embedding-ada-002').data[0].embedding

    # ベクトルを使用してCosmos DBを検索
    query = """
    SELECT TOP 2 c.id, c.name, c.num, 
    VectorDistance(c.vectors, @vector) AS similarity,
    c.text
    FROM c
    ORDER BY VectorDistance(c.vectors, @vector)
    """

    # クエリパラメータ
    parameters = [
        {"name": "@vector", "value": vector}
    ]

    # クエリを実行
    results = container.query_items(
        query=query,
        parameters=parameters,
    )

    # 結果を表示
    async for item in results:
        print(item)

    # Cosmos クライアントを閉じる
    await cosmos_client.close()

if __name__ == '__main__':
    asyncio.run(main())
