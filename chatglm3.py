import requests
from tools import tools_mapping
import json
import requests
import json
from tools import tools_mapping


class ChatGLM3:
    def __init__(self):
        self.chat_history = []
        self.prompt = {
            "role": "system",
            "content": """
        角色清晰： 你是壹号旗舰店的一个电商客服,今年20岁,回复内容语句通顺、逻辑合理,亲切随和,每次回复必须完整并且精准回答用户问题, 如遇到api返回结果时完全按照下面定义好的格式返回。
        结构化交互： 当用户触发某个函数时，你需要捕获上一个函数的响应，并按照指定格式进行输出。
        明确指导： 请确保在触发函数后，正确捕获上一个函数的响应，并按照指定格式进行输出。
        前提条件：
        订单状态枚举值设定为：1为已下单，2为已发货，3为已取消，4为已完成。
        处理方式：
        遇到订单状态时，进行枚举转换。
        重要！！！api调用结果后的回复一定要按固定返回格式
        请不要透露你用什么方式获取的数据， 不要提及根据API返回的结果, 不要提及经过搜索商品API, 不要提及你是人工智能助理/助手。
        遇到时间时，格式化为年-月-日。
        今天日期是{date}
        如果遇到图片用html格式 image标签将其包装返回
        重要！！！回复如遇到api返回结果时完全按照下面部分定义好的格式返回。
        在收到api返回订单信息列表时候返回结果只选取一条最匹配用户描述的订单。
        用户意图咨询商品时候，必须调用search_product，不可乱回复商品，并将调用结果按照下面格式化输出,
        格式如下:
        商品名称：xx \n
        价格：xx \n
        商品信息：xx \n
        尺寸：xx \n
        商品图片：<img width="100%" height="200" src="xx地址"/> \n
        [购买链接](商品链接)\n
        每个属性需添加换行符。
        重要！！！function response 所有都需要按定义好的格式输出内容
        用户意图咨询订单时候，必须调用pick_order，不可乱回复订单，并将调用结果按照下面格式化输出,
        格式如下:
        订单商品信息：xx \n
        商品价格：xx \n
        运费价格：xx \n
        收货地址信息：xx \n
        订单状态：xx \n
        下单时间：xx \n
        每个属性需添加换行符。
        在收到search_product 即查询商品 api返回商品信息时候返回结果，每个属性需添加换行符 ，按下面示例格式化输出将xx替换为返回结果对应数据：
        商品名称：xx \n
        价格：xx \n
        商品信息：xx \n
        尺寸：xx \n
        商品图片：<img width="100%" height="200" src="xx地址"/>\n
        [购买链接](商品链接)\n
        在收到pick_order 即查询订单 api返回订单信息时返回结果，
        每个属性需添加换行符 按下面示例格式化输出将xx替换为返回结果对应数据：
        订单商品信息：xx \n
        商品价格：xx \n
        运费价格：xx \n
        收货地址信息：xx \n
        订单状态：xx \n
        下单时间：xx \n。
        """,
            "name": "string",
            "function_call": {},
        }
        self.functions = [
            {
                "name": "search_product",
                "description": """分析用户意图当想要购买商品、了解商品信息、推荐商品时候触发，例如：请介绍下商品名、 想了解下商品名、请说说商品名、我要买商品名、商品名、推荐个商品名""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"description": "用户输入的信息提取出的商品名称"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "pick_order",
                "description": "！！！分析用户意图当想要（查询/获取）订单信息时候触发，例如：请帮我看下昨天订单 想帮我查询某某的订单 请帮我看看某某订单发货了没, 看看我xx的订单",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "description": "用户输入内容提取出的订单查询条件信息"
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "cancel_order",
                "description": "分析用户意图当想要了取消订单时候触发，例如请帮我取消订单、取消订单、cancel",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"description": "提取上下文中最近一条内容的订单id"},
                    },
                    "required": ["query"],
                },
            },
        ]
        self.url = "http://192.168.31.125:8001/v1/chat/completions"
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }

    def call_api(self, data):
        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def chat(self, query):
        if not isinstance(query, str):
            raise ValueError("query must be a string")
        if not query:
            raise ValueError("query must not be empty")

        messages = [
            self.prompt,
            {
                "role": "user",
                "content": query,
                "name": "string",
                "function_call": {},
            },
        ]
        self.chat_history.append(messages[-1])

        data = {
            "model": "chatglm3-6b",
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 0,
            "stream": False,
            "functions": self.functions,
            "repetition_penalty": 1.1,
        }
        json_response = self.call_api(data)
        response_message = json_response["choices"][0]["message"]
        function_call = response_message["function_call"]
        if function_call is None:
            self.chat_history.append(response_message)
            return response_message["content"]

        function_response = tools_mapping.get(function_call["name"])(
            json.loads(function_call["arguments"])
        )
        self.chat_history.append(response_message)
        messages.append(response_message)
        messages.append(
            {
                "role": "function",
                "name": function_call["name"],
                "content": str(function_response),
            }
        )
        self.chat_history.append(messages[-1])
        function_data = {
            "model": "chatglm3-6b",
            "messages": messages,
            "temperature": 0.8,
            "top_p": 0.8,
            "max_tokens": 0,
            "stream": False,
            "functions": {},
            "repetition_penalty": 1.1,
        }
        final_response = self.call_api(function_data)
        self.chat_history.append(final_response["choices"][0]["message"])
        return final_response["choices"][0]["message"]["content"]


def main():
    chatglm3 = ChatGLM3()
    response = chatglm3.chat("Hello, world!")
    print(response)


if __name__ == "__main__":
    main()
