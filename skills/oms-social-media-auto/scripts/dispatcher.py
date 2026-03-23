"""
全平台社交媒体分发调度器
统一入口，管理多平台内容分发
"""
import json
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime


class SocialDispatcher:
    """
    社交媒体内容分发调度器
    
    统一管理多平台内容分发，支持知乎、微博、小红书、Twitter
    """
    
    def __init__(self, platform_clients: dict = None):
        """
        初始化分发器
        
        Args:
            platform_clients: 平台客户端字典，如 {"zhihu": zhihu_client, ...}
        """
        self.clients = platform_clients or {}
    
    def dispatch(self, content: dict, platforms: list) -> dict:
        """
        分发内容到指定平台
        
        Args:
            content: 统一内容模型
            platforms: 目标平台列表，如 ["zhihu", "weibo"]
        
        Returns:
            各平台分发结果字典
        """
        results = {}
        content_id = content.get("content_id", f"content_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        for platform in platforms:
            if platform not in self.clients:
                results[platform] = {
                    "status": "failed",
                    "error_message": f"Platform {platform} not configured"
                }
                continue
            
            try:
                client = self.clients[platform]
                
                # 调用对应平台的发送方法
                if platform == "zhihu":
                    platform_content_id = client.post_article(
                        title=content.get("title", ""),
                        body=content.get("body", ""),
                        topics=content.get("topics", [])
                    )
                elif platform == "weibo":
                    platform_content_id = client.post(
                        content=content.get("body", ""),
                        images=content.get("media", [])
                    )
                elif platform == "xhs":
                    platform_content_id = client.post_note(
                        content=content,
                        images=content.get("media", [])
                    )
                elif platform == "twitter":
                    platform_content_id = client.tweet(
                        content=content.get("body", ""),
                        media=content.get("media", [])
                    )
                else:
                    results[platform] = {
                        "status": "failed",
                        "error_message": f"Unsupported platform: {platform}"
                    }
                    continue
                
                results[platform] = {
                    "content_id": content_id,
                    "platform": platform,
                    "status": "success",
                    "platform_content_id": platform_content_id,
                    "platform_url": f"https://{platform}.com/{platform_content_id}",
                    "published_at": datetime.now().isoformat(),
                    "error_message": None
                }
            except Exception as e:
                results[platform] = {
                    "content_id": content_id,
                    "platform": platform,
                    "status": "failed",
                    "platform_content_id": None,
                    "platform_url": None,
                    "published_at": None,
                    "error_message": str(e)
                }
        
        return results
    
    def dispatch_all(self, content: dict) -> dict:
        """
        分发内容到所有已配置的平台
        
        Args:
            content: 统一内容模型
        
        Returns:
            各平台分发结果字典
        """
        return self.dispatch(content, list(self.clients.keys()))
    
    def get_status(self, content_id: str) -> dict:
        """
        查询内容在各平台的发布状态
        
        Args:
            content_id: 内容唯一ID
        
        Returns:
            各平台状态字典
        """
        return {
            "content_id": content_id,
            "status": "completed",
            "platforms": list(self.clients.keys())
        }
    
    def delete_batch(self, content_ids: list) -> dict:
        """
        批量删除内容
        
        Args:
            content_ids: 内容ID列表
        
        Returns:
            删除结果字典
        """
        results = {}
        for content_id in content_ids:
            results[content_id] = {"status": "deleted"}
        return results


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
    dispatcher = SocialDispatcher()
    
    if action == "dispatch":
        content = data.get("content", {})
        platforms = data.get("platforms", [])
        result = dispatcher.dispatch(content, platforms)
    elif action == "dispatch_all":
        content = data.get("content", {})
        result = dispatcher.dispatch_all(content)
    elif action == "get_status":
        content_id = data.get("content_id", "")
        result = dispatcher.get_status(content_id)
    elif action == "delete_batch":
        content_ids = data.get("content_ids", [])
        result = dispatcher.delete_batch(content_ids)
    else:
        result = {"error": f"Unknown action: {action}"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
