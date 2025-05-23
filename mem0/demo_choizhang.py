import os

from mem0 import Memory
from openai import OpenAI
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

from mem0.configs.default import get_config

# 获取默认配置
config = get_config()

# 初始化 OpenAI 客户端
# openai_client = OpenAI(
#     api_key = "sk-lindjyxdvjnzifhqobtczhkrmoceukojrllhiiqphiudhvmn",
#     base_url = "https://api.siliconflow.cn/v1"
# )
# messages = [
#     {"role": "system", "content": ""},
#     {"role": "user", "content": "你是谁"}
# ]
# # 使用 OpenAI 接口生成对话回复
# response = openai_client.chat.completions.create(
#     model="Qwen/Qwen2.5-7B-Instruct",
#     messages=messages
# )
# assistant_response = response.choices[0].message.content
# print(assistant_response)

# 给user_id创建索引index
# client = QdrantClient(url="https://1083ef4d-ff19-4ed8-94ab-cc6860acfcc0.us-east-1-0.aws.cloud.qdrant.io:6333", api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.3GUQj7xbvPF-JPm00YUFkNpK6_yCiHkep1KAi4prA1g")
# client.create_payload_index(
#     collection_name="mem0",
#     field_name="user_id",
#     field_schema="keyword",
# )

m = Memory.from_config(config)

# messages = [
#     {"role": "user", "content": "我叫张三，我喜欢打篮球。我有个朋友叫李四，他喜欢游泳"},
#     {"role": "assistant", "content": "有朋友可真令人羡慕呢"}
# ]
# m.add(messages, user_id="alice11", metadata={"category": "person"})

# memories = m.get_all(user_id="alice11", limit=50)
# print(memories)

query = "我朋友喜欢什么运动"
result = m.search(query, user_id="alice11")
# 只能进行了向量召回，要给到LLM才能回复好
print(result)