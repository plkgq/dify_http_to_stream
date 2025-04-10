import json
import requests
from typing import Mapping
from werkzeug import Request, Response
from dify_plugin import Endpoint

class Search(Endpoint):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        # 从 settings 中获取 api_url
        api_url = settings.get("api_url")
        
        # 获取 JSON 请求体
        payload = values.get("payload", {})
        
        # 确保 api_url 存在
        if not api_url:
            return Response(json.dumps({"error": "API URL is not set."}), status=400, content_type="application/json")

        try:
            # 向指定 API 发送请求（流式）
            with requests.post(api_url, json=payload, stream=True) as response:
                # 检查响应状态
                response.raise_for_status()  # 抛出异常，如果状态码是 4xx 或 5xx

                def generate_response():
                    # 流式读取内容
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # 确保 chunk 不为空
                            yield chunk  # 按块返回内容

                return Response(generate_response(), status=response.status_code, content_type=response.headers.get("Content-Type", "application/json"))

        except requests.exceptions.RequestException as e:
            # 捕获请求异常
            return Response(json.dumps({"error": str(e)}), status=500, content_type="application/json")
