import asyncio  # 导入 asyncio 库用于异步编程
import os  # 导入 os 模块, 用于处理文件路径
import random  # 导入 random 模块, 用于生成随机延时
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient  # 导入 Telethon 客户端核心类
from telethon.errors import FloodWaitError, RPCError  # 导入 Telethon 的错误类型

import app_config  # 导入你的本地配置文件 (包含 API_ID, API_HASH, SESSION_OLD)
import send_msg_config  # 导入你的本地配置文件


# ===========================================

async def main():
    # 检查配置文件中是否存在 TASKS 列表, 如果不存在则抛出错误
    if not hasattr(send_msg_config, 'TASKS'):  # 检查配置属性是否存在
        print("❌ 错误: send_msg_config.py 中未找到 'TASKS' 列表配置")  # 打印错误提示
        return  # 退出程序

    # 获取当前脚本绝对路径, 确保 crontab 等环境能找到 session 文件
    base_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件目录
    session_path = os.path.join(base_path, app_config.SESSION_OLD)  # 拼接 Session 完整路径

    # 初始化客户端实例
    client = TelegramClient(session_path, app_config.API_ID, app_config.API_HASH)

    print(f"🚀 正在启动账号 ({app_config.SESSION_OLD})...")  # 打印启动提示

    # 使用 async with 自动管理连接和登录状态
    async with client:
        me = await client.get_me()  # 获取当前登录用户的信息
        print(f"✅ 登录成功: {me.first_name}")  # 确认登录成功

        tasks = send_msg_config.TASKS  # 读取任务列表
        total_tasks = len(tasks)  # 获取任务总数
        print(f"📋 共有 {total_tasks} 个待发送任务")  # 打印任务概况
        # 开始循环处理每个任务
        for index, item in enumerate(tasks):
            target = item.get('target')  # 获取目标 (用户名或ID)
            msg = item.get('message')  # 获取对应的消息内容

            try:
                # 1. 获取目标实体 (机器人)
                # 这一步是为了确保我们能找到该机器人,如果对话列表中没有,会自动尝试搜索
                entity = await client.get_entity(target)  # 获取机器人对象

                # 创建一个 UTC+8 的时区对象
                china_tz = timezone(timedelta(hours=8))
                # 获取当前时间并应用该时区
                cn_now = datetime.now(china_tz)
                # 格式化时间字符串
                current_time = cn_now.strftime('%H:%M:%S')

                # 2. 发送消息
                print(
                    f"📤 [{index + 1}/{total_tasks}] 北京时间 [{current_time}] 正在向 {target} 发送消息: {msg}")  # 打印进度日志
                await client.send_message(entity, msg)  # 执行发送操作
                print(f"✅ 发送完成!")  # 打印成功提示

                # 3. 随机延时 (风控保护)
                # 如果不是最后一条消息, 则进行延时, 避免触发 Telegram 刷屏风控
                if index < total_tasks - 1:
                    sleep_time = random.uniform(2, 5)  # 生成 2 到 5 秒之间的随机浮点数
                    print(f"   ⏳ 等待 {sleep_time:.2f} 秒以避免风控...")  # 打印等待日志
                    await asyncio.sleep(sleep_time)  # 执行异步等待

            except FloodWaitError as e:
                # 触发 Telegram 严重限流保护
                print(f"⚠️ 触发严重速率限制 (FloodWait), 必须等待 {e.seconds} 秒")  # 打印警告
                await asyncio.sleep(e.seconds)  # 强制脚本等待指定时间, 不要跳过

            except ValueError:
                # 通常是因为找不到该用户 (用户名错误或未曾交互过)
                print(f"❌ 无法找到目标用户: {target} (请检查用户名或隐私设置)")  # 打印无效用户错误

            except RPCError as e:
                # 捕获 Telegram API 返回的其他具体错误 (如被屏蔽、权限不足)
                print(f"❌ API 错误 ({target}): {e}")  # 打印 API 错误详情

            except Exception as e:
                # 捕获 Python 层面的其他未知错误
                print(f"❌ 未知错误 ({target}): {type(e).__name__}: {e}")  # 打印通用错误

    # 循环结束, async with 自动断开连接
    print("🏁 所有任务处理完毕")  # 打印结束日志


if __name__ == '__main__':
    asyncio.run(main())  # 运行主异步函数
