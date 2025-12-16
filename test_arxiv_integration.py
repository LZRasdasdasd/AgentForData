#!/usr/bin/env python3
"""测试arXiv搜索功能集成"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs', 'deepagents-cli'))

def test_arxiv_search():
    """测试arXiv搜索功能"""
    print("正在测试arXiv搜索功能集成...")
    
    try:
        from deepagents_cli.tools import arxiv_search
        
        # 测试搜索"Attention is all you need"
        print("\n搜索 'Attention is all you need'...")
        result = arxiv_search("Attention is all you need", max_papers=2)
        
        if result.get('success'):
            print(f"✅ 搜索成功！找到 {result.get('total_found', 0)} 篇论文")
            
            for i, paper in enumerate(result.get('papers', []), 1):
                print(f"\n{i}. {paper['title']}")
                print(f"   作者: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
                print(f"   arXiv ID: {paper['arxiv_id']}")
                print(f"   链接: {paper['url']}")
                print(f"   摘要: {paper['summary'][:100]}...")
        else:
            print(f"❌ 搜索失败: {result.get('error')}")
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装arxiv包: pip install arxiv")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_tools_import():
    """测试工具导入"""
    print("\n测试工具模块导入...")
    
    try:
        from deepagents_cli.tools import arxiv_search, web_search, fetch_url, http_request
        print("✅ 所有工具导入成功")
        
        # 检查arxiv_search函数
        if callable(arxiv_search):
            print("✅ arxiv_search 函数可用")
        else:
            print("❌ arxiv_search 不是可调用函数")
            
    except ImportError as e:
        print(f"❌ 工具导入失败: {e}")

if __name__ == "__main__":
    test_tools_import()
    test_arxiv_search()
    print("\n测试完成！")