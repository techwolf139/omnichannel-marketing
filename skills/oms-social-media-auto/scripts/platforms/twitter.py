"""
Twitter平台适配器
支持推文发布和多媒体内容
"""
import json
import sys
from typing import List, Optional


class TwitterAdapter:
    """
    Twitter API适配器
    
    支持推文发布、媒体上传、线程创建
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None, access_token: str = None):
        """
        初始化Twitter适配器
        
        Args:
            api_key: Twitter API Key
            api_secret: Twitter API Secret
            access_token: Twitter Access Token
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
    
    def tweet(self, content: str, media: List[str]) -> str:
        """
        发布推文
        
        Args:
            content: 推文内容
            media: 媒体文件路径列表
        
        Returns:
            推文ID
        """
        # 参数校验
        if not content:
            raise ValueError("Content cannot be empty")
        if len(content) > 4000:
            raise ValueError("Content must not exceed 4000 characters (Twitter Blue)")
        if len(media) > 4:
            raise ValueError("Cannot upload more than 4 media items")
        
        # 模拟API调用返回推文ID
        return "twitter_123"
    
    def delete_tweet(self, tweet_id: str) -> bool:
        """
        删除推文
        
        Args:
            tweet_id: 推文ID
        
        Returns:
            是否删除成功
        """
        return True
    
    def get_tweet_status(self, tweet_id: str) -> dict:
        """
        查询推文状态
        
        Args:
            tweet_id: 推文ID
        
        Returns:
            推文状态信息
        """
        return {
            "tweet_id": tweet_id,
            "status": "published",
            "views": 2000,
            "likes": 150,
            "retweets": 30
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
    adapter = TwitterAdapter()
    
    if action == "tweet":
        result = {
            "tweet_id": adapter.tweet(
                content=data.get("content", ""),
                media=data.get("media", [])
            )
        }
    elif action == "delete_tweet":
        result = {"deleted": adapter.delete_tweet(data.get("tweet_id", ""))}
    elif action == "get_tweet_status":
        result = adapter.get_tweet_status(data.get("tweet_id", ""))
    else:
        result = {"error": f"Unknown action: {action}"}
    
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
