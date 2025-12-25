"""
测试MacBERT模型
"""
import sys
import os
from pathlib import Path

# 获取项目根目录（test目录的父目录）
project_root = Path(__file__).parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

def test_macbert_model():
    """测试MacBERT模型加载和实体抽取"""
    print("=" * 60)
    print("测试MacBERT模型")
    print("=" * 60)
    
    try:
        from src.macbert_model import MacBERTModel
        
        # 加载模型
        print("\n[步骤1] 加载MacBERT模型...")
        model_path = project_root / "model" / "chinese-macbert-base"
        model = MacBERTModel(str(model_path))
        print("[OK] 模型加载成功")
        
        # 测试实体抽取
        print("\n[步骤2] 测试实体抽取...")
        test_text = "1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。"
        test_schema = {
            "人物": None,
            "地理位置": None,
            "组织机构": None,
            "时间": None
        }
        
        print(f"测试文本: {test_text}")
        print(f"测试Schema: {test_schema}")
        
        result = model.extract_entities(test_text, test_schema)
        
        if 'error' in result:
            print(f"[ERROR] 实体抽取失败: {result['error']}")
            return False
        else:
            print(f"[OK] 实体抽取成功")
            print(f"抽取结果: {result.get('entities', {})}")
            
            # 格式化输出
            if 'entities' in result and 'output' in result['entities']:
                print("\n抽取到的实体:")
                for entity_group in result['entities']['output']:
                    for entity in entity_group:
                        print(f"  - {entity.get('type', '未知')}: {entity.get('span', '')} "
                              f"(位置: {entity.get('offset', [])})")
        
        print("\n" + "=" * 60)
        print("[OK] 所有测试通过！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_macbert_model()
    sys.exit(0 if success else 1)

