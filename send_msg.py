import asyncio  # 导入 asyncio 库用于异步编程和延时等待
from datetime import datetime, timedelta  # 导入日期时间模块,用于计算下一次运行时间
from telethon import TelegramClient  # 导入 Telethon 客户端核心类
import app_config  # 导入你的本地配置文件 (包含 API_ID, API_HASH, SESSION_OLD)
import send_msg_config  # 导入你的本地配置文件


# ===========================================

async def main():
    # 初始化客户端实例,使用你配置文件中的 API ID 和 Hash
    client = TelegramClient(app_config.SESSION_OLD, app_config.API_ID, app_config.API_HASH)

    print(f"🚀 正在启动账号 ({app_config.SESSION_OLD})...")  # 打印启动提示

    # 使用 async with 自动管理连接和登录状态
    async with client:
        me = await client.get_me()  # 获取当前登录用户的信息
        print(f"✅ 登录成功: {me.first_name} (+{me.phone})")  # 确认登录成功

        try:
            # 1. 获取目标实体 (机器人)
            # 这一步是为了确保我们能找到该机器人,如果对话列表中没有,会自动尝试搜索
            entity = await client.get_entity(send_msg_config.TARGET_BOT_USERNAME)  # 获取机器人对象

            # 2. 发送签到消息
            print(
                f"📤 [{datetime.now().strftime('%H:%M:%S')}] 正在向 {send_msg_config.TARGET_BOT_USERNAME} 发送消息: {send_msg_config.MESSAGE}")  # 打印发送日志
            await client.send_message(entity, send_msg_config.MESSAGE)  # 执行发送操作
            print(f"✅ 发送完成!")  # 打印成功提示

        except Exception as e:
            # 捕获网络错误或其他异常,防止脚本崩溃停止
            print(f"❌ 发送失败,原因: {e}")  # 打印错误详情

# async with 块结束,自动断开连接


if __name__ == '__main__':
    # 注意：如果要长期运行,建议在服务器使用 nohup 或 screen/tmux 运行此脚本
    asyncio.run(main())  # 运行主异步函数
