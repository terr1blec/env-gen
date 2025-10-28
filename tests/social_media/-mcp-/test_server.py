"""
简单测试脚本来验证小红书 MCP 服务功能
"""

import sys
import os

# 添加路径以便导入
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'social_media', '-mcp-'))

# 导入服务器模块
exec(open('../../../../generated/social_media/-mcp-/_mcp__server.py').read())

# 测试服务器功能
print("=== 小红书 MCP 服务测试 ===\n")

# 创建服务器实例
server = SocialMediaMCPServer()

print("1. 测试认证检查:")
auth_result = server.check_cookie()
print(f"   认证状态: {auth_result['authenticated']}")
print(f"   消息: {auth_result['message']}")

print("\n2. 测试笔记搜索:")
search_result = server.search_notes("technology")
print(f"   找到 {search_result['count']} 条笔记")
for note in search_result['notes']:
    print(f"   - {note['title']}")

print("\n3. 测试获取笔记内容:")
if search_result['count'] > 0:
    note = search_result['notes'][0]
    content_result = server.get_note_content(note['note_id'], note['xsec_token'])
    if content_result['found']:
        print(f"   成功获取笔记: {content_result['note']['title']}")
        print(f"   作者: {content_result['user']['nickname']}")
    else:
        print(f"   获取笔记失败: {content_result['message']}")

print("\n4. 测试获取评论:")
if search_result['count'] > 0:
    note = search_result['notes'][0]
    comments_result = server.get_note_comments(note['note_id'], note['xsec_token'])
    print(f"   找到 {comments_result['count']} 条评论")
    for comment in comments_result['comments']:
        print(f"   - {comment['user']['nickname']}: {comment['content']}")

print("\n5. 测试发布评论:")
if search_result['count'] > 0:
    note = search_result['notes'][0]
    post_result = server.post_comment(note['note_id'], "这是一个测试评论！")
    print(f"   发布结果: {post_result['success']}")
    print(f"   评论ID: {post_result.get('comment_id', 'N/A')}")
    print(f"   消息: {post_result['message']}")

print("\n=== 测试完成 ===")