import requests
import json

url = "https://www.joinquant.com/algorithm/live/log"
params = {
    "backtestId": "c0d70622b43858da661ffa8261209e0b",
    "offset": "-1",
    "ajax": "1"
}

cookies = {
    "live_default_position_cols": "amount%2Cprice%2Cposition%2Cgain%2CgainPercent%2CdailyGainsPercent%2CpositionPersent",
    "token": "c8323c232db4ee2fada81dd80a37957b6ee0f177",
    "uid": "wKgyrWe+a6t8TgU9I7WaAg==",
    "getStrategy": "1",
    "from": "edit",
    "_xsrf": "2|ffc493a1|18404ccad881b1822f58a5db6c063ba1|1740763534",
    "newBacktest": "e0f45ee0101095f6e2f2350e87c47b93",
    "finishExtInfoce6985f6a07659d99d198c7c2a49a647": "1",
    "PHPSESSID": "idce09pgibnfspk1hrhmr9adk7"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
}

try:
    response = requests.get(url, params=params, cookies=cookies, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    # 尝试解析JSON响应
    try:
        data = response.json()
        print("\n解析后的JSON数据:")
        print(json.dumps(data, indent=4, ensure_ascii=False))
        
        # 将数据保存到文件
        with open("jq_log_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("\n数据已保存到 jq_log_data.json 文件")
    except json.JSONDecodeError:
        print("\n响应不是有效的JSON格式")
except Exception as e:
    print(f"发生错误: {e}") 