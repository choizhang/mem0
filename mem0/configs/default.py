import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# 加载环境变量
load_dotenv()

# 默认配置
default_config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "Qwen/Qwen2.5-7B-Instruct",
            "temperature": 0.2,
            "max_tokens": 2000
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "netease-youdao/bce-embedding-base_v1",
            "embedding_dims": 768
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "url": os.environ.get("QDRANT_URL"),
            "api_key": os.environ.get("QDRANT_API_KEY"),
            "collection_name": "mem0",  # 自定义集合名称
            "on_disk": True,  # 启用持久化存储
            "embedding_model_dims": 768  # Embedding 模型的维度
        }
    }
}

# 给新的collection创建索引index
# client = QdrantClient(url=os.environ.get("QDRANT_URL"), api_key=os.environ.get("QDRANT_API_KEY"))
# client.create_payload_index(
#     collection_name="healthcare_memories",
#     field_name="user_id",
#     field_schema="keyword",
# )

def get_config():
    """获取默认配置
    
    Returns:
        dict: 配置字典
    """
    return default_config