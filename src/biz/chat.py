import json
import re
from src.biz.prompt import PromptManager

class Chat:
    def __init__(self, client, instruction):
        self.client = client
        self.messages = [
            {
            "role": "system",
            "content": PromptManager().get_system_prompt(instruction)
            }
        ]

    def clean_history(self):
        new_messages = []
        user_msg_count = 0
        for message in reversed(self.messages):
            if message['role'] == 'user':
                user_msg_count = user_msg_count + 1
                if user_msg_count >= 4:
                    continue
            new_messages.insert(0, message)
        return new_messages

    def next_action(self, screehshot):
        self.messages = self.clean_history()
        self.messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{screehshot}"
                        }
                    }
                ]
            }
        )

        response = self.client.chat.completions.create(
            model="doubao-1-5-ui-tars-250428",
            temperature=0,
            messages=self.messages,
            top_p=0.7
        )
        parsed_output = json.loads(self.parse_action_output(response.choices[0].message.content))
        self.messages.append(
            {
                "role": "assistant",
                "content": response.choices[0].message.content
            }
        )
        return parsed_output

    def parse_action_output(self, output_text):
        # 提取Thought部分
        thought_match = re.search(r'Thought:(.*?)\nAction:', output_text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else ""

        # 提取Action部分
        action_match = re.search(r'Action:(.*?)(?:\n|$)', output_text, re.DOTALL)
        action_text = action_match.group(1).strip() if action_match else ""

        # 初始化结果字典
        result = {
            "thought": thought,
            "action": "",
            "key": None,
            "content": None,
            "start_box": None,
            "end_box": None,
            "direction": None,
            "action_text": action_text
        }

        if not action_text:
            return json.dumps(result, ensure_ascii=False)

        # 解析action类型
        action_parts = action_text.split('(')
        action_type = action_parts[0]
        result["action"] = action_type

        # 解析参数
        if len(action_parts) > 1:
            params_text = action_parts[1].rstrip(')')
            params = {}

            # 处理键值对参数
            for param in params_text.split(','):
                param = param.strip()
                if '=' in param:
                    key, value = param.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('\'"')

                    # 处理bbox格式
                    if 'box' in key:
                        # 提取坐标数字
                        numbers = re.findall(r'\d+', value)
                        if numbers:
                            coords = [int(num) for num in numbers]
                            if len(coords) == 4:
                                if key == 'start_box':
                                    result["start_box"] = coords
                                elif key == 'end_box':
                                    result["end_box"] = coords
                    elif key == 'key':
                        result["key"] = value
                    elif key == 'content':
                        # 处理转义字符
                        value = value.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
                        result["content"] = value
                    elif key == 'direction':
                        result["direction"] = value

        return json.dumps(result, ensure_ascii=False, indent=2)