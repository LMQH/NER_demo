"""
API测试脚本
用于测试NER Demo API接口
"""
import sys
import os
from pathlib import Path
import requests
import json
from typing import Dict, Any

# 获取项目根目录（test目录的父目录）
project_root = Path(__file__).parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:5000"


def test_health_check():
    """测试健康检查接口"""
    print("\n" + "=" * 60)
    print("测试健康检查接口")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {str(e)}")
        return False


def test_list_models():
    """测试获取模型列表接口"""
    print("\n" + "=" * 60)
    print("测试获取模型列表接口")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/models")
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {str(e)}")
        return False


def test_extract_entities(model: str = None):
    """测试实体抽取接口"""
    print("\n" + "=" * 60)
    print(f"测试实体抽取接口 (模型: {model or '默认'})")
    print("=" * 60)
    
    request_data = {
        "text": "1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。",
        "schema": {
            "人物": None,
            "地理位置": None,
            "组织机构": None
        }
    }
    
    if model:
        request_data["model"] = model
    
    try:
        print(f"请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
        response = requests.post(
            f"{BASE_URL}/api/extract",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"\n状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {str(e)}")
        return False


def test_switch_model(model: str):
    """测试切换模型接口"""
    print("\n" + "=" * 60)
    print(f"测试切换模型接口: {model}")
    print("=" * 60)
    
    request_data = {"model": model}
    
    try:
        print(f"请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
        response = requests.post(
            f"{BASE_URL}/api/model/switch",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"\n状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("NER Demo API 测试")
    print("=" * 60)
    print(f"API地址: {BASE_URL}")
    print("\n注意: 请确保API服务已启动 (python app.py)")
    
    results = []
    
    # 测试健康检查
    results.append(("健康检查", test_health_check()))
    
    # 测试获取模型列表
    results.append(("获取模型列表", test_list_models()))
    
    # 测试实体抽取（默认模型）
    results.append(("实体抽取-默认模型", test_extract_entities()))
    
    # 测试实体抽取（指定nlp_structbert模型）
    results.append(("实体抽取-nlp_structbert", test_extract_entities("nlp_structbert_siamese-uie_chinese-base")))
    
    # 测试实体抽取（指定chinese-macbert模型）
    results.append(("实体抽取-chinese-macbert", test_extract_entities("chinese-macbert-base")))
    
    # 测试切换模型
    results.append(("切换模型", test_switch_model("chinese-macbert-base")))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("=" * 60)
    if all_passed:
        print("所有测试通过！")
    else:
        print("部分测试失败，请检查API服务是否正常运行")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试中断")
    except Exception as e:
        print(f"\n\n测试出错: {str(e)}")
        import traceback
        traceback.print_exc()

