"""
小红书平台适配器
支持笔记发布和图文内容
"""
import json
import sys
from typing import List, Optional


class XHSAdapter:
    """
    小红书开放平台适配器
    
    支持图文笔记发布、话题标签、内容管理
    """
    
    def __init__(self, access_token: str = None):
        """
        初始化小红书适配器
        
        Args:
            access_token: 小红书访问令牌
        """
        self.access_token = access_token
    
    def post_note(self, content: dict, images: List[str]) -> str:
        """
        发布小红书笔记
        
        Args:
            content: 内容字典，包含title和body
            images: 图片路径列表
        
        Returns:
            笔记ID
        """
        title = content.get("title", "")
        body = content.get("body", "")
        
        # 参数校验
        if not title and not body:
            raise ValueError("Either title or body must be provided")
        if title and len(title) > 20:
            raise ValueError("Title must not exceed 20 characters")
        if len(body) > 1000:
            raise ValueError("Body must not exceed 1000 characters")
        if len(images) < 1 or len(images) > 18:
            raise ValueError("Images count must be between 1 and 18")
        
        # 模拟API调用返回笔记ID
        return "xhs_note_123"
    
    def delete_note(self, note_id: str) -> bool:
        """
        删除笔记
        
        Args:
            note_id: 笔记ID
        
        Returns:
            是否删除成功
        """
        return True
    
    def get_note_status(self, note_id: str) -> dict:
        """
        查询笔记状态
        
        Args:
            note_id: 笔记ID
        
        Returns:
            笔记状态信息
        """
        return {
            "note_id": note_id,
            "status": "published",
            "views": 500,
            "likes": 50,
            "collects": 20
        }


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing input file"}, ensure_ascii=False))
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(json.dumps({"error": f"Failed to read input: {str(e)}"}, ensure_ascii=False))
        sys.exit(1)
    
    action = data.get("action")
    adapter = XHSAdapter()
    
    if action == "post_note":
        result = {
            "note_id": adapter.post_note(
                content=data.get("content", {}),
                images=data.get("images", [])
            )
        }
    elif action == "delete_note":
        result = {"deleted": adapter.delete_note(data.get("note_id", ""))}
    elif action == "get_note_status":
        result = adapter.get_note_status(data.get("note_id", ""))
    else:
        result = {"error": f"Unknown action: {action}"}
    
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
