# 小红书 MCP 服务使用说明

## 概述

小红书 MCP 服务是一个模拟小红书（Little Red Book）社交媒体平台的 FastMCP 服务器模块。它提供了笔记搜索、内容获取、评论管理和认证检查等功能，完全基于本地离线数据库运行。

## 工具列表

### 1. check_cookie
**功能**: 检查用户认证状态
**输入**: 无
**输出**: 
- `authenticated`: 布尔值，表示认证状态
- `message`: 认证检查结果消息

**示例**:
```python
result = server.check_cookie()
# 输出: {"authenticated": true, "message": "Authentication check completed"}
```

### 2. search_notes
**功能**: 根据关键词搜索笔记
**输入**: 
- `keywords`: 搜索关键词（字符串，多个关键词用空格分隔）

**输出**:
- `notes`: 匹配的笔记列表
- `count`: 匹配的笔记数量
- `search_terms`: 实际使用的搜索关键词列表
- `message`: 搜索结果消息

**示例**:
```python
result = server.search_notes("technology art")
# 输出包含所有包含"technology"或"art"关键词的笔记
```

### 3. get_note_content
**功能**: 获取笔记详细内容
**输入**:
- `note_id`: 笔记的唯一标识符
- `xsec_token`: 认证令牌

**输出**:
- `note`: 笔记的完整信息
- `user`: 笔记作者的用户信息
- `found`: 是否成功找到笔记
- `message`: 操作结果消息

**示例**:
```python
result = server.get_note_content("note_8f3e7a2c", "xsec_user_8f3e7a2c_a1b2c3")
# 输出包含笔记内容和作者信息
```

### 4. get_note_comments
**功能**: 获取笔记的所有评论
**输入**:
- `note_id`: 笔记的唯一标识符
- `xsec_token`: 认证令牌

**输出**:
- `comments`: 笔记的评论列表
- `count`: 评论数量
- `found`: 是否成功找到笔记
- `message`: 操作结果消息

**示例**:
```python
result = server.get_note_comments("note_8f3e7a2c", "xsec_user_8f3e7a2c_a1b2c3")
# 输出包含所有评论及其作者信息
```

### 5. post_comment
**功能**: 在笔记下发布新评论
**输入**:
- `note_id`: 笔记的唯一标识符
- `comment`: 要发布的评论内容

**输出**:
- `success`: 评论发布是否成功
- `comment_id`: 新评论的唯一标识符
- `message`: 操作结果消息

**示例**:
```python
result = server.post_comment("note_8f3e7a2c", "这个笔记很有帮助！")
# 输出包含发布结果和新评论ID
```

## 数据库结构

服务依赖于本地 JSON 数据库，结构遵循 DATA CONTRACT：

```json
{
  "users": [
    {
      "user_id": "string",
      "username": "string", 
      "nickname": "string",
      "avatar": "string",
      "followers_count": "integer",
      "following_count": "integer",
      "notes_count": "integer"
    }
  ],
  "notes": [
    {
      "note_id": "string",
      "xsec_token": "string",
      "user_id": "string",
      "title": "string",
      "content": "string",
      "keywords": ["string"],
      "likes_count": "integer",
      "comments_count": "integer",
      "shares_count": "integer",
      "created_at": "string",
      "updated_at": "string"
    }
  ],
  "comments": [
    {
      "comment_id": "string",
      "note_id": "string",
      "user_id": "string",
      "content": "string",
      "created_at": "string",
      "likes_count": "integer"
    }
  ]
}
```

## 错误处理

- **数据库加载失败**: 使用默认空结构
- **笔记不存在**: 返回 `found: false` 和相应错误消息
- **认证令牌无效**: 拒绝访问并返回错误消息
- **评论内容为空**: 拒绝发布并返回错误消息

## 集成方式

### FastMCP 集成
```python
from generated.social_media.-mcp-._mcp__server import create_mcp_tools

tools = create_mcp_tools()
# tools 包含所有5个工具函数
```

### 直接使用
```python
from generated.social_media.-mcp-._mcp__server import SocialMediaMCPServer

server = SocialMediaMCPServer()
result = server.search_notes("technology")
```

## 测试

运行测试脚本验证功能：
```bash
cd tests/social_media/-mcp-
python test_server.py
```

## 注意事项

1. 服务完全基于本地数据库，不涉及真实的小红书 API
2. 所有数据关系（用户-笔记-评论）在数据库中维护
3. 时间戳使用 ISO 8601 格式
4. 搜索功能支持部分匹配
5. 认证基于简单的 xsec_token 验证